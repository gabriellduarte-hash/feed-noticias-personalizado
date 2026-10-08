"""
Cataloga novas fontes pro "Seguir fontes" do hub.

O catálogo é um mapa: as fontes catalogadas aqui NÃO são coletadas de
hora em hora (feed_catalog.vitrine = false, sql/031). Só entram na coleta
quando alguém segue a fonte (aí vira uma fonte normal, em sources).

Fluxo:
  1. Lê catalogo/candidatos.txt (categoria + URL de um site ou de um feed,
     e opcionalmente nome, região e idioma).
  2. Pra cada candidato, descobre o feed RSS/Atom:
       - a própria URL já é um feed? usa ela;
       - senão, procura <link rel="alternate" type="application/rss+xml"> no HTML;
       - senão, tenta caminhos comuns (/feed, /rss, /rss.xml...).
  3. Valida o feed de verdade (feedparser): tem entradas, títulos, e
     publicou algo recentemente.
     Sem RSS (ou com o site bloqueando robôs), tenta ainda:
       - o sitemap de notícias do site (o XML que ele publica pro Google Notícias);
       - o RSS de busca do Google Notícias restrito ao site.
     (ver coletor/alternativas.py)
  4. Gera um arquivo sql/0NN_catalogo_AAAA-MM-DD.sql com os INSERTs —
     não grava nada no banco. Você revisa o arquivo e roda no SQL Editor.

Uso (da raiz do projeto, com o .venv ativo):
    python catalogo/catalogar.py
    python catalogo/catalogar.py --candidatos catalogo/veiculos-en.txt --idioma en --rotulo ingles
"""
import argparse
import html
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse

import feedparser
import requests

# Mesmo User-Agent do coletor: se um site bloquear aqui, vai bloquear lá
# também, então é melhor descobrir agora do que depois de catalogado.
USER_AGENT = "DailyPaperBot/0.1 (uso pessoal - estudo)"
TIMEOUT_SEGUNDOS = 15
# Sites diferentes em paralelo (são centenas; um de cada vez levava horas).
# Cada site ainda é visitado por uma conexão só, sem pressa.
SITES_EM_PARALELO = 8
MIN_ENTRADAS = 3
MAX_DIAS_SEM_PUBLICAR = 45

# A lista fixa de resumo/resumir.py e do check constraint de articles.category,
# mais três só do catálogo, pra organizar a descoberta: "Notícias" (veículos
# de notícia geral), "Meio ambiente" e "Automóveis". A categoria de cada
# notícia continua vindo da IA. Mesma lista em hub/src/lib/feed.ts.
CATEGORIAS = [
    "Notícias", "Política", "Finanças", "Tecnologia", "Ciência", "Meio ambiente",
    "Saúde", "Esportes", "Entretenimento", "Automóveis", "Mundo", "Humor", "Outros",
]
IDIOMAS = ("pt", "en")

CAMINHOS_COMUNS = ["/feed", "/feed/", "/rss", "/rss/", "/rss.xml", "/feed.xml", "/atom.xml", "/index.xml"]
TIPOS_FEED = ("application/rss+xml", "application/atom+xml", "application/feed+json", "application/xml", "text/xml")

RAIZ = Path(__file__).resolve().parent.parent

# Reaproveita os módulos do coletor (leitura de sitemap/Google Notícias e o db.py)
sys.path.insert(0, str(RAIZ / "coletor"))
from alternativas import entradas_do_site, ler_sitemap, sitemaps_do_robots, url_google_news  # noqa: E402


class Candidato:
    def __init__(self, categoria, url, nome=None, linha=0, regiao=None, idioma="pt"):
        self.categoria = categoria
        self.url = url
        self.nome = nome
        self.linha = linha
        self.regiao = regiao   # "Minas Gerais", "EUA"... (pra busca achar por lugar)
        self.idioma = idioma


