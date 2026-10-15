-- ============================================================
-- 047_catalogo_de_temas_busca_e_feed.sql
-- Rode ANTES de subir o coletor e o hub desta leva.
--
-- 1) catalogo_temas: os ~90 temas (Filmes, Séries, Fofoca, Quadrinhos,
--    Cultura geek...), por assunto, com sinônimos pra busca ("hq",
--    "comics" -> Quadrinhos). A fonte é coletor/temas.py: o
--    classificar.py copia pra cá a cada rodada.
-- 2) Busca sem acento: coluna `busca` (título + começo do texto, em
--    minúsculas e sem acento), gerada pelo próprio banco. O hub procura
--    por ela com o singular e o plural ("serie" acha "séries", "filmes"
--    acha "filme").
-- 3) feed_principal(): o Início › Eu com as notícias das fontes da pessoa
--    e, junto, as dos temas que ela segue (do catálogo de sites, uma por
--    história, sem repetir o que já veio das fontes dela).
-- 4) Os últimos 3 dias voltam pra classificação: a próxima coleta dá os
--    temas novos a eles (~2 min a mais, uma vez).
-- ============================================================

set lock_timeout = '5s';

begin;

-- 1) catálogo de temas -------------------------------------------------------

create table catalogo_temas (
  nome text primary key,             -- "Quadrinhos": o que aparece e o que se segue
  grupo text not null,               -- "Cultura geek": pra organizar a lista
  sinonimos text[] not null default '{}',
  ordem int not null default 0,
  atualizado_em timestamptz not null default now()
);

alter table catalogo_temas enable row level security;
revoke all on catalogo_temas from anon, authenticated;
grant select on catalogo_temas to authenticated;
create policy "usuarios logados veem o catalogo de temas" on catalogo_temas
  for select to authenticated using (true);

-- 2) busca sem acento --------------------------------------------------------
-- translate/lower/left são imutáveis: dá pra coluna gerada (o banco
-- mantém sozinho, em toda notícia nova ou editada).

alter table articles add column busca text generated always as (
  lower(translate(
    title || ' ' || left(coalesce(content, ''), 4000),
    'ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑáàâãäéèêëíìîïóòôõöúùûüçñ',
    'AAAAAEEEEIIIIOOOOOUUUUCNaaaaaeeeeiiiiooooouuuucn'
  ))
) stored;

alter table catalog_articles add column busca text generated always as (
  lower(translate(
    title || ' ' || left(coalesce(content, ''), 4000),
    'ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑáàâãäéèêëíìîïóòôõöúùûüçñ',
    'AAAAAEEEEIIIIOOOOOUUUUCNaaaaaeeeeiiiiooooouuuucn'
  ))
) stored;

-- As mesmas colunas de antes, mais `busca` no fim
create or replace view artigos_do_usuario with (security_invoker = true) as
select a.id, a.title, a.url, a.author, a.content, a.ai_summary, a.category, a.image_url,
       a.published_at, a.collected_at, a.palavras_chave, a.feed_id,
       s.id as source_id, s.name as fonte_nome, s.url as fonte_url, s.topic_id,
       a.temas, a.entidades, a.historia_id, a.busca
from articles a
join sources s on s.feed_id = a.feed_id;

-- 3) feed principal com os temas seguidos ----------------------------------

create function feed_principal(p_limite int default 30, p_offset int default 0)
returns table (
  id uuid, title text, url text, author text, content text, ai_summary text, category text, image_url text,
  published_at timestamptz, collected_at timestamptz, fonte_id uuid, fonte_nome text, fonte_url text,
  origem text, temas text[], entidades jsonb, motivo text
)
language sql
stable
security invoker
set search_path = public
as $$
  with meus as (
    select tipo, chave, rotulo from seguindo where user_id = (select auth.uid())
  ),
  chaves as (
    select coalesce(array_agg(chave) filter (where tipo = 'tema'), '{}') as temas,
           coalesce(array_agg(chave) filter (where tipo = 'nome'), '{}') as nomes
    from meus
  ),
  -- dos sites do catálogo, só o que fala dos temas seguidos, uma por
  -- história, e nada que já venha das fontes da pessoa (a mesma URL ou a
  -- mesma história)
  dos_temas as (
    select distinct on (coalesce(c.historia_id::text, c.url))
           c.id, c.title, c.url, c.author, c.content, c.ai_summary, coalesce(c.category, f.category) as category,
           c.image_url, c.published_at, c.collected_at, f.id as fonte_id, f.name as fonte_nome, f.url as fonte_url,
           'catalogo'::text as origem, c.temas, c.entidades,
           (select string_agg(m.rotulo, ', ' order by m.rotulo) from meus m
            where (m.tipo = 'tema' and m.chave = any(c.temas))
               or (m.tipo = 'nome' and m.chave = any(c.palavras_chave))) as motivo
    from catalog_articles c
    join feed_catalog f on f.id = c.catalog_id, chaves k
    where c.collected_at > now() - interval '3 days'
      and (c.temas && k.temas or c.palavras_chave && k.nomes)
      and not exists (
        select 1 from artigos_do_usuario a
        where a.url = c.url or (c.historia_id is not null and a.historia_id = c.historia_id)
      )
    order by coalesce(c.historia_id::text, c.url), coalesce(c.published_at, c.collected_at) desc
  )
  select x.* from (
    select a.id, a.title, a.url, a.author, a.content, a.ai_summary, a.category, a.image_url,
           a.published_at, a.collected_at, a.source_id, a.fonte_nome, a.fonte_url,
           'usuario'::text, a.temas, a.entidades, null::text
    from artigos_do_usuario a
    union all
    select * from dos_temas
  ) x
  order by x.published_at desc nulls last, x.id
  limit greatest(1, least(p_limite, 60)) offset greatest(0, p_offset);
$$;

revoke execute on function feed_principal(int, int) from public, anon;
grant execute on function feed_principal(int, int) to authenticated;

-- 4) temas novos nos últimos 3 dias ----------------------------------------

update articles set classificado_em = null where collected_at > now() - interval '3 days';
update catalog_articles set classificado_em = null where collected_at > now() - interval '3 days';

commit;
