-- ============================================================
-- 020_catalog_articles.sql
-- Notícias das fontes do catálogo (feed_catalog), pra aba "Explorar"
-- do Início: um acumulado do que os canais brasileiros publicaram,
-- inclusive dos que o usuário ainda não segue.
--
-- Por que uma tabela separada de articles?
--   articles pertence a um usuário (articles -> sources -> topics ->
--   user_id), e a RLS dela depende disso. Notícia do catálogo é pública
--   e igual pra todo mundo: guardar uma cópia por usuário seria
--   desperdício, e misturar as duas na mesma tabela complicaria a RLS.
--
-- Quem escreve aqui é só o coletor (coletor/coletar_catalogo.py), que
-- conecta direto no Postgres e não passa pela RLS. Pelo hub, quem está
-- logado só lê.
-- ============================================================

create table catalog_articles (
    id           uuid primary key default gen_random_uuid(),
    catalog_id   uuid not null references feed_catalog(id) on delete cascade,
    title        text not null,
    url          text not null unique,   -- dedupe, igual em articles
    content      text,
    author       text,
    image_url    text,
    published_at timestamptz,
    collected_at timestamptz not null default now()
);

-- A aba Explorar lista do mais novo pro mais antigo, às vezes filtrando
-- por fonte; e o coletor apaga o que passou de 14 dias por collected_at.
create index idx_catalog_articles_published on catalog_articles (published_at desc nulls last, id);
create index idx_catalog_articles_catalog on catalog_articles (catalog_id);
create index idx_catalog_articles_collected on catalog_articles (collected_at);

alter table catalog_articles enable row level security;

-- "to authenticated": diferente do feed_catalog (público até pra quem
-- não entrou), as notícias só aparecem dentro do hub, logado.
create policy "usuarios logados leem noticias do catalogo"
  on catalog_articles for select
  to authenticated
  using (true);
