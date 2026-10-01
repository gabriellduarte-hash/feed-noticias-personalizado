-- ============================================================
-- 014_ler_mais_tarde.sql
-- "Salvar pra ler mais tarde" — tabela de relação usuário↔artigo
-- (não um campo em articles, porque é por usuário, não por artigo).
-- ============================================================

create table saved_articles (
    user_id uuid not null references auth.users(id) on delete cascade,
    article_id uuid not null references articles(id) on delete cascade,
    created_at timestamptz not null default now(),
    primary key (user_id, article_id)
);

alter table saved_articles enable row level security;

create policy "usuarios veem seus proprios salvos"
  on saved_articles for select
  using (auth.uid() = user_id);

create policy "usuarios salvam artigos pra si mesmos"
  on saved_articles for insert
  with check (auth.uid() = user_id);

create policy "usuarios removem seus proprios salvos"
  on saved_articles for delete
  using (auth.uid() = user_id);
