-- ============================================================
-- 045_nomes_vetores_e_seguir.sql
-- Rode ANTES de subir o coletor e o hub desta leva.
--
-- Fase 2 do feed sem IA (a fase 1 é o 044):
-- 1) vetores_noticias: o "sentido" de cada notícia em 384 números
--    (vetores.py, modelo multilíngue que roda no GitHub). É o que junta
--    português e inglês da mesma história. Guardado pela URL, só pra
--    janela do agrupamento: o coletor apaga os de mais de 4 dias.
--    Usa a extensão pgvector (tipo vector), que o Supabase já tem.
-- 2) entidades: os nomes de cada notícia pelo spaCy (pessoas,
--    organizações, lugares, obras), como aparecem e com o tipo, pro hub
--    mostrar e a pessoa seguir. palavras_chave continua com as chaves
--    normalizadas (o agrupamento e o "seguir" comparam por elas).
-- 3) Seguir temas e nomes: tabela seguindo (cada um a sua), sugestões
--    (os mais citados em 3 dias, o coletor atualiza de hora em hora) e
--    noticias_seguidas() pra aba Seguindo do Início.
-- 4) trending() devolve também temas e nomes da notícia (o leitor mostra
--    o que dá pra seguir). Muda as colunas: precisa apagar e recriar.
-- 5) pares_avaliados: a amostra de pares marcada à mão (mesma história
--    ou não), pra medir a precisão do agrupamento. Só o coletor e a
--    página Relatórios (chave secreta) mexem.
-- 6) Contador do menu: volta a subir com cada notícia nova e zera à
--    meia-noite (Brasília): as que chegaram hoje e a pessoa não leu. O
--    "desde a última visita" (038) zerava ao abrir o Início, que é a
--    primeira tela, e o número ficava sempre perto de zero.
-- ============================================================

set lock_timeout = '5s';

begin;

-- 1) vetores ---------------------------------------------------------------

create extension if not exists vector with schema extensions;

create table vetores_noticias (
  url text primary key,
  vetor extensions.vector(384) not null,
  criado_em timestamptz not null default now()
);
create index idx_vetores_noticias_criado on vetores_noticias (criado_em);

alter table vetores_noticias enable row level security;
revoke all on vetores_noticias from anon, authenticated;

-- 2) nomes -----------------------------------------------------------------

-- [{"nome": "Flávio Bolsonaro", "chave": "flavio bolsonaro", "tipo": "pessoa"}, ...]
-- Nulo = classificada antes do spaCy: o classificar.py refaz os últimos 3 dias
alter table articles add column entidades jsonb;
alter table catalog_articles add column entidades jsonb;

-- "quem segue Lula" e "quem segue Inteligência artificial": arrays com &&
create index idx_articles_palavras_chave on articles using gin (palavras_chave);
create index idx_articles_temas on articles using gin (temas);
create index idx_catalog_articles_palavras_chave on catalog_articles using gin (palavras_chave);
create index idx_catalog_articles_temas on catalog_articles using gin (temas);

-- As mesmas colunas de antes, mais três no fim (o hub lê pelo nome)
create or replace view artigos_do_usuario with (security_invoker = true) as
select a.id, a.title, a.url, a.author, a.content, a.ai_summary, a.category, a.image_url,
       a.published_at, a.collected_at, a.palavras_chave, a.feed_id,
       s.id as source_id, s.name as fonte_nome, s.url as fonte_url, s.topic_id,
       a.temas, a.entidades, a.historia_id
from articles a
join sources s on s.feed_id = a.feed_id;

-- 3) seguir temas e nomes --------------------------------------------------

create table seguindo (
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  tipo text not null check (tipo in ('tema', 'nome')),
  -- tema: o nome do tema ("Inteligência artificial"); nome: a chave
  -- normalizada ("flavio bolsonaro"), a mesma de palavras_chave
  chave text not null check (length(chave) between 1 and 80),
  rotulo text not null check (length(rotulo) between 1 and 80),
  criado_em timestamptz not null default now(),
  primary key (user_id, tipo, chave)
);

alter table seguindo enable row level security;
revoke all on seguindo from anon, authenticated;
grant select, insert, delete on seguindo to authenticated;
create policy "cada um ve o que segue" on seguindo
  for select to authenticated using (user_id = (select auth.uid()));
create policy "cada um segue por si" on seguindo
  for insert to authenticated with check (user_id = (select auth.uid()));
create policy "cada um deixa de seguir por si" on seguindo
  for delete to authenticated using (user_id = (select auth.uid()));

