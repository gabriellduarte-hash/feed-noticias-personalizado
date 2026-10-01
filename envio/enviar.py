"""
Pega o digest de hoje (ainda não enviado) e dispara por e-mail via
Resend, pro dono (FEED_TO_EMAIL) + quem estiver em `digest_recipients`
(lista de compartilhamento gerenciada em /compartilhar no hub). Marca
`digests.sent_at` depois do envio confirmado — é a coluna que já
existia no schema desde o início, só esperando esta etapa pra ser
usada de verdade.

IMPORTANTE: enquanto o sender for `onboarding@resend.dev` (sem domínio
verificado), o Resend só entrega pro e-mail da PRÓPRIA conta Resend —
destinatários extras em `digest_recipients` não vão receber nada de
verdade até você verificar um domínio em resend.com/domains e trocar
FROM_ADDRESS.
"""
import os

import resend
from psycopg2.extras import RealDictCursor
from resend.exceptions import ResendError

from db import get_connection

# onboarding@resend.dev só funciona em modo de teste (sem domínio
# verificado) e só entrega pro e-mail da própria conta Resend. Depois
# de verificar um domínio em resend.com/domains, troque por um
# endereço do seu domínio (ex.: feed@seudominio.com).
FROM_ADDRESS = "Feed de Notícias <onboarding@resend.dev>"


def buscar_digest_pendente(conn, user_id):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            select id, html_content
            from digests
            where user_id = %s and digest_date = current_date and sent_at is null
            """,
            (user_id,),
        )
        return cur.fetchone()


def buscar_destinatarios_extras(conn, user_id):
    with conn.cursor() as cur:
        cur.execute("select email from digest_recipients where user_id = %s", (user_id,))
        return [linha[0] for linha in cur.fetchall()]


def marcar_como_enviado(conn, digest_id):
    with conn.cursor() as cur:
        cur.execute("update digests set sent_at = now() where id = %s", (digest_id,))
    conn.commit()


def main():
    resend.api_key = os.environ["RESEND_API_KEY"]
    destinatario = os.environ["FEED_TO_EMAIL"]
    user_id = os.environ["FEED_USER_ID"]

    conn = get_connection()
    try:
        digest = buscar_digest_pendente(conn, user_id)
        if digest is None:
            print("Nenhum digest pendente de hoje (já foi enviado, ou resumir.py ainda não rodou hoje).")
            return

        destinatarios = [destinatario] + buscar_destinatarios_extras(conn, user_id)

        try:
            resposta = resend.Emails.send({
                "from": FROM_ADDRESS,
                "to": destinatarios,
                "subject": "Seu resumo diário",
                "html": digest["html_content"],
            })
        except ResendError as erro:
            print(f"Erro ao enviar e-mail: {erro}")
            return

        print(f"E-mail enviado pra {len(destinatarios)} destinatário(s): {resposta}")
        marcar_como_enviado(conn, digest["id"])
        print("`digests.sent_at` atualizado.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
