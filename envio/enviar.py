"""
Monta e envia o resumo diário de cada usuário, no horário que ele
escolheu (Configurações > Resumo diário no hub, tabela digest_settings,
sql/024). Roda de hora em hora (workflow "Resumo diário").

Pra cada usuário com o resumo ligado e cujo horário já chegou hoje
(horário de Brasília), e que ainda não recebeu o de hoje:
  1. pega as notícias que chegaram desde o último resumo (ou, se não
     houve um ontem, desde ontem no horário escolhido), só das coleções
     escolhidas (ou de todas), das mais recentes pras mais antigas;
  2. separa as 10 mais recentes com resumo da IA (notícias completas), 5
     manchetes do resto (só título e link) e conta o que sobrou (vira um
     link pro hub). Assim o e-mail tem sempre o mesmo tamanho, siga a
     pessoa 5 ou 50 fontes;
  3. monta o HTML (resumo/template.py) e salva em `digests`;
  4. envia via Resend pro e-mail do usuário + a lista de digest_recipients;
  5. marca `digests.sent_at`.

"Já chegou" em vez de "é exatamente a hora": o agendamento do GitHub às
vezes atrasa, e um atraso não pode fazer alguém perder o resumo do dia.

Como envia (um e-mail por destinatário, pra ninguém ver o endereço dos
outros):
  - SMTP, se SMTP_USER e SMTP_PASSWORD estiverem definidos: no período de
    testes, o Gmail do projeto com uma senha de app. Envia como esse
    Gmail, pra qualquer pessoa. Tenta a porta 465 e, se ela falhar, a 587.
    Se o SMTP não abrir de jeito nenhum, a rodada envia pelo Resend (com
    um aviso no log do GitHub), pra o resumo não se perder.
  - senão, Resend. Enquanto o remetente for `onboarding@resend.dev` (sem
    domínio verificado), o Resend só entrega pro e-mail da PRÓPRIA conta
    Resend. Por isso FEED_TO_EMAIL continua valendo como destinatário
    principal do FEED_USER_ID (se estiver definido).

Uso (de dentro de envio/):
    python enviar.py                       # envia pra quem está no horário
    python enviar.py --usuario <uuid> --forcar   # testa com um usuário, ignorando horário
    python enviar.py --simular             # monta e mostra, sem salvar nem enviar
"""
import argparse
import os
import smtplib
import sys
from email.message import EmailMessage
from email.utils import formataddr
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

FROM_ADDRESS = "Daily Paper <onboarding@resend.dev>"
FUSO = ZoneInfo("America/Sao_Paulo")
MAX_COMPLETAS = 10        # notícias com resumo da IA, as mais recentes
MAX_MANCHETES = 5         # do resto, só título e link
# Uma fonte que publica muito não ocupa o e-mail todo (em 07/10, 8 das 10
# mais recentes eram do Diário do Comércio). Se faltar variedade, completa
# com as mais recentes de qualquer fonte.
MAX_COMPLETAS_POR_FONTE = 3
MAX_MANCHETES_POR_FONTE = 2
# Pelo Google Notícias vêm também páginas que não são notícia (o
# AdoroCinema manda páginas de celebridade: "Milo Quifes"). Manchete sem
# resumo precisa de pelo menos isso de palavras pra entrar no e-mail.
MIN_PALAVRAS_MANCHETE = 4


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


def inicio_do_periodo(conn, usuario, agora):
    """Desde quando entram notícias: o último resumo enviado ou, se não
    houve um desde ontem, ontem no horário escolhido (envio às 7h ->
    notícias que chegaram desde as 7h de ontem)."""
    ontem_no_horario = (agora - timedelta(days=1)).replace(
        hour=usuario["hora_envio"], minute=0, second=0, microsecond=0
    )
    with conn.cursor() as cur:
        cur.execute(
            "select max(sent_at) from digests where user_id = %s and sent_at is not null",
            (usuario["id"],),
        )
        ultimo = cur.fetchone()[0]
    return max(ultimo, ontem_no_horario) if ultimo else ontem_no_horario


def noticias_do_periodo(conn, user_id, topic_ids, desde):
    """Notícias que chegaram desde `desde`, das coleções escolhidas, mais
    recentes primeiro. Com ou sem resumo: as sem resumo viram manchete."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            select a.title, a.url, a.published_at, a.image_url,
                   coalesce(s.name, '') as fonte, s.url as fonte_url,
                   a.ai_summary as resumo, a.category as categoria
            from articles a
            join sources s on s.id = a.source_id
            join topics t on t.id = s.topic_id
            where t.user_id = %(user_id)s
              and a.collected_at >= %(desde)s
              and (%(topic_ids)s::uuid[] is null or t.id = any(%(topic_ids)s::uuid[]))
            order by coalesce(a.published_at, a.collected_at) desc
            """,
            {"user_id": user_id, "topic_ids": topic_ids, "desde": desde},
        )
        return cur.fetchall()


def _mais_recentes(lista, limite, por_fonte):
    """As `limite` primeiras de `lista` (já das mais recentes pras mais
    antigas), no máximo `por_fonte` de cada fonte; se faltar variedade,
    completa com as mais recentes que sobraram. Mantém a ordem."""
    indices, contagem = [], Counter()
    for i, n in enumerate(lista):
        if len(indices) == limite:
            break
        if contagem[n["fonte"]] < por_fonte:
            indices.append(i)
            contagem[n["fonte"]] += 1
    for i in range(len(lista)):
        if len(indices) == limite:
            break
        if i not in indices:
            indices.append(i)
    return [lista[i] for i in sorted(indices)]


