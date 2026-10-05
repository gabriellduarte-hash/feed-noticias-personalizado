-- ============================================================
-- 022_catalogo_2026-10-05.sql
-- Gerado por catalogo/catalogar.py em 05/10/2026 18:15.
-- Cada feed abaixo foi baixado e validado (entradas, títulos, publicação
-- recente nos últimos 45 dias). Revise nomes/descrições antes de rodar.
-- on conflict (url) do nothing: rodar duas vezes não duplica nada.
-- ============================================================

-- kind: 'rss' (inclui o RSS de busca do Google Notícias) ou 'sitemap' (sql/021).

insert into feed_catalog (category, name, url, description, kind) values
    -- via Google Notícias: 17 entradas, última em 04/10/2026
    ('Tecnologia', 'Gizmodo', 'https://news.google.com/rss/search?q=site%3Agizmodo.uol.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss'),
    -- via Google Notícias: 100 entradas, última em 05/10/2026
    ('Tecnologia', 'MacMagazine', 'https://news.google.com/rss/search?q=site%3Amacmagazine.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss'),
    -- via Google Notícias: 59 entradas, última em 03/10/2026
    ('Finanças', 'E-Investidor', 'https://news.google.com/rss/search?q=site%3Aeinvestidor.estadao.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss'),
    -- via Google Notícias: 100 entradas, última em 05/10/2026
    ('Esportes', 'ge', 'https://news.google.com/rss/search?q=site%3Age.globo.com&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss'),
    -- via sitemap de notícias: 30 entradas, última em 05/10/2026
    ('Esportes', 'LANCE!', 'https://www.lance.com.br/sitemap/news/today.xml', null, 'sitemap'),
    -- via Google Notícias: 100 entradas, última em 05/10/2026
    ('Entretenimento', 'AdoroCinema', 'https://news.google.com/rss/search?q=site%3Aadorocinema.com&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss'),
    -- via Google Notícias: 100 entradas, última em 05/10/2026
    ('Entretenimento', 'Jovem Nerd', 'https://news.google.com/rss/search?q=site%3Ajovemnerd.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss'),
    -- via sitemap de notícias: 30 entradas, última em 05/10/2026
    ('Entretenimento', 'Omelete', 'https://www.omelete.com.br/sitemap-news.xml', null, 'sitemap'),
    -- via sitemap de notícias: 30 entradas, última em 05/10/2026
    ('Mundo', 'BBC News Brasil', 'https://www.bbc.com/sitemaps/https-index-com-news.xml#caminho=/portuguese', null, 'sitemap')
on conflict (url) do nothing;