class Resultado:
    def __init__(
        self, candidato, feed_url=None, nome=None, descricao=None, entradas=0, ultima=None, erro=None, via="rss"
    ):
        self.candidato = candidato
        self.via = via  # "rss", "sitemap" ou "google_news"
        self.feed_url = feed_url
        self.nome = nome
        self.descricao = descricao
        self.entradas = entradas
        self.ultima = ultima
        self.erro = erro


class _CabecalhoHtml(HTMLParser):
    """Lê do HTML os <link rel="alternate" ...rss...> e o nome do site
    (og:site_name, ou o <title> como último recurso)."""

    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.nome_site = None
        self.titulo = ""
        self._no_title = False

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "link":
            rels = a.get("rel", "").lower().split()
            if "alternate" in rels and a.get("type", "").lower() in TIPOS_FEED and a.get("href"):
                self.hrefs.append(a["href"])
        elif tag == "meta" and a.get("property", "").lower() == "og:site_name" and a.get("content"):
            self.nome_site = self.nome_site or a["content"]
        elif tag == "title" and not self.titulo:
            self._no_title = True

    def handle_data(self, data):
        if self._no_title:
            self.titulo += data

    def handle_endtag(self, tag):
        if tag == "title":
            self._no_title = False


def ler_candidatos(caminho, idioma_padrao="pt"):
    """Formato: uma linha por site, "Categoria | URL", e opcionalmente
    "| Nome | Região | Idioma" (vazio = sem). Linhas vazias e começando
    com # são ignoradas."""
    candidatos, erros = [], []
    for n, bruta in enumerate(caminho.read_text(encoding="utf-8").splitlines(), start=1):
        linha = bruta.strip()
        if not linha or linha.startswith("#"):
            continue
        partes = [p.strip() for p in linha.split("|")]
        if len(partes) < 2:
            erros.append(f"linha {n}: esperado 'Categoria | URL' -> {linha!r}")
            continue
        categoria, url = partes[0], partes[1]
        if categoria not in CATEGORIAS:
            erros.append(f"linha {n}: categoria {categoria!r} não está na lista fixa ({', '.join(CATEGORIAS)})")
            continue
        if not url.startswith(("http://", "https://")):
            erros.append(f"linha {n}: URL precisa começar com http:// ou https:// -> {url!r}")
            continue
        campo = lambda i: partes[i] if len(partes) > i and partes[i] else None  # noqa: E731
        idioma = campo(4) or idioma_padrao
        if idioma not in IDIOMAS:
            erros.append(f"linha {n}: idioma {idioma!r} não é um de {IDIOMAS}")
            continue
        candidatos.append(Candidato(categoria, url, campo(2), n, regiao=campo(3), idioma=idioma))
    return candidatos, erros


def baixar(sessao, url):
    resposta = sessao.get(url, timeout=TIMEOUT_SEGUNDOS, allow_redirects=True)
    resposta.raise_for_status()
    return resposta


def parece_feed(resposta):
    tipo = resposta.headers.get("content-type", "").lower()
    inicio = resposta.content[:500].lstrip().lower()
    return any(t in tipo for t in ("rss", "atom", "xml")) or inicio.startswith((b"<?xml", b"<rss", b"<feed"))


def descobrir_feeds(sessao, url):
    """Devolve (URLs candidatas a feed na ordem de teste, nome do site no HTML)."""
    resposta = baixar(sessao, url)
    if parece_feed(resposta):
        return [resposta.url], None

    parser = _CabecalhoHtml()
    parser.feed(resposta.text)
    encontrados = [urljoin(resposta.url, href) for href in parser.hrefs]

    base = f"{urlparse(resposta.url).scheme}://{urlparse(resposta.url).netloc}"
    comuns = [base + caminho for caminho in CAMINHOS_COMUNS]
    # Título da página costuma ser "Nome do Site - slogan": fica só a 1ª parte
    nome_site = parser.nome_site or re.split(r"\s[|\-–—:]\s", parser.titulo.strip())[0] or None
    # sem repetir, mantendo a ordem (os declarados no HTML primeiro)
    return list(dict.fromkeys(encontrados + comuns)), nome_site


