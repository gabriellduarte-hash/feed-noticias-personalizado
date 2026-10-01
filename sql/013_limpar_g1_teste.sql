-- ============================================================
-- 013_limpar_g1_teste.sql
-- Apaga os artigos do G1 que já foram salvos com HTML cru no
-- content (antes da correção), pra recoletar limpos.
-- ============================================================

delete from articles
where source_id = (select id from sources where url = 'https://g1.globo.com/rss/g1/brasil/');
