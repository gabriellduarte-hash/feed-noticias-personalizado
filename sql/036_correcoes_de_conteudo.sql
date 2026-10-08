-- ============================================================
-- 036_correcoes_de_conteudo.sql
-- Limpa o que já entrou antes das correções do coletor (08/10).
--
-- 1) AdoroCinema pelo Google Notícias só da seção de notícias: a busca
--    "site:adorocinema.com" trazia páginas de filme, de pessoa e de
--    streaming. No catálogo e em quem já segue.
-- 2) Apaga o que veio pelo Google Notícias e não é notícia: listagens
--    ("... - Página 1246"), "Ver X online" e títulos com menos de 4
--    palavras (nome de pessoa ou de filme). O coletor já filtra isso
--    daqui pra frente (alternativas.eh_noticia_do_google_news). Notícia
--    salva pra ler depois fica.
-- 3) Capas erradas da CNN Brasil: miniaturas de 200px de outra matéria,
--    pegas do meio do texto. Sem capa, o enriquecimento da próxima coleta
--    busca a capa da própria página (og:image).
--
-- Os textos com acento quebrado ("simbÃ³lico", 83 notícias da Folha e da
-- Arkade) não se consertam aqui: rode uma vez, depois do push do coletor,
--   cd coletor && python limpar_textos.py --dias 60
-- (a faxina agora conserta acentos). O hub já mostra certo.
-- ============================================================

set lock_timeout = '5s';

begin;

update feed_catalog
set url = 'https://news.google.com/rss/search?q=site%3Aadorocinema.com/noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419'
where url = 'https://news.google.com/rss/search?q=site%3Aadorocinema.com&hl=pt-BR&gl=BR&ceid=BR:pt-419';

update sources
set url = 'https://news.google.com/rss/search?q=site%3Aadorocinema.com/noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419'
where url = 'https://news.google.com/rss/search?q=site%3Aadorocinema.com&hl=pt-BR&gl=BR&ceid=BR:pt-419';

delete from catalog_articles
where url like 'https://news.google.com/%'
  and (title ~* '(^|\s)(p[áa]gina|page)\s+[0-9]+'
       or title ~* '^(ver|assistir) .* online$'
       or array_length(regexp_split_to_array(btrim(title), '\s+'), 1) < 4);

delete from articles a
where a.url like 'https://news.google.com/%'
  and (a.title ~* '(^|\s)(p[áa]gina|page)\s+[0-9]+'
       or a.title ~* '^(ver|assistir) .* online$'
       or array_length(regexp_split_to_array(btrim(a.title), '\s+'), 1) < 4)
  and not exists (select 1 from saved_articles s where s.article_id = a.id);

update articles set image_url = null, enriquecido_em = null
where image_url ~ 'cnnbrasil.*[?&]w=200';
update catalog_articles set image_url = null, enriquecido_em = null
where image_url ~ 'cnnbrasil.*[?&]w=200';

commit;
