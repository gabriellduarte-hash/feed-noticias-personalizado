"""Monta o HTML do e-mail do resumo diário, com a identidade do hub:
preto e branco em cinzas quentes, roxo só em destaque, JetBrains Mono.

Estrutura:
  - capa: foto do dia (Unsplash, envio/foto_do_dia.py) com a data numa
    "pílula" embaixo, e o título do resumo;
  - as notícias completas (as mais recentes com resumo da IA), em seções
    por categoria editorial, na ordem da mais recente de cada seção;
  - cada notícia: capa da notícia ACIMA do texto, site de origem (no lugar
    do autor), título e o resumo formatado da IA;
  - "Mais manchetes": do resto, só site, hora e título, e um link pro hub
    com o que sobrou;
  - rodapé com link pro hub e onde mudar o horário do resumo.

E-mail HTML é um mundo à parte: Gmail e Outlook ignoram <style> e CSS
externo, então tudo é `style="..."` inline, com tabelas pra estrutura
(o que todos os clientes respeitam). A fonte JetBrains Mono carrega no
Apple Mail/iOS; no Gmail cai pra outra monoespaçada.

Todo texto que vem de fora (título, site, resumo da IA) passa por
html.escape antes de entrar no HTML (o Markdown do resumo só vira
<strong>/<em>/citação DEPOIS do escape), e só links http(s) viram href/src.
"""
import html
import re
from datetime import date, timedelta
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

FUSO_BR = ZoneInfo("America/Sao_Paulo")

HUB_URL = "https://feed-hub-leitura.vercel.app"

FONTE = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace"
PRETO = "#121212"
TEXTO = "#3f3d39"
CINZA = "#8d8a83"
LINHA = "#e1dfda"
FUNDO = "#f4f3f0"
UNSPLASH_HOME = "https://unsplash.com/?utm_source=feed_de_noticias&utm_medium=referral"
ROXO = "#6d3ff5"

CSS_P = f"margin: 0 0 14px; font-family: {FONTE}; font-size: 14px; line-height: 1.75; color: {TEXTO};"
CSS_CITACAO = (
    f"margin: 4px 0 16px; padding: 2px 0 2px 14px; border-left: 2px solid {ROXO}; "
    f"font-family: {FONTE}; font-size: 15px; line-height: 1.7; font-style: italic; color: {PRETO};"
)
CSS_CITACAO_AUTOR = (
    f"display: block; margin-top: 6px; font-style: normal; font-size: 11px; "
    f"letter-spacing: 0.5px; color: {CINZA}; font-weight: 600;"
)

DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def _esc(texto):
    return html.escape(texto or "", quote=True)


def _url_segura(url):
    """Só http(s) vira link/imagem (nada de javascript: vindo de um feed)."""
    return _esc(url) if url and urlparse(url).scheme in ("http", "https") else ""


def _host(url):
    p = urlparse(url or "")
    # fonte lida pelo Google Notícias (q=site:macmagazine.com.br): o site
    # de verdade é o da busca, não o news.google.com
    if p.netloc == "news.google.com":
        site = re.search(r"site:([^\s/]+)", parse_qs(p.query).get("q", [""])[0])
        if site:
            return site.group(1).removeprefix("www.")
    return p.netloc.removeprefix("www.")


def _no_brasil(momento):
    # o banco devolve em UTC; o leitor está no Brasil
    return momento.astimezone(FUSO_BR) if momento.tzinfo else momento


def desde_quando(desde, hoje: date):
    """"ontem às 07:00", "hoje às 07:00" ou "5/10 às 07:00"."""
    d = _no_brasil(desde)
    if d.date() == hoje:
        dia = "hoje"
    elif d.date() == hoje - timedelta(days=1):
        dia = "ontem"
    else:
        dia = f"{d.day}/{d.month}"
    return f"{dia} às {d:%H:%M}"


def data_extenso(d: date):
    return f"{DIAS[d.weekday()]}, {d.day} de {MESES[d.month - 1]}"


def _inline(texto):
    """Depois do html.escape: **negrito** e *itálico* do resumo da IA."""
    texto = re.sub(r"\*\*(.+?)\*\*", rf'<strong style="color: {PRETO}; font-weight: 700;">\1</strong>', texto)
    return re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", texto)


