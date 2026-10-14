"""
Monta e envia o resumo diário de cada usuário, no horário que ele
escolheu (Configurações > Resumo diário no hub, tabela digest_settings,
sql/024). Roda de hora em hora (workflow "Resumo diário").

Pra cada usuário com o resumo ligado e cujo horário já chegou hoje
(horário de Brasília), e que ainda não recebeu o de hoje:
  1. pega as notícias que chegaram nas últimas 12 horas, só das coleções
     escolhidas (ou de todas), das mais recentes pras mais antigas;
  2. ordena por relevância, sem IA (sql/044): primeiro as histórias que
     mais sites estão cobrindo (agrupar.py), depois as mais recentes, uma
     notícia por história. Separa as 10 primeiras com texto (notícias
     completas), 5 manchetes do resto (só título e link) e conta o que
     sobrou (vira um link pro hub). Assim o e-mail tem sempre o mesmo
     tamanho, siga a pessoa 5 ou 50 fontes;
  2b. a IA (Gemini) entra só aqui: resume essas 10 que ainda não têm
     resumo (o resumo fica guardado). Sem crédito ou sem chave, o e-mail
     sai com o começo do texto;
  3. monta o HTML (resumo/template.py) e salva em `digests`;
  4. envia pelo Resend, do domínio do projeto (resumo@dailypaper.news),
     pro e-mail do usuário + a lista de digest_recipients: um e-mail por
     destinatário, pra ninguém ver o endereço dos outros;
  5. marca `digests.sent_at`.

"Já chegou" em vez de "é exatamente a hora": o agendamento do GitHub às
vezes atrasa, e um atraso não pode fazer alguém perder o resumo do dia.

Uso (de dentro de envio/):
    python enviar.py                       # envia pra quem está no horário
    python enviar.py --usuario <uuid> --forcar   # testa com um usuário, ignorando horário
    python enviar.py --simular             # monta e mostra, sem salvar nem enviar
"""
import argparse
import os
import sys
import time
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import resend
from psycopg2.extras import RealDictCursor
from resend.exceptions import ResendError

from db import get_connection
from foto_do_dia import foto_do_dia

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "resumo"))
from template import data_extenso, montar_email_html  # noqa: E402

FROM_ADDRESS = "Daily Paper <resumo@dailypaper.news>"
# Respostas ao resumo vão pro Gmail do projeto (o domínio ainda não recebe
# e-mail; quando receber, vira contato@dailypaper.news)
RESPONDER_PARA = "feeddailypaper@gmail.com"
# O Resend aceita poucas requisições por segundo: uma pausa entre envios
PAUSA_ENTRE_ENVIOS = 0.6
FUSO = ZoneInfo("America/Sao_Paulo")
MAX_COMPLETAS = 10        # notícias com resumo da IA, as mais relevantes
TEXTO_PRA_RESUMIR = 400   # menos que isso não dá resumo (é só a chamada do feed)
TRECHO_SEM_IA = 450       # sem a IA, o e-mail mostra o começo do texto até aqui
MAX_MANCHETES = 5         # do resto, só título e link
# Uma fonte que publica muito não ocupa o e-mail todo (em 07/10, 8 das 10
# mais recentes eram do Diário do Comércio). Se faltar variedade, completa
# com as mais recentes de qualquer fonte.
MAX_COMPLETAS_POR_FONTE = 3
MAX_MANCHETES_POR_FONTE = 2
# Quem segue muitos sites de um assunto (celebridades, por exemplo) veria
# o e-mail inteiro dele, porque esses sites repetem as mesmas histórias e
# a cobertura sobe. No máximo 3 completas por categoria.
MAX_COMPLETAS_POR_CATEGORIA = 3
# Pelo Google Notícias vêm também páginas que não são notícia (o
# AdoroCinema manda páginas de celebridade: "Milo Quifes"). Manchete sem
# resumo precisa de pelo menos isso de palavras pra entrar no e-mail.
MIN_PALAVRAS_MANCHETE = 4
JANELA_HORAS = 12


def usuarios_no_horario(conn, agora, forcar=False, usuario=None):
    """Usuários com resumo ligado, horário já alcançado e sem envio hoje.
    Sem linha em digest_settings = padrão (ligado, 6h, todas)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            select u.id, u.email,
                   coalesce(c.hora_envio, 6) as hora_envio,
                   c.topic_ids
            from auth.users u
            left join digest_settings c on c.user_id = u.id
            where coalesce(c.ativo, true)
              and (%(usuario)s::uuid is null or u.id = %(usuario)s::uuid)
              and (%(forcar)s or coalesce(c.hora_envio, 6) <= %(hora)s)
              and not exists (
                  select 1 from digests d
                  where d.user_id = u.id and d.digest_date = %(hoje)s and d.sent_at is not null
              )
            """,
            {"usuario": usuario, "forcar": forcar, "hora": agora.hour, "hoje": agora.date()},
        )
        return cur.fetchall()


