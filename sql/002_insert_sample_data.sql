-- ============================================================
-- 002_insert_sample_data.sql
-- Primeiro INSERT manual: um tópico e uma fonte de teste.
-- Troque 'SEU_USER_ID_AQUI' pelo UUID copiado em
-- Authentication > Users no painel do Supabase.
-- ============================================================

-- 1) Cria um tópico.
--    "returning id" faz o Postgres devolver o id gerado, pra você
--    já ver na hora qual UUID foi criado (senão o insert não retorna nada).
insert into topics (user_id, name)
values ('SEU_USER_ID_AQUI', 'Inteligência Artificial')
returning id, name, created_at;

-- 2) Cria uma fonte para esse tópico.
--    Em vez de copiar manualmente o id do passo 1, usamos uma
--    subquery: "pega o id do tópico cujo nome é X". Isso evita
--    erro de digitação ao colar um UUID e é uma técnica que você
--    vai reusar bastante.
insert into sources (topic_id, url, type)
values (
    (select id from topics where name = 'Inteligência Artificial' limit 1),
    'https://www.technologyreview.com/feed/',
    'rss'
)
returning id, topic_id, url, type;

-- 3) Confere o resultado juntando as duas tabelas (join).
select
    topics.name as topico,
    sources.url as fonte,
    sources.type as tipo
from topics
join sources on sources.topic_id = topics.id;
