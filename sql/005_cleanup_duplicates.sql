-- ============================================================
-- 005_cleanup_duplicates.sql
-- Remove o tópico e as fontes duplicadas criadas em 28/09 por engano
-- (o "sumiço de dados" foi falso alarme — leitura errada minha, não
-- perda real). Confirmado: nenhum artigo está preso a essas linhas,
-- é seguro apagar.
-- ============================================================

-- Fontes duplicadas (mesma URL, mesmo tópico original, sem nenhum artigo ligado)
delete from sources where id in (
    '891f0ff3-1f36-4cac-a74e-24954badaaa5',  -- rss duplicada
    'a198a051-bab0-495b-9de5-8352778a8a62'   -- scrape duplicada
);

-- Tópico duplicado (órfão — nenhuma fonte aponta pra ele depois do delete acima)
delete from topics where id = '06bb1dac-4f84-469a-a790-474b88c3b21c';

-- Confere: deve sobrar 1 tópico, 2 fontes, e os 21 artigos intactos
select
    (select count(*) from topics) as topicos,
    (select count(*) from sources) as fontes,
    (select count(*) from articles) as artigos;
