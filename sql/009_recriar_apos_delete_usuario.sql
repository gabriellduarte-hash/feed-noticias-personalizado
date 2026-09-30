-- ============================================================
-- 009_recriar_apos_delete_usuario.sql
-- Recria tópico + fontes depois que a exclusão de um usuário em
-- Authentication > Users cascateou e zerou topics/sources/articles/
-- digests. Usa o UUID novo (a conta que você loga no hub):
-- 0528872b-cf56-4b5d-baa3-367c6f37a582
-- ============================================================

insert into topics (user_id, name)
values ('0528872b-cf56-4b5d-baa3-367c6f37a582', 'Inteligência Artificial')
returning id, name, created_at;

insert into sources (topic_id, url, type)
values (
    (select id from topics where name = 'Inteligência Artificial' limit 1),
    'https://www.technologyreview.com/feed/',
    'rss'
)
returning id, topic_id, url, type;

insert into sources (topic_id, url, type)
values (
    (select id from topics where name = 'Inteligência Artificial' limit 1),
    'https://pt.wikipedia.org/wiki/Inteligência_artificial',
    'scrape'
)
returning id, topic_id, url, type;

-- Confere
select topics.name as topico, sources.url as fonte, sources.type as tipo
from topics
join sources on sources.topic_id = topics.id;