def inicio_do_periodo(agora):
    """O resumo traz as notícias das últimas JANELA_HORAS horas (envio às
    7h -> o que chegou desde as 19h de ontem): o e-mail fica com o que é
    recente de verdade, e o número do e-mail conta só isso."""
    return agora - timedelta(hours=JANELA_HORAS)


def noticias_do_periodo(conn, user_id, topic_ids, desde):
    """Notícias que chegaram desde `desde`, das coleções escolhidas, com a
    cobertura da história (quantos sites; 1 = notícia avulsa)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            select a.id, a.title, a.url, a.published_at, a.image_url, a.content,
                   coalesce(a.published_at, a.collected_at) as quando,
                   coalesce(s.name, '') as fonte, s.url as fonte_url,
                   a.ai_summary as resumo, a.category as categoria,
                   a.historia_id, coalesce(h.fontes, 1) as cobertura
            from articles a
            join sources s on s.feed_id = a.feed_id
            join topics t on t.id = s.topic_id
            left join historias h on h.id = a.historia_id
            where t.user_id = %(user_id)s
              and a.collected_at >= %(desde)s
              and (%(topic_ids)s::uuid[] is null or t.id = any(%(topic_ids)s::uuid[]))
            order by coalesce(a.published_at, a.collected_at) desc
            """,
            {"user_id": user_id, "topic_ids": topic_ids, "desde": desde},
        )
        return cur.fetchall()


def _primeiras(lista, limite, por_fonte, por_categoria=None):
    """As `limite` primeiras de `lista` (já na ordem de relevância), no
    máximo `por_fonte` de cada fonte (e `por_categoria` de cada categoria);
    se faltar variedade, completa com as próximas que sobraram. Mantém a
    ordem."""
    indices, fontes, categorias = [], Counter(), Counter()
    for i, n in enumerate(lista):
        if len(indices) == limite:
            break
        categoria = n.get("categoria") or "Outros"
        if fontes[n["fonte"]] < por_fonte and (por_categoria is None or categorias[categoria] < por_categoria):
            indices.append(i)
            fontes[n["fonte"]] += 1
            categorias[categoria] += 1
    for i in range(len(lista)):
        if len(indices) == limite:
            break
        if i not in indices:
            indices.append(i)
    return [lista[i] for i in sorted(indices)]


def por_relevancia(noticias):
    """Sem IA: as histórias que mais sites estão cobrindo primeiro; na
    mesma cobertura, as mais recentes. Uma notícia por história."""
    ordenadas = sorted(noticias, key=lambda n: (-n["cobertura"], -n["quando"].timestamp()))
    vistas, saida = set(), []
    for n in ordenadas:
        if n["historia_id"]:
            if n["historia_id"] in vistas:
                continue
            vistas.add(n["historia_id"])
        saida.append(n)
    return saida


def separar(noticias):
    """(completas, manchetes, quantas sobraram)."""
    ordenadas = por_relevancia(noticias)
    com_texto = [n for n in ordenadas if n["resumo"] or len(n["content"] or "") >= TEXTO_PRA_RESUMIR]
    completas = _primeiras(com_texto, MAX_COMPLETAS, MAX_COMPLETAS_POR_FONTE, MAX_COMPLETAS_POR_CATEGORIA)
    escolhidas = {id(n) for n in completas}
    resto = [n for n in ordenadas if id(n) not in escolhidas]
    candidatas = [n for n in resto if len(n["title"].split()) >= MIN_PALAVRAS_MANCHETE]
    manchetes = _primeiras(candidatas, MAX_MANCHETES, MAX_MANCHETES_POR_FONTE)
    return completas, manchetes, len(noticias) - len(completas) - len(manchetes)


def trecho(texto):
    """Sem a IA: o começo do texto, até TRECHO_SEM_IA, fechando a frase."""
    texto = " ".join((texto or "").split("\n")[:3]).strip()
    if len(texto) <= TRECHO_SEM_IA:
        return texto
    corte = texto[:TRECHO_SEM_IA]
    fim = max(corte.rfind(". "), corte.rfind("! "), corte.rfind("? "))
    return corte[: fim + 1] if fim > 150 else corte.rsplit(" ", 1)[0] + "…"


def resumir_as_escolhidas(conn, completas, simular=False):
    """A IA só aqui (sql/044): resume, num pedido só, as notícias escolhidas
    pro e-mail que ainda não têm resumo, e guarda o resumo (a mesma notícia
    no e-mail de outra pessoa não paga de novo). Sem chave, sem crédito ou
    com erro, o e-mail sai com o começo do texto."""
    faltando = [n for n in completas if not n["resumo"]]
    if not faltando:
        return 0
    feitos = 0
    if simular:
        print(f"  simulação: a IA resumiria {len(faltando)} notícia(s)")
    elif os.environ.get("GEMINI_API_KEY"):
        try:
            import resumir  # resumo/resumir.py (o caminho já está no sys.path)
            from google import genai

            cliente = genai.Client(http_options={"timeout": resumir.TIMEOUT_REQUISICAO_MS})
            artigos = [{"id": n["id"], "title": n["title"], "content": n["content"]} for n in faltando]
            casados = resumir.casar_resumos(artigos, resumir.resumir_artigos(cliente, "Resumo do dia", artigos))
            resumos = {str(c["id"]): c["resumo"] for c in casados if c["resumo"]}
            with conn.cursor() as cur:
                for id_, resumo in resumos.items():
                    cur.execute("update articles set ai_summary = %s where id = %s", (resumo, id_))
            conn.commit()
            for n in faltando:
                n["resumo"] = resumos.get(str(n["id"]))
            feitos = len(resumos)
        except Exception as erro:
            conn.rollback()
            print(f"  ::warning::IA indisponível ({type(erro).__name__}: {str(erro)[:160]}); vai o começo do texto")
    for n in completas:
        if not n["resumo"]:
            n["resumo"] = trecho(n["content"])
    return feitos


