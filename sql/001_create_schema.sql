-- ============================================================
-- 001_create_schema.sql
-- Schema inicial do Feed de Notícias Personalizado.
-- Rode este script no SQL Editor do Supabase (projeto do feed).
-- ============================================================

-- ------------------------------------------------------------
-- topics: os temas que o usuário quer acompanhar
-- (ex.: "Inteligência Artificial", "Futebol", "Economia BR")
-- ------------------------------------------------------------
create table topics (
    id         uuid primary key default gen_random_uuid(),
    user_id    uuid not null references auth.users(id) on delete cascade,
    name       text not null,
    created_at timestamptz not null default now()
);

-- Busca comum: "me dá os tópicos do usuário X"
create index idx_topics_user_id on topics(user_id);


-- ------------------------------------------------------------
-- sources: de onde o conteúdo de um tópico vem
-- (um feed RSS, ou uma URL avulsa pra fazer scraping)
-- ------------------------------------------------------------
create table sources (
    id         uuid primary key default gen_random_uuid(),
    topic_id   uuid not null references topics(id) on delete cascade,
    url        text not null,
    type       text not null check (type in ('rss', 'scrape')),
    created_at timestamptz not null default now()
);

create index idx_sources_topic_id on sources(topic_id);


-- ------------------------------------------------------------
-- articles: cada artigo coletado de uma fonte
-- ------------------------------------------------------------
create table articles (
    id           uuid primary key default gen_random_uuid(),
    source_id    uuid not null references sources(id) on delete cascade,
    title        text not null,
    url          text not null unique,  -- garante deduplicação no banco
    content      text,
    published_at timestamptz,
    collected_at timestamptz not null default now()
);

create index idx_articles_source_id on articles(source_id);
-- Busca comum: "artigos coletados nas últimas 24h" (usado no job diário)
create index idx_articles_collected_at on articles(collected_at);


-- ------------------------------------------------------------
-- digests: o resumo diário gerado e enviado por e-mail
-- ------------------------------------------------------------
create table digests (
    id           uuid primary key default gen_random_uuid(),
    user_id      uuid not null references auth.users(id) on delete cascade,
    digest_date  date not null,
    html_content text,
    sent_at      timestamptz,
    created_at   timestamptz not null default now(),

    -- um usuário só pode ter um digest por dia
    unique (user_id, digest_date)
);

create index idx_digests_user_id on digests(user_id);