def resumo_para_html(resumo):
    """O resumo vem em Markdown simples (resumo/resumir.py): parágrafos
    separados por linha em branco, **negrito**, e "> citação — Autor".
    Tudo é escapado ANTES de virar tag, então nada que a IA escreva vira
    HTML de verdade. Resumos antigos (texto corrido) viram um parágrafo."""
    blocos = [b.strip() for b in re.split(r"\n\s*\n", (resumo or "").strip()) if b.strip()]
    partes = []
    for bloco in blocos:
        if bloco.startswith(">"):
            texto = " ".join(linha.lstrip("> ").strip() for linha in bloco.splitlines())
            autor = ""
            m = re.match(r"^(.*?)\s+[—–-]\s+([^—–\-]{2,60})$", texto)
            if m:
                texto, autor = m.group(1), m.group(2)
            autor_html = f'<span style="{CSS_CITACAO_AUTOR}">— {_esc(autor)}</span>' if autor else ""
            partes.append(f'<p style="{CSS_CITACAO}">{_inline(_esc(texto))}{autor_html}</p>')
        else:
            texto = " ".join(linha.strip() for linha in bloco.splitlines())
            partes.append(f'<p style="{CSS_P}">{_inline(_esc(texto))}</p>')
    return "".join(partes)


# ------------------------------------------------------------------ partes

def _capa(foto, dia: date, contagem):
    imagem = credito = ""
    if foto and _url_segura(foto["url"]):
        # a foto leva pra página dela no Unsplash
        imagem = f"""
      <tr><td style="padding: 0 0 0;">
        <a href="{_url_segura(foto['unsplash_url'])}" style="display: block;">
          <img src="{_url_segura(foto['url'])}" width="600" alt=""
               style="display: block; width: 100%; max-width: 600px; height: auto; border-radius: 16px; border: 0;">
        </a>
      </td></tr>"""
        # crédito no formato que o Unsplash pede ("Photo by Fulano on Unsplash"):
        # nome do fotógrafo → perfil dele, "Unsplash" → página inicial, ambos com UTM
        credito = (
            f'<p style="margin: 10px 0 0; font-family: {FONTE}; font-size: 10px; color: {CINZA}; text-align: center;">'
            f'Foto de <a href="{_url_segura(foto["fotografo_url"])}" style="color: {CINZA};">{_esc(foto["fotografo"])}</a>'
            f' no <a href="{_esc(UNSPLASH_HOME)}" style="color: {CINZA};">Unsplash</a></p>'
        )
    return f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr><td align="center" style="padding: 8px 0 22px;">
        <p style="margin: 0; font-family: {FONTE}; font-size: 20px; font-weight: 800; letter-spacing: -0.3px; color: {PRETO};">
          <span style="color: {ROXO};">{{</span>daily paper<span style="color: {ROXO};">}}</span>
        </p>
      </td></tr>{imagem}
      <tr><td align="center" style="padding: {'18px' if imagem else '4px'} 0 0;">
        <span style="display: inline-block; padding: 9px 20px; border-radius: 999px; background: {PRETO};
                     font-family: {FONTE}; font-size: 13px; font-weight: 700; color: #ffffff; letter-spacing: 0.3px;">
          {_esc(data_extenso(dia))}
        </span>
        {credito}
      </td></tr>
      <tr><td align="center" style="padding: 26px 8px 6px;">
        <h1 style="margin: 0; font-family: {FONTE}; font-size: 30px; line-height: 1.15; font-weight: 800;
                   letter-spacing: -0.5px; color: {PRETO};">Seu resumo do dia</h1>
        <p style="margin: 10px 0 0; font-family: {FONTE}; font-size: 13px; line-height: 1.6; font-weight: 300; color: {TEXTO};">
          {contagem}
        </p>
      </td></tr>
    </table>"""


def _secao(categoria):
    return f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr><td style="padding: 40px 0 6px; border-bottom: 1px solid {LINHA};">
        <p style="margin: 0 0 8px; font-family: {FONTE}; font-size: 11px; font-weight: 700; letter-spacing: 2.5px;
                  text-transform: uppercase; color: {ROXO};">{_esc(categoria)}</p>
      </td></tr>
    </table>"""