-- Os temas e nomes mais citados nos últimos 3 dias: o que o hub sugere
-- pra seguir. O classificar.py refaz de hora em hora.
create table sugestoes_seguir (
  tipo text not null check (tipo in ('tema', 'nome')),
  chave text not null,
  rotulo text not null,
  detalhe text,            -- tema: a categoria; nome: pessoa, organização, lugar ou outro
  noticias int not null,   -- quantas notícias citaram
  primary key (tipo, chave)
);

alter table sugestoes_seguir enable row level security;
revoke all on sugestoes_seguir from anon, authenticated;
grant select on sugestoes_seguir to authenticated;
create policy "usuarios logados veem as sugestoes" on sugestoes_seguir
  for select to authenticated using (true);

-- Aba Seguindo: notícias dos últimos 7 dias com algum tema ou nome que a
-- pessoa segue, das fontes dela e do catálogo. Uma por história (a das
-- fontes dela primeiro, depois a mais recente), com a cobertura e o que
-- ela segue que apareceu na notícia (motivo).
create function noticias_seguidas(p_limite int default 30, p_offset int default 0)
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
    select tipo, chave, rotulo from seguindo where user_id = (select auth.uid())
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

revoke execute on function noticias_seguidas(int, int) from public, anon;
grant execute on function noticias_seguidas(int, int) to authenticated;

-- 4) Trending com temas e nomes --------------------------------------------
-- O mesmo do 044, com temas e entidades no fim.

drop function trending(text, int);

create function trending(p_categoria text default null, p_limite int default 12)
returns table (
  id uuid, title text, url text, author text, content text, ai_summary text, image_url text,
  published_at timestamptz, collected_at timestamptz, palavras_chave text[],
  fonte_id uuid, fonte_nome text, fonte_url text, categoria text, cobertura int,
  temas text[], entidades jsonb
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
           (h.fontes - 1) as cobertura, h.ultima as quando, c.temas, c.entidades
    from historias h
    join catalog_articles c on c.id = h.representante_catalogo
    join feed_catalog f on f.id = c.catalog_id
    where h.ultima > now() - interval '12 hours' and h.fontes >= 2
    union all
    -- avulsas, pra completar
    select c.id, c.title, c.url, c.author, c.content, c.ai_summary, c.image_url,
           c.published_at, c.collected_at, coalesce(c.palavras_chave, '{}'),
           f.id, f.name, f.url, coalesce(c.category, f.category), f.category,
           0, coalesce(c.published_at, c.collected_at), c.temas, c.entidades
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
         o.fonte_id, o.fonte_nome, o.fonte_url, o.categoria, o.cobertura, o.temas, o.entidades
  from ordenadas o
  where p_categoria is not null or o.posicao = 1
  order by o.cobertura desc, o.quando desc
  limit greatest(1, least(p_limite, 40));
$$;

revoke execute on function trending(text, int) from public, anon;
grant execute on function trending(text, int) to authenticated;

-- 5) amostra marcada à mão -------------------------------------------------

create table pares_avaliados (
  id bigint generated always as identity primary key,
  a_url text not null,
  b_url text not null,
  a_titulo text not null,
  b_titulo text not null,
  a_fonte text,
  b_fonte text,
  a_trecho text,
  b_trecho text,
  a_quando timestamptz,
  b_quando timestamptz,
  nota real not null,
  juntou boolean not null,          -- a decisão do agrupar.py na hora do sorteio
  -- texto, sentido, nomes, título, horas, números, línguas, mesma fonte:
  -- dá pra testar outros pesos depois sem recalcular nada (agrupar.py --medir)
  sinais jsonb not null,
  faixa text not null,              -- faixa da nota ("58-65")
  peso real not null default 1,     -- quantos pares da janela este representa
  resposta text check (resposta in ('mesma', 'diferente', 'nao_sei')),
  respondido_em timestamptz,
  criado_em timestamptz not null default now(),
  unique (a_url, b_url)
);
create index idx_pares_avaliados_pendentes on pares_avaliados (id) where resposta is null;

alter table pares_avaliados enable row level security;
revoke all on pares_avaliados from anon, authenticated;

-- 6) contador do menu --------------------------------------------------------
-- Mesmo nome e colunas (o hub lê do mesmo jeito). sources.visto_em e
-- registrar_visita() ficam sem uso; dá pra apagar numa limpeza depois.

create or replace view novas_por_fonte with (security_invoker = true) as
select s.id as source_id, count(*)::integer as novas
from sources s
join articles a on a.feed_id = s.feed_id
where a.collected_at >= (date_trunc('day', now() at time zone 'America/Sao_Paulo') at time zone 'America/Sao_Paulo')
  and not exists (
    select 1 from read_articles r
    where r.article_id = a.id and r.user_id = (select auth.uid())
  )
group by s.id;

commit;
