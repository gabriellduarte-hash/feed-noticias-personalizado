-- ============================================================
-- 040_coleta_pelo_hub.sql
-- Rode ANTES de subir o coletor e o hub desta leva.
--
-- Sites abertos que barram as máquinas do GitHub (ESPN Brasil, PLACAR,
-- Adrenaline, IstoÉ Dinheiro): o coletor só conseguia o plano B do
-- Google Notícias, que traz o título e um link do Google, sem texto nem
-- foto. Da Vercel eles respondem. Então:
--   coletar_pelo_hub = true  -> quem coleta e abre as páginas é o hub
--   (/api/coletar-bloqueados), chamado no fim da coleta de hora em hora.
--   O coletor marca sozinho os próximos que barrarem o GitHub.
-- Paywall continua respeitado: página que se declara paga
-- (isAccessibleForFree: false) não tem o texto copiado.
--
-- E a limpeza das notícias repetidas: a mesma história entrou duas vezes
-- no mesmo feed, uma pelo link direto e outra pelo Google. Fica a direta.
-- Daqui pra frente o coletor e o hub não deixam repetir (manchetes.py).
-- ============================================================

set lock_timeout = '5s';

begin;

alter table feeds add column coletar_pelo_hub boolean not null default false;
alter table feed_catalog add column coletar_pelo_hub boolean not null default false;

update feed_catalog set coletar_pelo_hub = true
where url in (
  'https://www.espn.com.br/rss',
  'https://www.placar.com.br/feed',
  'https://www.adrenaline.com.br/feed/',
  'https://istoedinheiro.com.br/feed/rss2'
);

update feeds f set coletar_pelo_hub = true
from feed_catalog c
where c.url = f.url and c.coletar_pelo_hub;

-- Seguir: feed novo que já é conhecido por barrar o GitHub nasce marcado
create or replace function seguir_fonte(p_topic_id uuid, p_url text, p_tipo text default 'rss', p_nome text default null)
returns table (fonte_id uuid, feed uuid, feed_novo boolean)
language plpgsql
security definer
set search_path = public
as $$
declare
  v_feed uuid;
  v_fonte uuid;
begin
  if not exists (select 1 from topics where id = p_topic_id and user_id = auth.uid()) then
    raise exception 'coleção não encontrada';
  end if;

  insert into feeds (url, type, name, coletar_pelo_hub)
  values (
    p_url, coalesce(p_tipo, 'rss'), p_nome,
    coalesce((select c.coletar_pelo_hub from feed_catalog c where c.url = p_url), false)
  )
  on conflict (url) do nothing
  returning id into v_feed;
  feed_novo := v_feed is not null;
  if v_feed is null then
    select id into v_feed from feeds where url = p_url;
  end if;

  insert into sources (topic_id, url, type, name, feed_id)
  values (p_topic_id, p_url, coalesce(p_tipo, 'rss'), p_nome, v_feed)
  returning id into v_fonte;

  fonte_id := v_fonte;
  feed := v_feed;
  return next;
end;
$$;

-- O enriquecimento do GitHub já tinha tentado (e levado 403) nas notícias
-- desses sites: voltam pra fila, agora a do hub
update articles a set enriquecido_em = null
from feeds f
where f.id = a.feed_id and f.coletar_pelo_hub
  and a.url not like 'https://news.google.com/%'
  and (a.content is null or length(a.content) < 600 or a.image_url is null);

update catalog_articles a set enriquecido_em = null
from feed_catalog f
where f.id = a.catalog_id and f.coletar_pelo_hub
  and a.url not like 'https://news.google.com/%'
  and (a.content is null or length(a.content) < 600 or a.image_url is null);

-- Repetidas: mesma regra do coletor/manchetes.py (palavras principais da
-- manchete mais curta quase todas na outra), só entre uma do Google e uma
-- direta do mesmo feed, coletadas com até 3 dias de diferença.
create function pg_temp.palavras(titulo text) returns text[]
language sql immutable as $$
  select coalesce(array_agg(distinct p), '{}')
  from regexp_split_to_table(
         translate(lower(titulo), 'áàâãäéèêëíìîïóòôõöúùûüç', 'aaaaaeeeeiiiiooooouuuuc'),
         '[^a-z0-9]+'
       ) as p
  where length(p) >= 3
    and p not in ('and', 'com', 'das', 'dos', 'for', 'mas', 'nas', 'nos', 'num', 'para', 'pela',
                  'pelo', 'por', 'que', 'sem', 'sob', 'sua', 'seu', 'the', 'uma', 'with')
$$;

create function pg_temp.mesma_manchete(a text, b text) returns boolean
language sql immutable as $$
  with p as (select pg_temp.palavras(a) as pa, pg_temp.palavras(b) as pb)
  select case
    when cardinality(pa) = 0 or cardinality(pb) = 0 then false
    when pa @> pb and pb @> pa then true
    else least(cardinality(pa), cardinality(pb)) >= 5
         and cardinality(array(select unnest(pa) intersect select unnest(pb)))::numeric
             / least(cardinality(pa), cardinality(pb)) >= 0.8
  end
  from p
$$;

delete from articles g
using articles d
where g.feed_id = d.feed_id
  and g.url like 'https://news.google.com/%'
  and d.url not like 'https://news.google.com/%'
  and abs(extract(epoch from g.collected_at - d.collected_at)) < 3 * 86400
  and pg_temp.mesma_manchete(g.title, d.title)
  and not exists (select 1 from saved_articles s where s.article_id = g.id);

delete from catalog_articles g
using catalog_articles d
where g.catalog_id = d.catalog_id
  and g.url like 'https://news.google.com/%'
  and d.url not like 'https://news.google.com/%'
  and abs(extract(epoch from g.collected_at - d.collected_at)) < 3 * 86400
  and pg_temp.mesma_manchete(g.title, d.title);

commit;