def _noticia(card, ultima):
    url = _url_segura(card["url"])
    host = _host(card.get("fonte_url") or card["url"])
    site = card.get("fonte") or host
    capa = ""
    if _url_segura(card.get("image_url")):
        capa = f"""
        <a href="{url}" style="text-decoration: none;">
          <img src="{_url_segura(card['image_url'])}" width="600" alt=""
               style="display: block; width: 100%; max-width: 600px; height: auto; border-radius: 12px; border: 0; margin: 0 0 16px;">
        </a>"""
    favicon = f"https://www.google.com/s2/favicons?domain={_esc(host)}&sz=32"
    quando = ""
    if card.get("published_at"):
        p = _no_brasil(card["published_at"])
        quando = f" &nbsp;·&nbsp; {p.day} {MESES[p.month - 1][:3]}, {p:%H:%M}"
    return f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr><td style="padding: 26px 0 {'8px' if ultima else '22px'}; {'' if ultima else f'border-bottom: 1px solid {LINHA};'}">
        {capa}
        <p style="margin: 0 0 8px; font-family: {FONTE}; font-size: 11px; color: {CINZA};">
          <img src="{favicon}" width="14" height="14" alt="" style="vertical-align: -2px; border-radius: 3px; border: 0;">
          &nbsp;<strong style="color: {PRETO}; font-weight: 700;">{_esc(site)}</strong>{quando}
        </p>
        <h2 style="margin: 0 0 14px; font-family: {FONTE}; font-size: 20px; line-height: 1.3; font-weight: 800;
                   letter-spacing: -0.3px;">
          <a href="{url}" style="color: {PRETO}; text-decoration: none;">{_esc(card['title'])}</a>
        </h2>
        {resumo_para_html(card['resumo'])}
        <a href="{url}" style="font-family: {FONTE}; font-size: 12px; font-weight: 700; color: {ROXO}; text-decoration: none;">
          Ler em {_esc(host)} &rarr;
        </a>
      </td></tr>
    </table>"""


def _manchetes(itens, restantes):
    """Do que não coube nas notícias completas: site, hora e título (o
    título é o link), e no fim um link pro hub com o que sobrou."""
    linhas = []
    for c in itens:
        host = _host(c.get("fonte_url") or c["url"])
        quando = f" &nbsp;·&nbsp; {_no_brasil(c['published_at']):%H:%M}" if c.get("published_at") else ""
        linhas.append(f"""
      <tr><td style="padding: 12px 0; border-top: 1px solid {LINHA};">
        <p style="margin: 0 0 4px; font-family: {FONTE}; font-size: 10px; color: {CINZA};">
          <img src="https://www.google.com/s2/favicons?domain={_esc(host)}&sz=32" width="12" height="12" alt=""
               style="vertical-align: -2px; border-radius: 2px; border: 0;">
          &nbsp;<strong style="color: {TEXTO}; font-weight: 700;">{_esc(c.get('fonte') or host)}</strong>{quando}
        </p>
        <a href="{_url_segura(c['url'])}" style="font-family: {FONTE}; font-size: 14px; line-height: 1.45; font-weight: 700;
           color: {PRETO}; text-decoration: none;">{_esc(c['title'])}</a>
      </td></tr>""")
    if restantes:
        linhas.append(f"""
      <tr><td style="padding: 14px 0 0; border-top: 1px solid {LINHA};">
        <a href="{HUB_URL}" style="font-family: {FONTE}; font-size: 12px; font-weight: 700; color: {ROXO}; text-decoration: none;">
          + {restantes} {'notícia' if restantes == 1 else 'notícias'} no Daily Paper &rarr;</a>
      </td></tr>""")
    return f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr><td style="padding: 40px 0 8px;">
        <p style="margin: 0; font-family: {FONTE}; font-size: 11px; font-weight: 700; letter-spacing: 2.5px;
                  text-transform: uppercase; color: {ROXO};">Mais manchetes</p>
      </td></tr>{''.join(linhas)}
    </table>"""