def separar(noticias):
    """(completas, manchetes, quantas sobraram). `noticias` já vem das
    mais recentes pras mais antigas."""
    completas = _mais_recentes([n for n in noticias if n["resumo"]], MAX_COMPLETAS, MAX_COMPLETAS_POR_FONTE)
    escolhidas = {id(n) for n in completas}
    resto = [n for n in noticias if id(n) not in escolhidas]
    candidatas = [n for n in resto if n["resumo"] or len(n["title"].split()) >= MIN_PALAVRAS_MANCHETE]
    manchetes = _mais_recentes(candidatas, MAX_MANCHETES, MAX_MANCHETES_POR_FONTE)
    return completas, manchetes, len(resto) - len(manchetes)


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


class Remetente:
    """Abre o SMTP (ou prepara o Resend) uma vez e envia um por um."""

    def __init__(self):
        self.usuario = os.environ.get("SMTP_USER", "").strip()
        self.senha = "".join(os.environ.get("SMTP_PASSWORD", "").split())  # a senha de app do Google vem com espaços
        self.host = os.environ.get("SMTP_HOST", "").strip() or "smtp.gmail.com"
        self.smtp = None
        if self.usuario and self.senha:
            try:
                self.conectar()
            except (smtplib.SMTPException, OSError) as erro:
                # ::warning:: vira um aviso amarelo na página da execução no GitHub
                print(f"::warning::SMTP indisponível ({type(erro).__name__}: {erro}); esta rodada envia pelo Resend")
        if not self.smtp:
            resend.api_key = os.environ["RESEND_API_KEY"]

    def conectar(self):
        """Porta 465 (SSL) e, se ela falhar, 587 (STARTTLS). O log diz em
        que passo parou. Senha recusada não tenta a outra porta."""
        ultimo_erro = None
        for porta in (465, 587):
            smtp, passo = None, "conectar"
            try:
                if porta == 465:
                    smtp = smtplib.SMTP_SSL(self.host, porta, timeout=30)
                else:
                    smtp = smtplib.SMTP(self.host, porta, timeout=30)
                    passo = "starttls"
                    smtp.starttls()
                passo = "login"
                smtp.login(self.usuario, self.senha)
                print(f"SMTP: conectado em {self.host}:{porta} como {self.usuario}")
                self.smtp = smtp
                return
            except (smtplib.SMTPException, OSError) as erro:
                print(f"SMTP: falhou em {self.host}:{porta}, no passo '{passo}': {type(erro).__name__}: {erro}")
                if smtp:
                    smtp.close()
                if isinstance(erro, smtplib.SMTPAuthenticationError):
                    raise
                ultimo_erro = erro
        raise ultimo_erro

    def enviar(self, para, assunto, html):
        if not self.smtp:
            resend.Emails.send({"from": FROM_ADDRESS, "to": [para], "subject": assunto, "html": html})
            return
        mensagem = EmailMessage()
        mensagem["From"] = formataddr(("Daily Paper", self.usuario))
        mensagem["To"] = para
        mensagem["Subject"] = assunto
        mensagem.set_content("Seu resumo do dia está em HTML. Abra este e-mail num app que mostre HTML.")
        mensagem.add_alternative(html, subtype="html")
        try:
            self.smtp.send_message(mensagem)
        except smtplib.SMTPServerDisconnected:
            # o Gmail fecha conexão parada: reconecta uma vez e tenta de novo
            self.conectar()
            self.smtp.send_message(mensagem)

    def fechar(self):
        if self.smtp:
            try:
                self.smtp.quit()
            except (smtplib.SMTPException, OSError):
                pass  # a conexão já tinha caído; o que foi enviado já está no log


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--usuario", help="só este usuário (uuid)")
    parser.add_argument("--forcar", action="store_true", help="ignora o horário escolhido")
    parser.add_argument("--simular", action="store_true", help="monta e mostra, sem salvar nem enviar")
    args = parser.parse_args()

    agora = datetime.now(FUSO)
    remetente = None

    conn = get_connection()
    try:
        usuarios = usuarios_no_horario(conn, agora, args.forcar, args.usuario)
        conn.commit()
        foto = foto_do_dia(conn, agora.date()) if usuarios else None
        print(f"{agora:%d/%m %H:%M} (Brasília): {len(usuarios)} usuário(s) com resumo pra enviar.")

        for usuario in usuarios:
            desde = inicio_do_periodo(conn, usuario, agora)
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
            remetente = remetente or Remetente()
            enviados = 0
            for destino in para:
                try:
                    remetente.enviar(destino, f"Seu resumo de {data_extenso(agora.date())}", html)
                    enviados += 1
                except (ResendError, smtplib.SMTPException, OSError) as erro:
                    print(f"  erro ao enviar pra {destino}: {erro}")
            if not enviados:
                # não marca como enviado: a próxima rodada (daqui a 1h) tenta de novo
                continue
            marcar_como_enviado(conn, digest_id)
            print(f"  enviado pra {enviados} de {len(para)} destinatário(s)")
    finally:
        if remetente:
            remetente.fechar()
        conn.close()


if __name__ == "__main__":
    main()
