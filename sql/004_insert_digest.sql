-- ============================================================
-- 004_insert_digest.sql
-- Salva o resumo diário gerado pelo resumo/resumir.py na tabela
-- `digests`. Troque 'SEU_USER_ID_AQUI' pelo mesmo UUID usado em
-- sql/002_insert_sample_data.sql.
-- ============================================================

insert into digests (user_id, digest_date, html_content)
values (
    'SEU_USER_ID_AQUI',
    current_date,
    $$<h2>Inteligência Artificial</h2>
<p>Uma investigação da <em>MIT Technology Review</em> revelou graves falhas no "muro virtual" de vigilância instalado na fronteira dos Estados Unidos: mesmo com o uso de torres equipadas com inteligência artificial, centenas de pessoas cruzaram áreas monitoradas sem serem detectadas e acabaram morrendo nas proximidades sem assistência. Paralelamente, especialistas alertam para o excesso de alarde e promessas exageradas (<em>hype</em>) na indústria, chamando a atenção para incidentes de segurança e invasões que envolveram modelos de empresas como OpenAI, Anthropic e Meta.</p>
<p>Além das preocupações com a eficácia prática e a segurança cibernética dos sistemas atuais, o setor continua a dividir opiniões sobre riscos extremos, impulsionando debates sobre a possibilidade real de a IA representar ameaças de armas biológicas ou até mesmo perigos existenciais para a humanidade.</p>$$
)
returning id, digest_date, created_at;

-- Confere o resultado:
select user_id, digest_date, sent_at, created_at from digests;

-- Curiosidade pra testar depois: rode o insert de novo (mesmo user_id,
-- mesma digest_date = hoje) e veja o erro de "unique constraint" —
-- é a regra unique(user_id, digest_date) que criamos lá no schema,
-- impedindo dois resumos pro mesmo dia.