def rotulo_do_dominio(url):
    """'https://www.tecmundo.com.br/x' -> 'tecmundo'."""
    partes = urlparse(url).netloc.lower().removeprefix("www.").split(".")
    return partes[0] if partes else ""


def escolher_nome(candidato, titulo_feed, nome_site):
    """O título do feed nem sempre é o nome do site: feeds hospedados por
    um grupo vêm com o nome do grupo ("Estadão | ..." pro TecMundo), e
    alguns vêm só com o domínio ("www.espn.com.br -"). Nesses casos, o
    nome declarado no próprio site é mais confiável."""
    if candidato.nome:
        return candidato.nome
    titulo = limpar(titulo_feed, 80).strip(" -|–—")
    rotulo = rotulo_do_dominio(candidato.url)
    parece_dominio = bool(re.search(r"\.(com|net|org|br)\b", titulo.lower()))
    if titulo and not parece_dominio and rotulo in normalizar(titulo).replace(" ", ""):
        return titulo
    site = limpar(nome_site, 80)
    if site and rotulo in normalizar(site).replace(" ", ""):
        return site
    # Nem o feed nem a página citam o domínio pedido (ex.: o site redireciona
    # pro portal do grupo): o próprio domínio é o nome menos errado. Vale
    # passar o nome certo no candidatos.txt nesses casos.
    return rotulo.capitalize() if rotulo else (site or titulo)


def normalizar(texto):
    import unicodedata

    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")


def descrever_erro(e):
    """'HTTP 403' (bloqueou o robô), 'HTTP 404' (não existe), ou o tipo do erro."""
    status = getattr(getattr(e, "response", None), "status_code", None)
    return f"HTTP {status}" if status else type(e).__name__


def data_da_entrada(entrada):
    for campo in ("published_parsed", "updated_parsed"):
        valor = entrada.get(campo)
        if valor:
            return datetime(*valor[:6], tzinfo=timezone.utc)
    return None


def limpar(texto, limite=None):
    texto = html.unescape(re.sub(r"<[^>]+>", " ", texto or ""))
    texto = re.sub(r"\s+", " ", texto).strip()
    if limite and len(texto) > limite:
        texto = texto[: limite - 1].rsplit(" ", 1)[0] + "…"
    return texto


def validar_feed(sessao, url):
    """Baixa e confere o feed. Devolve (feed, erro)."""
    try:
        resposta = baixar(sessao, url)
    except requests.RequestException as e:
        return None, f"não abriu ({descrever_erro(e)})"
    feed = feedparser.parse(resposta.content)
    if not feed.entries:
        return None, "sem entradas"
    if len(feed.entries) < MIN_ENTRADAS:
        return None, f"só {len(feed.entries)} entrada(s)"
    if not all(e.get("title") for e in feed.entries[:MIN_ENTRADAS]):
        return None, "entradas sem título"
    datas = [d for d in (data_da_entrada(e) for e in feed.entries) if d]
    if datas and max(datas) < datetime.now(timezone.utc) - timedelta(days=MAX_DIAS_SEM_PUBLICAR):
        return None, f"última publicação em {max(datas):%d/%m/%Y} (parado há mais de {MAX_DIAS_SEM_PUBLICAR} dias)"
    feed["_url_final"] = resposta.url
    return feed, None


