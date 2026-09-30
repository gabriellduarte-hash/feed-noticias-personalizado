-- ============================================================
-- 012_fonte_g1_teste_imagem.sql
-- Fonte de teste pra validar a extração de capa (o G1 expõe
-- media_content com medium=image, diferente das 2 fontes atuais).
-- ============================================================

insert into sources (topic_id, url, type)
values (
    (select id from topics where name = 'Inteligência Artificial' limit 1),
    'https://g1.globo.com/rss/g1/brasil/',
    'rss'
)
returning id, topic_id, url, type;
