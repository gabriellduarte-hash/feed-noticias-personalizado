-- ============================================================
-- 051_macmagazine_pelo_rss.sql
-- Pode rodar quando quiser (não depende do push).
--
-- 1) A MacMagazine estava cadastrada pela busca do Google Notícias
--    (site:macmagazine.com.br), que só traz título e link, por isso nunca
--    teve texto. O RSS do próprio site (macmagazine.com.br/feed/) traz a
--    matéria inteira e o robots.txt libera. Troca o endereço no feed, na
--    fonte de quem segue e no catálogo. As notícias que vieram pelo Google
--    nos últimos dias ganham o link direto e o texto quando a mesma
--    manchete chegar pelo RSS (manchetes.py). Se o site barrar o GitHub,
--    o coletor passa a fonte pro Worker sozinho, na primeira coleta.
--
-- 2) Apaga as páginas de tag do WordPress ("Arquivo para iPhone Duo") que
--    a busca do Google trouxe como se fossem notícia (MacMagazine e
--    PAPELPOP). Daqui pra frente o coletor e o hub já descartam.
--    As que alguém salvou ficam.
-- ============================================================

update feeds set url = 'https://macmagazine.com.br/feed/'
where url = 'https://news.google.com/rss/search?q=site%3Amacmagazine.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419';

update sources set url = 'https://macmagazine.com.br/feed/'
where url = 'https://news.google.com/rss/search?q=site%3Amacmagazine.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419';

update feed_catalog set url = 'https://macmagazine.com.br/feed/'
where url = 'https://news.google.com/rss/search?q=site%3Amacmagazine.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419';

delete from articles a
where a.url like 'https://news.google.com/%'
  and a.title ~* '^(arquivos?\s+para|archives?\s+for)\y'
  and not exists (select 1 from saved_articles s where s.article_id = a.id);

delete from catalog_articles
where url like 'https://news.google.com/%'
  and title ~* '^(arquivos?\s+para|archives?\s+for)\y';

-- Conferência: 1, 1 e 1 linha com o endereço novo; 0 páginas de tag
select
  (select count(*) from feeds where url = 'https://macmagazine.com.br/feed/') as feeds,
  (select count(*) from sources where url = 'https://macmagazine.com.br/feed/') as fontes,
  (select count(*) from feed_catalog where url = 'https://macmagazine.com.br/feed/') as catalogo,
  (select count(*) from catalog_articles where title ~* '^(arquivos?\s+para|archives?\s+for)\y') as paginas_de_tag;