def catalogar(sessao, candidato):
    """Tenta, nessa ordem: RSS do próprio site, sitemap de notícias,
    RSS de busca do Google Notícias. Fica com o primeiro que validar."""
    motivos = []
    nome_site = None
    try:
        possiveis, nome_site = descobrir_feeds(sessao, candidato.url)
    except requests.RequestException as e:
        # Site fora do ar ou bloqueando robôs: ainda dá pra tentar o Google Notícias
        possiveis = []
        motivos.append(f"site não abriu ({descrever_erro(e)})")

    for url in possiveis:
        feed, erro = validar_feed(sessao, url)
        if feed is None:
            motivos.append(f"RSS: {url}: {erro}")
            continue
        datas = [d for d in (data_da_entrada(e) for e in feed.entries) if d]
        return Resultado(
            candidato,
            feed_url=feed["_url_final"],
            nome=escolher_nome(candidato, feed.feed.get("title"), nome_site),
            descricao=limpar(feed.feed.get("subtitle") or feed.feed.get("description"), 120) or None,
            entradas=len(feed.entries),
            ultima=max(datas) if datas else None,
        )
    # dos motivos de RSS, só o primeiro (geralmente o feed declarado no HTML)
    motivos = [m for m in motivos if not m.startswith("RSS")] + [m for m in motivos if m.startswith("RSS")][:1]

    resultado = tentar_sitemap(candidato, nome_site, motivos)
    if resultado:
        return resultado
    resultado = tentar_google_news(sessao, candidato, nome_site, motivos)
    if resultado:
        return resultado
    return Resultado(candidato, erro=" | ".join(motivos))


def alvo_do_site(url):
    """Endereço pro sitemap e pro Google Notícias: a seção, se o candidato
    aponta pra uma (bbc.com/portuguese), mas a página inicial se ele já é
    o endereço de um feed (electrek.co/feed/): "site:electrek.co/feed" no
    Google Notícias não acha nada."""
    p = urlparse(url)
    if re.search(r"(^|/)(feeds?|rss|atom)(/|$)|\.(xml|rss|atom|cms)$", p.path.lower()):
        return f"{p.scheme}://{p.netloc}"
    return url


def recente_o_bastante(datas):
    limite = datetime.now(timezone.utc) - timedelta(days=MAX_DIAS_SEM_PUBLICAR)
    return not datas or max(datas) >= limite


def tentar_sitemap(candidato, nome_site, motivos):
    """Sitemap de notícias declarado no robots.txt (ou num caminho comum).
    Se o candidato aponta pra uma seção (ex.: bbc.com/portuguese), o
    filtro vai junto no endereço salvo (#caminho=...)."""
    alvo = alvo_do_site(candidato.url)
    caminho = urlparse(alvo).path.rstrip("/")
    try:
        sitemaps = sitemaps_do_robots(alvo, USER_AGENT)
    except requests.RequestException as e:
        motivos.append(f"sitemap: robots.txt não abriu ({descrever_erro(e)})")
        return None
    for sitemap in sitemaps:
        endereco = sitemap + (f"#caminho={caminho}" if caminho else "")
        try:
            itens = ler_sitemap(endereco, USER_AGENT)
        except Exception:
            continue
        datas = [i["published_at"] for i in itens if i["published_at"]]
        if len(itens) < MIN_ENTRADAS or not recente_o_bastante(datas):
            continue
        return Resultado(
            candidato,
            feed_url=endereco,
            nome=escolher_nome(candidato, None, nome_site),
            descricao=None,
            entradas=len(itens),
            ultima=max(datas) if datas else None,
            via="sitemap",
        )
    motivos.append("sem sitemap de notícias")
    return None


def tentar_google_news(sessao, candidato, nome_site, motivos):
    """RSS de busca do Google Notícias restrito ao site. Confere se as
    notícias são mesmo do site pedido (o campo <source> de cada item)."""
    alvo = alvo_do_site(candidato.url)
    url = url_google_news(alvo, candidato.idioma)
    feed, erro = validar_feed(sessao, url)
    if feed is None:
        motivos.append(f"Google Notícias: {erro}")
        return None
    do_site = entradas_do_site(feed.entries, alvo)
    if len(do_site) < MIN_ENTRADAS:
        motivos.append("Google Notícias: resultados não são desse site")
        return None
    titulo_fonte = do_site[0].get("source", {}).get("title")
    datas = [d for d in (data_da_entrada(e) for e in do_site) if d]
    return Resultado(
        candidato,
        feed_url=url,
        nome=escolher_nome(candidato, titulo_fonte, nome_site),
        descricao="Via Google Notícias",
        entradas=len(do_site),
        ultima=max(datas) if datas else None,
        via="google_news",
    )


