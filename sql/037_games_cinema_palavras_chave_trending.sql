-- ============================================================
-- 037_games_cinema_palavras_chave_trending.sql
-- Rode ANTES de subir o coletor e o hub desta leva.
--
-- 1) Categorias novas: Games e Cinema saem de Entretenimento.
--    - Games: videogames, consoles, e-sports.
--    - Cinema: filmes, séries e streaming.
--    - Entretenimento fica com TV aberta, música, celebridades e cultura.
--    No catálogo, as fontes de games e de cinema mudam de categoria
--    (as mistas, como Jovem Nerd e Vulture, continuam em Entretenimento).
--    Nas notícias dos usuários, as que vieram dessas fontes mudam junto;
--    daqui pra frente a IA escolhe notícia por notícia.
-- 2) Palavras-chave: a IA passa a devolver de 3 a 5 por notícia (base
--    para "notícias por tema" no futuro e para o Trending agora).
-- 3) trending(): as notícias do catálogo das últimas 12 horas que mais
--    fontes diferentes estão cobrindo (palavras-chave em comum), com
--    foto e resumo. Sem categoria: a principal de cada categoria.
-- ============================================================

set lock_timeout = '5s';

begin;

-- 1) categorias -----------------------------------------------------------

alter table articles drop constraint articles_category_check;
alter table articles add constraint articles_category_check check (
  category is null or category = any (array[
    'Tecnologia', 'Finanças', 'Humor', 'Política', 'Ciência', 'Saúde', 'Esportes',
    'Entretenimento', 'Cinema', 'Games', 'Mundo', 'Outros'
  ])
);

update feed_catalog set category = 'Games'
where category = 'Entretenimento' and name in (
  '80 Level', 'Arkade', 'Combo Infinito', 'Critical Hits', 'Destructoid', 'Eurogamer',
  'Flow Games', 'Game Informer', 'GameBlast', 'GameSpot', 'GamesRadar+', 'GameVicio',
  'IGN', 'IGN Brasil', 'Kotaku', 'Nintendo Blast', 'Nintendo Life', 'PC Gamer', 'PCGamesN',
  'PlayStation Blog', 'PlayStation.Blog BR', 'Polygon', 'PSX Brasil', 'Pure Xbox',
  'Push Square', 'Rock Paper Shotgun', 'Video Games Chronicle', 'Voxel', 'Xbox Wire'
);

update feed_catalog set category = 'Cinema'
where category = 'Entretenimento' and name in (
  '/Film', 'AdoroCinema', 'CinePOP', 'Collider', 'Deadline', 'Empire', 'IndieWire',
  'Omelete', 'Pipoca Moderna', 'Plano Crítico', 'RogerEbert.com', 'Screen Daily',
  'Screen Rant', 'The Hollywood Reporter', 'TheWrap', 'Variety'
);

-- notícias dos usuários que vieram dessas fontes (mesma URL de feed)
update articles a
set category = c.category
from sources s
join feed_catalog c on c.url = s.url
where s.id = a.source_id
  and a.category = 'Entretenimento'
  and c.category in ('Games', 'Cinema');

-- 2) palavras-chave ------------------------------------------------------

alter table articles add column palavras_chave text[];
alter table catalog_articles add column palavras_chave text[];

-- 3) trending ------------------------------------------------------------

create index if not exists idx_catalog_articles_trending
  on catalog_articles (collected_at desc)
  where ai_summary is not null and image_url is not null;

create or replace function trending(p_categoria text default null, p_limite int default 12)
returns table (
  id uuid, title text, url text, author text, content text, ai_summary text, image_url text,
  published_at timestamptz, collected_at timestamptz, palavras_chave text[],
  fonte_id uuid, fonte_nome text, fonte_url text, categoria text, cobertura int
)
language sql
stable
security invoker
set search_path = public
as $$
  with recentes as (
    select c.id, c.title, c.url, c.author, c.content, c.ai_summary, c.image_url,
           c.published_at, c.collected_at, coalesce(c.palavras_chave, '{}') as palavras_chave,
           f.id as fonte_id, f.name as fonte_nome, f.url as fonte_url, f.category as categoria
    from catalog_articles c
    join feed_catalog f on f.id = c.catalog_id
    where f.vitrine
      and c.collected_at > now() - interval '12 hours'
      and c.ai_summary is not null
      and c.image_url is not null
      and (p_categoria is null or f.category = p_categoria)
  ),
  pontuadas as (
    -- cobertura: quantas OUTRAS fontes publicaram algo com pelo menos 2
    -- palavras-chave em comum (a mesma história contada por mais gente)
    select r.*,
           (select count(distinct o.fonte_id)
            from recentes o
            where o.fonte_id <> r.fonte_id
              and cardinality(array(
                    select unnest(o.palavras_chave) intersect select unnest(r.palavras_chave)
                  )) >= 2)::int as cobertura
    from recentes r
  ),
  ordenadas as (
    select p.*,
           row_number() over (
             partition by p.categoria
             order by p.cobertura desc, coalesce(p.published_at, p.collected_at) desc
           ) as posicao
    from pontuadas p
  )
  select o.id, o.title, o.url, o.author, o.content, o.ai_summary, o.image_url,
         o.published_at, o.collected_at, o.palavras_chave,
         o.fonte_id, o.fonte_nome, o.fonte_url, o.categoria, o.cobertura
  from ordenadas o
  -- sem categoria: só a principal de cada uma; com categoria: a lista dela
  -- (o hub ainda tira as repetidas da mesma história)
  where p_categoria is not null or o.posicao = 1
  order by o.cobertura desc, coalesce(o.published_at, o.collected_at) desc
  limit greatest(1, least(p_limite, 40));
$$;

revoke execute on function trending(text, int) from public, anon;
grant execute on function trending(text, int) to authenticated;

commit;
