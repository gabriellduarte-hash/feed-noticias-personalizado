-- ============================================================
-- 021_fontes_sitemap.sql
-- Fontes sem RSS: o coletor passa a ler também o "sitemap de notícias"
-- (o arquivo XML que os sites publicam pro Google Notícias, com link,
-- título e data de cada matéria recente).
--
-- A outra alternativa, o RSS de busca do Google Notícias
-- (news.google.com/rss/search?q=site:...), já é um RSS comum, então
-- entra como 'rss' mesmo e não precisa de nada no banco.
-- ============================================================

-- 1) sources.type ganha 'sitemap'. Check constraint não tem "alter":
--    apaga e cria de novo com a lista nova (nome conferido em
--    pg_constraint: sources_type_check).
alter table sources drop constraint sources_type_check;
alter table sources add constraint sources_type_check
  check (type in ('rss', 'scrape', 'sitemap'));

-- 2) feed_catalog passa a dizer como cada fonte é lida. Tudo o que já
--    está lá é RSS, por isso o default 'rss' serve pras linhas antigas.
alter table feed_catalog add column kind text not null default 'rss'
  check (kind in ('rss', 'sitemap'));
