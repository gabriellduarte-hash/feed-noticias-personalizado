"""
A mesma notícia por dois caminhos: o feed do site (link direto, com
texto) e o plano B do Google Notícias (link do Google, só o título).
Quando os dois entram no mesmo feed, a pessoa vê a notícia duas vezes.

Os títulos nem sempre são iguais: o Google usa o título da página, o
feed usa a manchete ("Inter e Grêmio empatam em clássico dramático e
seguem juntos no Z-4" x "...no Sul e seguem lado a lado no Z-4 do
Brasileirão"). Por isso a comparação é pelas palavras principais: se
quase todas as palavras da manchete mais curta estão na outra, é a mesma.

A mesma regra está no hub (src/lib/manchetes.ts).
"""
import re
import unicodedata

PALAVRAS_FRACAS = {
    "and", "com", "das", "dos", "for", "mas", "nas", "nos", "num", "para", "pela", "pelo",
    "por", "que", "sem", "sob", "sua", "seu", "the", "uma", "with",
}
MIN_PALAVRAS = 5          # manchete curta demais não dá pra comparar com segurança
SOBREPOSICAO_MINIMA = 0.8
DIAS_PRA_COMPARAR = 3


def eh_link_do_google(url):
    return (url or "").startswith("https://news.google.com/")


def palavras(titulo):
    sem_acento = unicodedata.normalize("NFKD", titulo or "").encode("ascii", "ignore").decode().lower()
    return {p for p in re.split(r"[^a-z0-9]+", sem_acento) if len(p) >= 3 and p not in PALAVRAS_FRACAS}


def mesma_manchete(a, b):
    pa, pb = palavras(a), palavras(b)
    if not pa or not pb:
        return False
    if pa == pb:
        return True
    menor = min(len(pa), len(pb))
    return menor >= MIN_PALAVRAS and len(pa & pb) / menor >= SOBREPOSICAO_MINIMA


def separar_repetidas(existentes, novas):
    """existentes: notícias recentes do mesmo feed ({"id", "url", "title"}).
    Devolve (inserir, promover):
      - do Google, repetindo uma que já existe: fica de fora;
      - direta, repetindo uma do Google: vai pra `promover` como
        (id da do Google, notícia direta). A do Google ganha o link, o
        texto e a foto, e mantém o id, então "lido" e "salvo" continuam;
      - o resto entra normalmente (link repetido o banco já ignora)."""
    inserir, promover = [], []
    do_google = [e for e in existentes if eh_link_do_google(e["url"])]
    ja_promovidas = set()
    for nova in novas:
        if eh_link_do_google(nova.get("url")):
            if any(mesma_manchete(nova["title"], e["title"]) for e in existentes):
                continue
        else:
            alvo = next(
                (e for e in do_google if e["id"] not in ja_promovidas and mesma_manchete(nova["title"], e["title"])),
                None,
            )
            if alvo:
                ja_promovidas.add(alvo["id"])
                promover.append((alvo["id"], nova))
                continue
        inserir.append(nova)
    return inserir, promover
