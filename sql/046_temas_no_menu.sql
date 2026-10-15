-- ============================================================
-- 046_temas_no_menu.sql
-- Rode ANTES de subir o hub desta leva.
--
-- Seguir temas virou como seguir fontes: os temas e nomes seguidos ficam
-- no menu, abaixo das coleções ("Temas"), cada um com a página das
-- notícias dele e o número das que chegaram hoje. A aba Seguindo do
-- Início sai.
--
-- 1) noticias_seguidas ganha p_tipo e p_chave: com eles, só as notícias
--    daquele tema ou nome (a página do tema, mesmo pra quem ainda não
--    segue); sem eles, de todos os que a pessoa segue ("Todos os temas").
--    Os dois têm valor padrão: o hub de antes continua funcionando até o
--    push.
-- 2) contagem_seguidos(): quantas histórias de cada tema seguido chegaram
--    hoje (desde a meia-noite, Brasília). É o número do menu; zera à
--    meia-noite, como o das fontes.
-- ============================================================

set lock_timeout = '5s';

begin;

-- 1) notícias de um tema, ou de todos os seguidos ---------------------------

drop function noticias_seguidas(int, int);

create function noticias_seguidas(
  p_limite int default 30,
  p_offset int default 0,
  p_tipo text default null,
  p_chave text default null
)
returns table (
  id uuid, title text, url text, author text, content text, ai_summary text, category text, image_url text,
  published_at timestamptz, collected_at timestamptz, fonte_id uuid, fonte_nome text, fonte_url text,
  origem text, temas text[], entidades jsonb, cobertura int, motivo text
)
language sql
stable
security invoker
set search_path = public
as $$
  with meus as (
    -- sem tema escolhido: tudo o que a pessoa segue
    select tipo, chave, rotulo from seguindo
    where user_id = (select auth.uid()) and p_tipo is null
    union all
    -- com tema escolhido: só ele
    select p_tipo, p_chave, p_chave
    where p_tipo in ('tema', 'nome') and p_chave is not null
  ),
  chaves as (
    select coalesce(array_agg(chave) filter (where tipo = 'tema'), '{}') as temas,
           coalesce(array_agg(chave) filter (where tipo = 'nome'), '{}') as nomes
    from meus
  ),
  candidatas as (
    select a.id, a.title, a.url, a.author, a.content, a.ai_summary, a.category, a.image_url,
           a.published_at, a.collected_at, a.source_id as fonte_id, a.fonte_nome, a.fonte_url,
           'usuario'::text as origem, a.temas, a.entidades, a.palavras_chave, a.historia_id
    from artigos_do_usuario a, chaves k
    where a.collected_at > now() - interval '7 days'
      and (a.temas && k.temas or a.palavras_chave && k.nomes)
    union all
    select c.id, c.title, c.url, c.author, c.content, c.ai_summary, coalesce(c.category, f.category), c.image_url,
           c.published_at, c.collected_at, f.id, f.name, f.url,
           'catalogo', c.temas, c.entidades, c.palavras_chave, c.historia_id
    from catalog_articles c
    join feed_catalog f on f.id = c.catalog_id, chaves k
    where c.collected_at > now() - interval '7 days'
      and (c.temas && k.temas or c.palavras_chave && k.nomes)
  ),
  unicas as (
    select distinct on (coalesce(c.historia_id::text, c.url)) c.*
    from candidatas c
    order by coalesce(c.historia_id::text, c.url), (c.origem = 'usuario') desc,
             coalesce(c.published_at, c.collected_at) desc
  )
  select u.id, u.title, u.url, u.author, u.content, u.ai_summary, u.category, u.image_url,
         u.published_at, u.collected_at, u.fonte_id, u.fonte_nome, u.fonte_url, u.origem, u.temas, u.entidades,
         coalesce(h.fontes - 1, 0) as cobertura,
         (select string_agg(m.rotulo, ', ' order by m.rotulo) from meus m
          where (m.tipo = 'tema' and m.chave = any(u.temas))
             or (m.tipo = 'nome' and m.chave = any(u.palavras_chave))) as motivo
  from unicas u
  left join historias h on h.id = u.historia_id
  order by coalesce(u.published_at, u.collected_at) desc, u.id
  limit greatest(1, least(p_limite, 60)) offset greatest(0, p_offset);
$$;

revoke execute on function noticias_seguidas(int, int, text, text) from public, anon;
grant execute on function noticias_seguidas(int, int, text, text) to authenticated;

-- 2) o número de cada tema no menu ------------------------------------------

create function contagem_seguidos()
returns table (tipo text, chave text, noticias int)
language sql
stable
security invoker
set search_path = public
as $$
  with meus as (
    select tipo, chave from seguindo where user_id = (select auth.uid())
  ),
  hoje as (
    select date_trunc('day', now() at time zone 'America/Sao_Paulo') at time zone 'America/Sao_Paulo' as inicio
  ),
  candidatas as (
    select a.url, a.historia_id, a.temas, a.palavras_chave
    from artigos_do_usuario a, hoje
    where a.collected_at >= hoje.inicio
    union all
    select c.url, c.historia_id, c.temas, c.palavras_chave
    from catalog_articles c, hoje
    where c.collected_at >= hoje.inicio
  )
  -- uma por história, como na página do tema
  select m.tipo, m.chave, count(distinct coalesce(c.historia_id::text, c.url))::int
  from meus m
  join candidatas c
    on (m.tipo = 'tema' and m.chave = any(c.temas))
    or (m.tipo = 'nome' and m.chave = any(c.palavras_chave))
  group by m.tipo, m.chave;
$$;

revoke execute on function contagem_seguidos() from public, anon;
grant execute on function contagem_seguidos() to authenticated;

commit;