def agrupar_por_categoria(cards):
    """Seções na ordem da notícia mais recente de cada uma (os cards já
    vêm dos mais recentes pros mais antigos)."""
    grupos = {}
    for card in cards:
        grupos.setdefault(card["categoria"] or "Outros", []).append(card)
    return {categoria: itens for categoria, itens in grupos.items() if itens}


def salvar_digest(conn, user_id, dia, html):
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into digests (user_id, digest_date, html_content)
            values (%s, %s, %s)
            on conflict (user_id, digest_date)
            do update set html_content = excluded.html_content
            returning id
            """,
            (user_id, dia, html),
        )
        digest_id = cur.fetchone()[0]
    conn.commit()
    return digest_id


def destinatarios(conn, usuario):
    with conn.cursor() as cur:
        cur.execute("select email from digest_recipients where user_id = %s", (usuario["id"],))
        extras = [linha[0] for linha in cur.fetchall()]
    return list(dict.fromkeys([usuario["email"], *extras]))


def marcar_como_enviado(conn, digest_id):
    with conn.cursor() as cur:
        cur.execute("update digests set sent_at = now() where id = %s", (digest_id,))
    conn.commit()


def enviar_email(para, assunto, html):
    resend.Emails.send({
        "from": FROM_ADDRESS,
        "to": [para],
        "reply_to": RESPONDER_PARA,
        "subject": assunto,
        "html": html,
    })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--usuario", help="só este usuário (uuid)")
    parser.add_argument("--forcar", action="store_true", help="ignora o horário escolhido")
    parser.add_argument("--simular", action="store_true", help="monta e mostra, sem salvar nem enviar")
    args = parser.parse_args()

    agora = datetime.now(FUSO)

    conn = get_connection()
    try:
        usuarios = usuarios_no_horario(conn, agora, args.forcar, args.usuario)
        conn.commit()
        foto = foto_do_dia(conn, agora.date()) if usuarios else None
        print(f"{agora:%d/%m %H:%M} (Brasília): {len(usuarios)} usuário(s) com resumo pra enviar.")

        for usuario in usuarios:
            desde = inicio_do_periodo(agora)
            noticias = noticias_do_periodo(conn, usuario["id"], usuario["topic_ids"], desde)
            completas, manchetes, restantes = separar(noticias)
            print(
                f"- {usuario['email']} ({usuario['hora_envio']}h): {len(noticias)} notícia(s) desde "
                f"{desde.astimezone(FUSO):%d/%m %H:%M}; {len(completas)} completa(s), "
                f"{len(manchetes)} manchete(s), {restantes} no link pro hub"
            )
            if not noticias:
                print("  nada novo desde o último resumo, pulando (sem e-mail vazio)")
                continue
            resumidas = resumir_as_escolhidas(conn, completas, args.simular)
            if resumidas:
                print(f"  {resumidas} resumo(s) feitos pela IA agora")

            html = montar_email_html(
                agrupar_por_categoria(completas), agora.date(), foto,
                manchetes=manchetes, restantes=restantes, total=len(noticias), desde=desde,
            )
            para = destinatarios(conn, usuario)
            conn.commit()  # leituras feitas: não segura transação durante o envio
            if args.simular:
                arquivo = Path(__file__).parent / f"previa-{usuario['id']}.html"
                arquivo.write_text(html, encoding="utf-8")
                print(f"  simulação: enviaria pra {para}; prévia em {arquivo.name}")
                continue

            digest_id = salvar_digest(conn, usuario["id"], agora.date(), html)
            resend.api_key = os.environ["RESEND_API_KEY"]
            enviados = 0
            for destino in para:
                try:
                    enviar_email(destino, f"Seu resumo de {data_extenso(agora.date())}", html)
                    enviados += 1
                except (ResendError, OSError) as erro:
                    print(f"  erro ao enviar pra {destino}: {erro}")
                time.sleep(PAUSA_ENTRE_ENVIOS)
            if not enviados:
                # não marca como enviado: a próxima rodada (daqui a 1h) tenta de novo
                continue
            marcar_como_enviado(conn, digest_id)
            print(f"  enviado pra {enviados} de {len(para)} destinatário(s)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
