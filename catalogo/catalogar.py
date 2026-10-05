"""
Cataloga novas fontes pro "Seguir fontes" do hub.

Fluxo:
  1. Lê catalogo/candidatos.txt (categoria + URL de um site ou de um feed).
  2. Pra cada candidato, descobre o feed RSS/Atom:
       - a própria URL já é um feed? usa ela;
       - senão, procura <link rel="alternate" type="application/rss+xml"> no HTML;
       - senão, tenta caminhos comuns (/feed, /rss, /rss.xml...).
  3. Valida o feed de verdade (feedparser): tem entradas, títulos, e
     publicou algo recentemente.
  4. Gera um arquivo sql/0NN_catalogo_AAAA-MM-DD.sql com os INSERTs —
     não grava nada no banco. Você revisa o arquivo e roda no SQL Editor.

Uso (da raiz do projeto, com o .venv ativo):
    python catalogo/catalogar.py
    python catalogo/catalogar.py --candidatos outro_arquivo.txt
"""
import argparse
import html
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import feedparser
import requests

# Mesmo User-Agent do coletor: se um site bloquear aqui, vai bloquear lá
# também, então é melhor descobrir agora do que depois de catalogado.
USER_AGENT = "FeedNoticiasBot/0.1 (uso pessoal - estudo)"
TIMEOUT_SEGUNDOS = 15
PAUSA_ENTRE_SITES_SEGUNDOS = 1.0
MIN_ENTRADAS = 3
MAX_DIAS_SEM_PUBLICAR = 45

# Mesma lista fixa de resumo/resumir.py e do check constraint de articles.category
CATEGORIAS = [
    "Tecnologia", "Finanças", "Humor", "Política", "Ciência",
    "Saúde", "Esportes", "Entretenimento", "Mundo", "Outros",
]

CAMINHOS_COMUNS = ["/feed", "/feed/", "/rss", "/rss/", "/rss.xml", "/feed.xml", "/atom.xml", "/index.xml"]
TIPOS_FEED = ("application/rss+xml", "application/atom+xml", "application/feed+json", "application/xml", "text/xml")

RAIZ = Path(__file__).resolve().parent.parent


class Candidato:
    def __init__(self, categoria, url, nome=None, linha=0):
        self.categoria = categoria
        self.url = url
        self.nome = nome
        self.linha = linha


class Resultado:
    def __init__(self, candidato, feed_url=None, nome=None, descricao=None, entradas=0, ultima=None, erro=None):
        self.candidato = candidato
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


def ler_candidatos(caminho):
    """Formato: uma linha por site, "Categoria | URL" ou "Categoria | URL | Nome".
    Linhas vazias e começando com # são ignoradas."""
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
        candidatos.append(Candidato(categoria, url, partes[2] if len(partes) > 2 and partes[2] else None, n))
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
    try:
        possiveis, nome_site = descobrir_feeds(sessao, candidato.url)
    except requests.RequestException as e:
        return Resultado(candidato, erro=f"site não abriu ({descrever_erro(e)})")

    motivos = []
    for url in possiveis:
        feed, erro = validar_feed(sessao, url)
        if feed is None:
            motivos.append(f"{url}: {erro}")
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
    # mostra só o primeiro motivo: geralmente é o mais informativo (o feed declarado no HTML)
    return Resultado(candidato, erro="nenhum feed válido" + (f" — {motivos[0]}" if motivos else ""))


def urls_ja_no_catalogo():
    """Lê (só leitura) as URLs que já estão em feed_catalog, pra não repetir.
    Sem DATABASE_URL configurado, segue sem esse filtro (o SQL gerado usa
    on conflict do nothing de qualquer jeito)."""
    try:
        sys.path.insert(0, str(RAIZ / "coletor"))
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


def sql_texto(valor):
    if valor is None:
        return "null"
    return "'" + str(valor).replace("'", "''") + "'"


def proximo_arquivo_sql():
    numeros = [int(p.name[:3]) for p in (RAIZ / "sql").glob("[0-9][0-9][0-9]_*.sql")]
    numero = max(numeros, default=0) + 1
    return RAIZ / "sql" / f"{numero:03d}_catalogo_{date.today().isoformat()}.sql"


def escrever_sql(aprovados, caminho):
    linhas = [
        "-- ============================================================",
        f"-- {caminho.name}",
        f"-- Gerado por catalogo/catalogar.py em {datetime.now():%d/%m/%Y %H:%M}.",
        "-- Cada feed abaixo foi baixado e validado (entradas, títulos, publicação",
        f"-- recente nos últimos {MAX_DIAS_SEM_PUBLICAR} dias). Revise nomes/descrições antes de rodar.",
        "-- on conflict (url) do nothing: rodar duas vezes não duplica nada.",
        "-- ============================================================",
        "",
        "insert into feed_catalog (category, name, url, description) values",
    ]
    valores = []
    for r in sorted(aprovados, key=lambda r: (CATEGORIAS.index(r.candidato.categoria), r.nome.lower())):
        ultima = f"{r.ultima:%d/%m/%Y}" if r.ultima else "sem data"
        valores.append(
            f"    -- {r.entradas} entradas, última em {ultima}\n"
            f"    ({sql_texto(r.candidato.categoria)}, {sql_texto(r.nome)}, {sql_texto(r.feed_url)}, {sql_texto(r.descricao)})"
        )
    linhas.append(",\n".join(valores))
    linhas.append("on conflict (url) do nothing;")
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidatos", default=str(RAIZ / "catalogo" / "candidatos.txt"))
    args = parser.parse_args()

    candidatos, erros_arquivo = ler_candidatos(Path(args.candidatos))
    for erro in erros_arquivo:
        print(f"  ignorado — {erro}")

    ja_catalogadas = urls_ja_no_catalogo()
    sessao = requests.Session()
    sessao.headers["User-Agent"] = USER_AGENT

    aprovados, rejeitados, repetidos = [], [], []
    vistos = set(ja_catalogadas)
    for i, candidato in enumerate(candidatos, start=1):
        print(f"[{i}/{len(candidatos)}] {candidato.categoria:<14} {candidato.url}")
        resultado = catalogar(sessao, candidato)
        if resultado.erro:
            print(f"    ✗ {resultado.erro}")
            rejeitados.append(resultado)
        elif resultado.feed_url in vistos:
            print(f"    = já no catálogo ({resultado.feed_url})")
            repetidos.append(resultado)
        else:
            print(f"    ✓ {resultado.nome} — {resultado.feed_url} ({resultado.entradas} entradas)")
            vistos.add(resultado.feed_url)
            aprovados.append(resultado)
        time.sleep(PAUSA_ENTRE_SITES_SEGUNDOS)

    print()
    print(f"{len(aprovados)} aprovado(s), {len(repetidos)} já no catálogo, {len(rejeitados)} rejeitado(s).")
    if not aprovados:
        print("Nada novo pra catalogar — nenhum arquivo SQL gerado.")
        return
    caminho = proximo_arquivo_sql()
    escrever_sql(aprovados, caminho)
    print(f"SQL gerado: {caminho.relative_to(RAIZ)} — revise e rode no SQL Editor do Supabase.")


if __name__ == "__main__":
    main()
