"""
Monta e envia o resumo diário de cada usuário, no horário que ele
escolheu (Configurações > Resumo diário no hub, tabela digest_settings,
sql/024). Roda de hora em hora (workflow "Resumo diário").

Pra cada usuário com o resumo ligado e cujo horário já chegou hoje
(horário de Brasília), e que ainda não recebeu o de hoje:
  1. pega os artigos já resumidos pela IA nas últimas 24h, só das
     coleções escolhidas (ou de todas);
  2. monta o HTML (resumo/template.py) e salva em `digests`;
  3. envia via Resend pro e-mail do usuário + a lista de digest_recipients;
  4. marca `digests.sent_at`.

"Já chegou" em vez de "é exatamente a hora": o agendamento do GitHub às
vezes atrasa, e um atraso não pode fazer alguém perder o resumo do dia.

IMPORTANTE: enquanto o remetente for `onboarding@resend.dev` (sem domínio
verificado), o Resend só entrega pro e-mail da PRÓPRIA conta Resend. Por
isso FEED_TO_EMAIL continua valendo como destinatário principal do
FEED_USER_ID (se estiver definido).

Uso (de dentro de envio/):
    python enviar.py                       # envia pra quem está no horário
    python enviar.py --usuario <uuid> --forcar   # testa com um usuário, ignorando horário
    python enviar.py --simular             # monta e mostra, sem salvar nem enviar
"""
import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import resend
from psycopg2.extras import RealDictCursor
from resend.exceptions import ResendError

from db import get_connection

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "resumo"))
from template import montar_email_html  # noqa: E402

FROM_ADDRESS = "Feed de Notícias <onboarding@resend.dev>"
FUSO = ZoneInfo("America/Sao_Paulo")
CATEGORIAS = [
    "Tecnologia", "Finanças", "Humor", "Política", "Ciência",
    "Saúde", "Esportes", "Entretenimento", "Mundo", "Outros",
]


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


def artigos_do_resumo(conn, user_id, topic_ids):
    """Artigos já resumidos pela IA nas últimas 24h, das coleções escolhidas."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            select a.title, a.url, a.author, a.published_at,
                   a.ai_summary as resumo, a.category as categoria
            from articles a
            join sources s on s.id = a.source_id
            join topics t on t.id = s.topic_id
            where t.user_id = %(user_id)s
              and a.ai_summary is not null
              and a.collected_at > now() - interval '24 hours'
              and (%(topic_ids)s::uuid[] is null or t.id = any(%(topic_ids)s::uuid[]))
            order by a.published_at desc nulls last
            """,
            {"user_id": user_id, "topic_ids": topic_ids},
        )
        return cur.fetchall()


def agrupar_por_categoria(cards):
    grupos = {categoria: [] for categoria in CATEGORIAS}
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
    principal = usuario["email"]
    if os.environ.get("FEED_USER_ID") == str(usuario["id"]) and os.environ.get("FEED_TO_EMAIL"):
        principal = os.environ["FEED_TO_EMAIL"]
    with conn.cursor() as cur:
        cur.execute("select email from digest_recipients where user_id = %s", (usuario["id"],))
        extras = [linha[0] for linha in cur.fetchall()]
    return list(dict.fromkeys([principal, *extras]))


def marcar_como_enviado(conn, digest_id):
    with conn.cursor() as cur:
        cur.execute("update digests set sent_at = now() where id = %s", (digest_id,))
    conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--usuario", help="só este usuário (uuid)")
    parser.add_argument("--forcar", action="store_true", help="ignora o horário escolhido")
    parser.add_argument("--simular", action="store_true", help="monta e mostra, sem salvar nem enviar")
    args = parser.parse_args()

    agora = datetime.now(FUSO)
    if not args.simular:
        resend.api_key = os.environ["RESEND_API_KEY"]

    conn = get_connection()
    try:
        usuarios = usuarios_no_horario(conn, agora, args.forcar, args.usuario)
        conn.commit()
        print(f"{agora:%d/%m %H:%M} (Brasília): {len(usuarios)} usuário(s) com resumo pra enviar.")

        for usuario in usuarios:
            artigos = artigos_do_resumo(conn, usuario["id"], usuario["topic_ids"])
            print(f"- {usuario['email']} ({usuario['hora_envio']}h): {len(artigos)} artigo(s)")
            if not artigos:
                print("  nada novo nas últimas 24h, pulando (sem e-mail vazio)")
                continue

            html = montar_email_html(agrupar_por_categoria(artigos), agora.date())
            para = destinatarios(conn, usuario)
            conn.commit()  # leituras feitas: não segura transação durante o envio
            if args.simular:
                print(f"  simulação: enviaria pra {para}")
                continue

            digest_id = salvar_digest(conn, usuario["id"], agora.date(), html)
            try:
                resend.Emails.send({"from": FROM_ADDRESS, "to": para, "subject": "Seu resumo diário", "html": html})
            except ResendError as erro:
                # não marca como enviado: a próxima rodada (daqui a 1h) tenta de novo
                print(f"  erro ao enviar: {erro}")
                continue
            marcar_como_enviado(conn, digest_id)
            print(f"  enviado pra {len(para)} destinatário(s)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
