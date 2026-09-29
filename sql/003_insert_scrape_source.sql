-- ============================================================
-- 003_insert_scrape_source.sql
-- Cadastra uma segunda fonte, do tipo 'scrape' (sem RSS), pra
-- testar o caminho de fallback do coletor (trafilatura).
-- ============================================================

insert into sources (topic_id, url, type)
values (
    (select id from topics where name = 'Inteligência Artificial' limit 1),
    'https://pt.wikipedia.org/wiki/Inteligência_artificial',
    'scrape'
)
returning id, topic_id, url, type;

-- Confere: agora devem aparecer 2 fontes para o mesmo tópico.
select topics.name as topico, sources.url as fonte, sources.type as tipo
from topics
join sources on sources.topic_id = topics.id;
