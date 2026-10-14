-- ============================================================
-- 044_classificacao_e_historias_sem_ia.sql
-- Rode ANTES de subir o coletor e o hub desta leva.
--
-- A IA (Gemini) resumia e classificava toda notícia, de hora em hora: em
-- 14/10 eram ~3 mil notícias por dia só das fontes do Gabriel, e o
-- crédito acabou. Agora a IA só resume as 10 notícias que vão pro e-mail
-- (na hora do envio); o resto é feito sem IA:
--   - categoria, temas e nomes (classificar.py): taxonomia com termos
--     por categoria + a categoria do site;
--   - histórias (agrupar.py): notícias de fontes diferentes sobre o mesmo
--     acontecimento, por uma nota de semelhança (texto, nomes, título,
--     tempo). É o que define o Trending e a relevância no e-mail.
-- ============================================================

set lock_timeout = '5s';

begin;

-- classificação sem IA ---------------------------------------------------

alter table articles
  add column temas text[],
  add column categoria_confianca real,
  add column classificado_em timestamptz;
alter table catalog_articles
  add column temas text[],
  add column categoria_confianca real,
  add column classificado_em timestamptz;

create index idx_articles_a_classificar on articles (collected_at desc) where classificado_em is null;
create index idx_catalog_articles_a_classificar on catalog_articles (collected_at desc) where classificado_em is null;

-- histórias ---------------------------------------------------------------

create table historias (
  id uuid primary key,
  titulo text not null,
  categoria text,
  fontes int not null,              -- sites diferentes cobrindo
  noticias int not null,
  primeira timestamptz,
  ultima timestamptz,
  -- a notícia do catálogo que aparece no Trending (com foto e texto)
  representante_catalogo uuid,
  nomes text[],                     -- os nomes mais citados (pessoas, empresas, lugares)
  atualizada_em timestamptz not null default now()
);
create index idx_historias_ultima on historias (ultima desc);

alter table historias enable row level security;
revoke all on historias from anon;
grant select on historias to authenticated;
create policy "qualquer usuario logado ve as historias" on historias for select to authenticated using (true);

alter table articles
  add column historia_id uuid,
  add column historia_nota smallint,
  add column historia_motivo text;   -- por que entrou: "texto 0.58 · título 0.80 · 2h · nomes: ..."
alter table catalog_articles
  add column historia_id uuid,
  add column historia_nota smallint,
  add column historia_motivo text;

create index idx_articles_historia on articles (historia_id) where historia_id is not null;
create index idx_catalog_articles_historia on catalog_articles (historia_id) where historia_id is not null;

-- Trending sem IA ---------------------------------------------------------
-- As histórias das últimas 12h que mais sites estão cobrindo, cada uma
-- pela notícia do catálogo que a representa. Completa com notícias
-- avulsas recentes (com foto e texto) quando há poucas histórias.
-- Mesmas colunas de antes: o hub não muda o jeito de ler.

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
  with candidatas as (
    -- histórias com 2+ sites
    select c.id, c.title, c.url, c.author, c.content, c.ai_summary, c.image_url,
           c.published_at, c.collected_at, coalesce(h.nomes, '{}') as palavras_chave,
           f.id as fonte_id, f.name as fonte_nome, f.url as fonte_url,
           coalesce(h.categoria, c.category, f.category) as categoria, f.category as categoria_do_site,
           (h.fontes - 1) as cobertura, h.ultima as quando
    from historias h
    join catalog_articles c on c.id = h.representante_catalogo
    join feed_catalog f on f.id = c.catalog_id
    where h.ultima > now() - interval '12 hours' and h.fontes >= 2
    union all
    -- avulsas, pra completar
    select c.id, c.title, c.url, c.author, c.content, c.ai_summary, c.image_url,
           c.published_at, c.collected_at, coalesce(c.palavras_chave, '{}'),
           f.id, f.name, f.url, coalesce(c.category, f.category), f.category,
           0, coalesce(c.published_at, c.collected_at)
    from catalog_articles c
    join feed_catalog f on f.id = c.catalog_id
    where f.vitrine and c.historia_id is null
      and c.collected_at > now() - interval '12 hours'
      and c.image_url is not null and length(coalesce(c.content, '')) >= 400
  ),
  filtradas as (
    select * from candidatas
    where p_categoria is null
       or categoria = p_categoria
       or (p_categoria in ('Notícias', 'Meio ambiente', 'Automóveis') and categoria_do_site = p_categoria)
  ),
  ordenadas as (
    select f.*,
           row_number() over (partition by f.categoria order by f.cobertura desc, f.quando desc) as posicao
    from filtradas f
  )
  select o.id, o.title, o.url, o.author, o.content, o.ai_summary, o.image_url,
         o.published_at, o.collected_at, o.palavras_chave,
         o.fonte_id, o.fonte_nome, o.fonte_url, o.categoria, o.cobertura
  from ordenadas o
  where p_categoria is not null or o.posicao = 1
  order by o.cobertura desc, o.quando desc
  limit greatest(1, least(p_limite, 40));
$$;

revoke execute on function trending(text, int) from public, anon;
grant execute on function trending(text, int) to authenticated;

commit;