def urls_ja_no_catalogo():
    """Lê (só leitura) as URLs que já estão em feed_catalog, pra não repetir.
    Sem DATABASE_URL configurado, segue sem esse filtro (o SQL gerado usa
    on conflict do nothing de qualquer jeito)."""
    try:
        from db import get_connection  # noqa: E402  (reaproveita o db.py do coletor)

        conn = get_connection()
        conn.set_session(readonly=True)
        with conn.cursor() as cur:
            cur.execute("select url from feed_catalog")
            urls = {linha[0] for linha in cur.fetchall()}
        conn.close()
        return urls
    except Exception as e:  # sem banco disponível: não é motivo pra parar
        print(f"(aviso: não consegui ler feed_catalog — {e}. Seguindo sem checar duplicadas.)")
        return set()


def site_de(url):
    """Domínio de um site ou de uma fonte do catálogo, sem 'www.'. Pro RSS
    do Google Notícias, é o site da busca (q=site:...), não o google.com."""
    p = urlparse(url)
    if p.netloc == "news.google.com":
        alvo = parse_qs(p.query).get("q", [""])[0].removeprefix("site:")
        return alvo.split("/")[0].removeprefix("www.")
    return p.netloc.lower().removeprefix("www.")


def sql_texto(valor):
    if valor is None:
        return "null"
    return "'" + str(valor).replace("'", "''") + "'"


def proximo_arquivo_sql(rotulo=None):
    numeros = [int(p.name[:3]) for p in (RAIZ / "sql").glob("[0-9][0-9][0-9]_*.sql")]
    numero = max(numeros, default=0) + 1
    meio = f"catalogo_{rotulo}" if rotulo else "catalogo"
    return RAIZ / "sql" / f"{numero:03d}_{meio}_{date.today().isoformat()}.sql"


def escrever_sql(aprovados, caminho):
    linhas = [
        "-- ============================================================",
        f"-- {caminho.name}",
        f"-- Gerado por catalogo/catalogar.py em {datetime.now():%d/%m/%Y %H:%M}.",
        "-- Cada feed abaixo foi baixado e validado (entradas, títulos, publicação",
        f"-- recente nos últimos {MAX_DIAS_SEM_PUBLICAR} dias). Revise nomes/descrições antes de rodar.",
        "-- on conflict (url) do nothing: rodar duas vezes não duplica nada.",
        "--",
        "-- Entram só no mapa (vitrine = false, o padrão do sql/031): não são",
        "-- coletadas de hora em hora. Quando alguém segue, viram fonte normal.",
        "-- ============================================================",
        "",
        "-- kind: 'rss' (inclui o RSS de busca do Google Notícias) ou 'sitemap' (sql/021).",
        "",
        "insert into feed_catalog (category, name, url, description, kind, idioma, regiao) values",
    ]
    valores = []
    for r in sorted(aprovados, key=lambda r: (CATEGORIAS.index(r.candidato.categoria), r.candidato.regiao or "", r.nome.lower())):
        ultima = f"{r.ultima:%d/%m/%Y}" if r.ultima else "sem data"
        origem = {"rss": "RSS do site", "sitemap": "sitemap de notícias", "google_news": "Google Notícias"}[r.via]
        kind = "sitemap" if r.via == "sitemap" else "rss"
        valores.append(
            f"    -- via {origem}: {r.entradas} entradas, última em {ultima}\n"
            f"    ({sql_texto(r.candidato.categoria)}, {sql_texto(r.nome)}, {sql_texto(r.feed_url)}, "
            f"{sql_texto(r.descricao)}, {sql_texto(kind)}, {sql_texto(r.candidato.idioma)}, {sql_texto(r.candidato.regiao)})"
        )
    linhas.append(",\n".join(valores))
    linhas.append("on conflict (url) do nothing;")
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")