def _apoio():
    """Pedido de apoio ao projeto (PIX), no fim: o pagamento em si fica na
    página /apoiar do hub (e-mail não copia código nem gera QR)."""
    return f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr><td align="center" style="padding: 44px 8px 36px; border-top: 1px solid {LINHA};">
        <p style="margin: 0 0 8px; font-size: 24px; line-height: 1;">&#9749;</p>
        <p style="margin: 0 0 8px; font-family: {FONTE}; font-size: 16px; font-weight: 800; color: {PRETO};">Gostou do resumo de hoje?</p>
        <p style="margin: 0 0 18px; font-family: {FONTE}; font-size: 12px; line-height: 1.7; color: {TEXTO};">
          Este projeto é independente e não depende de publicidade para funcionar.<br>
          Se ele foi útil para você, ajude a mantê-lo.
        </p>
        <a href="{HUB_URL}/apoiar" style="display: inline-block; padding: 11px 22px; border-radius: 8px; background: {ROXO};
           font-family: {FONTE}; font-size: 13px; font-weight: 700; color: #ffffff; text-decoration: none;">Apoiar com PIX &rarr;</a>
        <p style="margin: 16px 0 0; font-family: {FONTE}; font-size: 11px; color: {CINZA};">Obrigado por apoiar o projeto &#10084;&#65039;</p>
      </td></tr>
    </table>"""


def montar_email_html(cards_por_categoria: dict, data: date, foto=None, *,
                      manchetes=(), restantes=0, total=None, desde=None) -> str:
    """cards_por_categoria: {categoria: [card, ...]}, as notícias completas
    na ordem das seções. card: title, url, fonte, fonte_url, image_url,
    published_at, resumo.
    manchetes: cards sem resumo (só o título aparece); restantes: quantas
    notícias do período ficaram de fora (viram o link pro hub).
    total e desde: quantas notícias chegaram no período e desde quando.
    foto: a foto do dia (envio/foto_do_dia.py) ou None."""
    cards = [c for itens in cards_por_categoria.values() for c in itens]
    total = total if total is not None else len(cards) + len(manchetes) + restantes
    contagem = f"{total} {'notícia nova' if total == 1 else 'notícias novas'}"
    if desde:
        contagem += f" desde {desde_quando(desde, data)}"
    if len(cards) + len(manchetes) < total:
        contagem += ". Aqui estão as mais recentes."

    corpo = []
    for categoria, itens in cards_por_categoria.items():
        corpo.append(_secao(categoria))
        corpo.extend(_noticia(c, i == len(itens) - 1) for i, c in enumerate(itens))
    if manchetes or restantes:
        corpo.append(_manchetes(manchetes, restantes))

    # texto que aparece na prévia da caixa de entrada (fica escondido no corpo)
    previa = _esc(" · ".join(c["title"] for c in [*cards, *manchetes][:3]))

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700;800&display=swap" rel="stylesheet">
  <title>Seu resumo do dia</title>
</head>
<body style="margin: 0; padding: 0; background-color: {FUNDO};">
  <div style="display: none; max-height: 0; overflow: hidden; opacity: 0;">{previa}</div>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: {FUNDO};">
    <tr><td align="center" style="padding: 24px 16px 40px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px;">
        <tr><td>
          {_capa(foto, data, contagem)}
          {''.join(corpo)}
          {_apoio()}
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr><td style="padding: 32px 0 0; border-top: 1px solid {LINHA};">
              <p style="margin: 0 0 6px; font-family: {FONTE}; font-size: 11px; line-height: 1.7; color: {CINZA};">
                Você recebe este resumo porque segue fontes no Daily Paper.
              </p>
              <p style="margin: 0; font-family: {FONTE}; font-size: 11px; line-height: 1.7; color: {CINZA};">
                <a href="{HUB_URL}" style="color: {PRETO}; font-weight: 700; text-decoration: none;">Abrir o Daily Paper</a>
                &nbsp;·&nbsp; para mudar o horário ou o que entra no resumo, vá em Configurações &rsaquo; Resumo diário
              </p>
            </td></tr>
          </table>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""
