"""Monta o HTML final do e-mail: um feed de cards, agrupado por
categoria editorial (Tecnologia, Finanças, ...), cada categoria abrindo
uma nova seção.

E-mail HTML é um mundo à parte: a maioria dos clientes (Gmail, Outlook)
ignora <style> no <head> e corta CSS externo, então o seguro é usar
`style="..."` inline em cada tag — sem depender de classes/CSS separado.

Todo texto que vem de fora (título, autor, resumo gerado pela IA) passa
por html.escape antes de entrar no HTML (o Markdown do resumo só vira
<strong>/<em>/citação DEPOIS do escape) — sem isso, um título com "&"
ou um resumo comparando "X < Y" quebraria a página.
"""
import html
import re
from datetime import date

CSS_CONTAINER = "font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px;"
CSS_CABECALHO = "font-size: 13px; color: #888; margin: 0 0 24px;"
CSS_CATEGORIA = (
    "margin: 32px 0 12px; padding-bottom: 6px; font-size: 13px; font-weight: bold; "
    "letter-spacing: 0.5px; text-transform: uppercase; color: #444; "
    "border-bottom: 2px solid #444;"
)
CSS_CARD = "margin: 0 0 20px; padding-bottom: 20px; border-bottom: 1px solid #eee;"
CSS_CARD_TITULO = "margin: 0 0 4px; font-size: 16px; color: #1a1a1a;"
CSS_CARD_META = "margin: 0 0 8px; font-size: 12px; color: #888;"
CSS_CARD_RESUMO = "margin: 0 0 10px; font-size: 14px; line-height: 1.6; color: #333;"
CSS_CITACAO = (
    "margin: 0 0 10px; padding: 2px 0 2px 12px; border-left: 3px solid #6d3ff5; "
    "font-size: 14px; line-height: 1.6; font-style: italic; color: #444;"
)
CSS_CITACAO_AUTOR = "display: block; margin-top: 4px; font-style: normal; font-size: 12px; color: #888;"
CSS_CARD_LINK = "font-size: 13px; color: #0066cc; text-decoration: none; font-weight: bold;"
CSS_RODAPE = "margin-top: 32px; font-size: 12px; color: #888;"


def _formatar_data(dt):
    return dt.strftime("%d/%m/%Y") if dt else "data não informada"


def _inline(texto):
    """Depois do html.escape: **negrito** e *itálico* do resumo da IA."""
    texto = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", texto)
    return re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", texto)


def resumo_para_html(resumo):
    """O resumo vem em Markdown simples (resumo/resumir.py): parágrafos
    separados por linha em branco, **negrito**, e "> citação — Autor".
    Tudo é escapado ANTES de virar tag, então nada que a IA escreva vira
    HTML de verdade. Resumos antigos (texto corrido) viram um parágrafo."""
    blocos = [b.strip() for b in re.split(r"\n\s*\n", resumo.strip()) if b.strip()]
    partes = []
    for bloco in blocos:
        if bloco.startswith(">"):
            texto = " ".join(linha.lstrip("> ").strip() for linha in bloco.splitlines())
            autor = ""
            m = re.match(r"^(.*?)\s+[—–-]\s+([^—–\-]{2,60})$", texto)
            if m:
                texto, autor = m.group(1), m.group(2)
            autor_html = f'<span style="{CSS_CITACAO_AUTOR}">— {html.escape(autor)}</span>' if autor else ""
            partes.append(f'<p style="{CSS_CITACAO}">{_inline(html.escape(texto))}{autor_html}</p>')
        else:
            texto = " ".join(linha.strip() for linha in bloco.splitlines())
            partes.append(f'<p style="{CSS_CARD_RESUMO}">{_inline(html.escape(texto))}</p>')
    return "".join(partes)


def _montar_card(card):
    titulo = html.escape(card["title"])
    url = html.escape(card["url"])
    autor = html.escape(card.get("author") or "autor não informado")
    data_artigo = _formatar_data(card.get("published_at"))
    resumo = resumo_para_html(card["resumo"])

    return f"""<div style="{CSS_CARD}">
  <p style="{CSS_CARD_TITULO}">{titulo}</p>
  <p style="{CSS_CARD_META}">{autor} — {data_artigo}</p>
  {resumo}
  <a href="{url}" style="{CSS_CARD_LINK}">Leia o artigo completo →</a>
</div>"""


def _montar_secao(categoria, cards):
    itens = "".join(_montar_card(card) for card in cards)
    return f'<h2 style="{CSS_CATEGORIA}">{html.escape(categoria)}</h2>{itens}'


def montar_email_html(cards_por_categoria: dict, data: date) -> str:
    """cards_por_categoria: {categoria: [card, ...]}, na ordem em que as
    seções devem aparecer (agrupar_por_categoria já filtra categorias
    vazias e preserva a ordem fixa de CATEGORIAS)."""
    secoes = "".join(
        _montar_secao(categoria, cards)
        for categoria, cards in cards_por_categoria.items()
    )
    data_formatada = data.strftime("%d/%m/%Y")

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<body style="margin: 0; padding: 0; background-color: #f4f4f4;">
  <div style="{CSS_CONTAINER}">
    <p style="{CSS_CABECALHO}">Seu resumo diário — {data_formatada}</p>
    {secoes}
    <p style="{CSS_RODAPE}">Gerado automaticamente pelo Feed de Notícias Personalizado.</p>
  </div>
</body>
</html>"""