_local = threading.local()


def _sessao():
    """Uma sessão HTTP por thread (requests.Session não é segura entre threads)."""
    if not hasattr(_local, "sessao"):
        _local.sessao = requests.Session()
        _local.sessao.headers["User-Agent"] = USER_AGENT
    return _local.sessao


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidatos", default=str(RAIZ / "catalogo" / "candidatos.txt"))
    parser.add_argument("--idioma", default="pt", choices=IDIOMAS, help="idioma das linhas que não dizem o próprio")
    parser.add_argument("--rotulo", help="entra no nome do arquivo SQL (ex.: ingles)")
    args = parser.parse_args()

    candidatos, erros_arquivo = ler_candidatos(Path(args.candidatos), args.idioma)
    for erro in erros_arquivo:
        print(f"  ignorado — {erro}")

    ja_catalogadas = urls_ja_no_catalogo()
    sites_catalogados = {site_de(u) for u in ja_catalogadas}

    # Candidato que é a página inicial de um site já catalogado: pula,
    # mesmo que o feed de hoje dê outro endereço (ex.: o RSS falhou e
    # sairia pelo Google Notícias, duplicando a fonte). Candidatos com
    # caminho (ex.: seções do G1) continuam sendo checados pela URL.
    def ja_no_catalogo(c):
        return urlparse(c.url).path.strip("/") == "" and site_de(c.url) in sites_catalogados

    pendentes = [c for c in candidatos if not ja_no_catalogo(c)]
    repetidos = [Resultado(c) for c in candidatos if ja_no_catalogo(c)]
    for r in repetidos:
        print(f"= site já no catálogo: {r.candidato.url}")

    feitos = [0]
    trava = threading.Lock()

    def processar(candidato):
        try:
            resultado = catalogar(_sessao(), candidato)
        except Exception as e:  # feed malformado que derruba o feedparser etc.: rejeita só este
            resultado = Resultado(candidato, erro=f"erro inesperado ({type(e).__name__}: {e})")
        with trava:
            feitos[0] += 1
            marca = "✗" if resultado.erro else "✓"
            detalhe = resultado.erro if resultado.erro else f"{resultado.nome} [{resultado.via}] — {resultado.feed_url}"
            print(f"[{feitos[0]}/{len(pendentes)}] {marca} {candidato.url}: {detalhe}", flush=True)
        return resultado

    with ThreadPoolExecutor(SITES_EM_PARALELO) as executor:
        resultados = list(executor.map(processar, pendentes))

    # na ordem do arquivo: se dois candidatos dão no mesmo feed, fica o primeiro
    aprovados, rejeitados = [], []
    vistos = set(ja_catalogadas)
    for resultado in resultados:
        if resultado.erro:
            rejeitados.append(resultado)
        elif resultado.feed_url in vistos:
            repetidos.append(resultado)
        else:
            vistos.add(resultado.feed_url)
            aprovados.append(resultado)

    print()
    print(f"{len(aprovados)} aprovado(s), {len(repetidos)} já no catálogo, {len(rejeitados)} rejeitado(s).")
    for r in rejeitados:
        print(f"  rejeitado: {r.candidato.url} — {r.erro[:160]}")
    if not aprovados:
        print("Nada novo pra catalogar — nenhum arquivo SQL gerado.")
        return
    caminho = proximo_arquivo_sql(args.rotulo)
    escrever_sql(aprovados, caminho)
    print(f"SQL gerado: {caminho.relative_to(RAIZ)} — revise e rode no SQL Editor do Supabase.")


if __name__ == "__main__":
    main()
