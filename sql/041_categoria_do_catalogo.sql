-- ============================================================
-- 041_categoria_do_catalogo.sql
-- Rode ANTES de subir o coletor desta leva (o resumir.py passa a gravar
-- a coluna nova).
--
-- O Trending usava a categoria do SITE: uma notícia de futebol publicada
-- por um site de política aparecia em "Política". A IA já classificava
-- cada notícia do catálogo (o mesmo pedido das notícias dos usuários),
-- mas a resposta era jogada fora. Agora fica em catalog_articles.category
-- e o Trending usa ela; sem ela (notícia sem texto, que a IA não resume),
-- vale a categoria do site.
--
-- Filtro por categoria no Trending:
--   - categorias da IA (Esportes, Política...): a da notícia;
--   - as que só existem no catálogo (Notícias, Meio ambiente,
--     Automóveis): a do site, porque a IA nunca dá essas.
-- ============================================================

set lock_timeout = '5s';

begin;

alter table catalog_articles add column category text;
alter table catalog_articles add constraint catalog_articles_category_check check (
  category is null or category = any (array[
    'Tecnologia', 'Finanças', 'Humor', 'Política', 'Ciência', 'Saúde', 'Esportes',
    'Entretenimento', 'Cinema', 'Games', 'Mundo', 'Outros'
  ])
);

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
           f.id as fonte_id, f.name as fonte_nome, f.url as fonte_url,
           coalesce(c.category, f.category) as categoria
    from catalog_articles c
    join feed_catalog f on f.id = c.catalog_id
    where f.vitrine
      and c.collected_at > now() - interval '12 hours'
      and c.ai_summary is not null
      and c.image_url is not null
      and (
        p_categoria is null
        or coalesce(c.category, f.category) = p_categoria
        or (p_categoria in ('Notícias', 'Meio ambiente', 'Automóveis') and f.category = p_categoria)
      )
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
  where p_categoria is not null or o.posicao = 1
  order by o.cobertura desc, coalesce(o.published_at, o.collected_at) desc
  limit greatest(1, least(p_limite, 40));
$$;

revoke execute on function trending(text, int) from public, anon;
grant execute on function trending(text, int) to authenticated;

commit;
