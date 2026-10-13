-- ============================================================
-- 042_nintendo_blast_pelo_hub.sql
-- Rode quando quiser (não depende do push, mas o efeito completo vem com
-- o coletor e o hub desta leva).
--
-- O feed da Nintendo Blast traz só o começo da matéria ("Continue lendo
-- »"), e a página completa não abre pras máquinas do GitHub (o
-- enriquecimento marcava como tentada e o texto ficava cortado). Da
-- Vercel a página abre normal. Então ela passa pro hub, como a ESPN
-- (sql/040), e as notícias cortadas dela voltam pra fila.
--
-- Daqui pra frente o enriquecimento marca sozinho os sites que barram
-- as PÁGINAS (não só o feed), e trata "Continue lendo »" como texto
-- cortado mesmo quando passa de 600 caracteres.
-- ============================================================

set lock_timeout = '5s';

begin;

update feed_catalog set coletar_pelo_hub = true
where url = 'https://www.nintendoblast.com.br/feeds/posts/default';

update feeds set coletar_pelo_hub = true
where url = 'https://www.nintendoblast.com.br/feeds/posts/default';

update articles a set enriquecido_em = null
from feeds f
where f.id = a.feed_id and f.url = 'https://www.nintendoblast.com.br/feeds/posts/default'
  and (a.content is null or length(a.content) < 600
       or a.content ~* '(continue lendo|leia mais|read more|keep reading)\s*(»|›|\.\.\.|…)');

update catalog_articles a set enriquecido_em = null
from feed_catalog f
where f.id = a.catalog_id and f.url = 'https://www.nintendoblast.com.br/feeds/posts/default'
  and (a.content is null or length(a.content) < 600
       or a.content ~* '(continue lendo|leia mais|read more|keep reading)\s*(»|›|\.\.\.|…)');

commit;
