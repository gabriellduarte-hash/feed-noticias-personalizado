"""Monta o HTML do e-mail do resumo diário, com a identidade do hub:
preto e branco em cinzas quentes, roxo só em destaque, JetBrains Mono.

Estrutura:
  - capa: foto do dia (Unsplash, envio/foto_do_dia.py) com a data numa
    "pílula" embaixo, e o título do resumo;
  - seções por categoria editorial (Tecnologia, Finanças, ...);
  - cada notícia: capa da notícia ACIMA do texto, site de origem (no lugar
    do autor), título e o resumo formatado da IA;
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
from datetime import date
from urllib.parse import urlparse
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
    return urlparse(url or "").netloc.removeprefix("www.")


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

def _capa(foto, dia: date, total, fontes):
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
        <p style="margin: 0; font-family: {FONTE}; font-size: 11px; font-weight: 700; letter-spacing: 3px; color: {PRETO};">
          <span style="color: {ROXO};">●</span>&nbsp;FEED DE NOTÍCIAS
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
        <p style="margin: 10px 0 0; font-family: {FONTE}; font-size: 13px; font-weight: 300; color: {TEXTO};">
          {total} {'notícia' if total == 1 else 'notícias'} de {fontes} {'fonte' if fontes == 1 else 'fontes'}, já {'resumida' if total == 1 else 'resumidas'} para você
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
        p = card["published_at"]
        if p.tzinfo:  # o banco devolve em UTC; o leitor está no Brasil
            p = p.astimezone(FUSO_BR)
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


def montar_email_html(cards_por_categoria: dict, data: date, foto=None) -> str:
    """cards_por_categoria: {categoria: [card, ...]} na ordem das seções.
    card: title, url, fonte, fonte_url, image_url, published_at, resumo.
    foto: a foto do dia (envio/foto_do_dia.py) ou None."""
    cards = [c for itens in cards_por_categoria.values() for c in itens]
    total = len(cards)
    fontes = len({c.get("fonte") or _host(c["url"]) for c in cards})

    corpo = []
    for categoria, itens in cards_por_categoria.items():
        corpo.append(_secao(categoria))
        corpo.extend(_noticia(c, i == len(itens) - 1) for i, c in enumerate(itens))

    # texto que aparece na prévia da caixa de entrada (fica escondido no corpo)
    previa = _esc(" · ".join(c["title"] for c in cards[:3]))

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
          {_capa(foto, data, total, fontes)}
          {''.join(corpo)}
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr><td style="padding: 44px 0 0; border-top: 1px solid {LINHA};">
              <p style="margin: 0 0 6px; font-family: {FONTE}; font-size: 11px; line-height: 1.7; color: {CINZA};">
                Você recebe este resumo porque segue fontes no Feed de Notícias.
              </p>
              <p style="margin: 0; font-family: {FONTE}; font-size: 11px; line-height: 1.7; color: {CINZA};">
                <a href="{HUB_URL}" style="color: {PRETO}; font-weight: 700; text-decoration: none;">Abrir o Feed de Notícias</a>
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
