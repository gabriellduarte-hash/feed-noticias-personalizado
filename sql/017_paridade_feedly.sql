-- ============================================================
-- 017_paridade_feedly.sql
-- O que o hub precisa pra funcionar como a Feedly: nome de exibição
-- e favorito por fonte, controle de "lido" por usuário, contagem de
-- não lidos no menu lateral, e permissão de editar uma fonte
-- (renomear, favoritar, mover de coleção).
-- ============================================================

-- 1) Nome de exibição da fonte ("IGN Brasil" em vez da URL do feed).
--    Nullable: fontes antigas ficam sem nome e o hub mostra o domínio.
alter table sources add column name text;
alter table sources add column favorite boolean not null default false;

-- Aproveita o catálogo pra dar nome às fontes que vieram de lá.
update sources s
set name = c.name
from feed_catalog c
where c.url = s.url and s.name is null;


-- 2) Fonte não tinha policy de UPDATE (só select/insert/delete).
--    USING   = quais linhas posso editar (fontes dos meus tópicos)
--    WITH CHECK = como a linha pode ficar depois (o topic_id novo,
--    ao mover de coleção, também tem que ser meu).
create policy "usuarios editam fontes dos seus topicos"
  on sources for update
  using (
    exists (select 1 from topics where topics.id = sources.topic_id and topics.user_id = auth.uid())
  )
  with check (
    exists (select 1 from topics where topics.id = sources.topic_id and topics.user_id = auth.uid())
  );


-- 3) Artigos lidos — mesmo formato de saved_articles (relação
--    usuário↔artigo, porque "lido" é por usuário, não do artigo).
create table read_articles (
    user_id    uuid not null references auth.users(id) on delete cascade,
    article_id uuid not null references articles(id) on delete cascade,
    read_at    timestamptz not null default now(),
    primary key (user_id, article_id)
);

-- "Lidos recentemente" ordena por read_at do usuário.
create index idx_read_articles_user_read_at on read_articles(user_id, read_at desc);

alter table read_articles enable row level security;

create policy "usuarios veem seus proprios lidos"
  on read_articles for select using (auth.uid() = user_id);
create policy "usuarios marcam lidos pra si mesmos"
  on read_articles for insert with check (auth.uid() = user_id);
create policy "usuarios desmarcam seus proprios lidos"
  on read_articles for delete using (auth.uid() = user_id);


-- 4) Contagem de não lidos por fonte (os números do menu lateral).
--    security_invoker = true faz a view rodar com as permissões de
--    quem consulta — ou seja, a RLS de articles continua valendo e
--    cada usuário só conta os próprios artigos. Sem isso, a view
--    rodaria como o dono (postgres) e ignoraria a RLS.
--    Janela de 30 dias, igual a Feedly: artigo velho não fica
--    "não lido" pra sempre inflando o contador.
create view unread_counts with (security_invoker = true) as
select a.source_id, count(*)::int as nao_lidos
from articles a
where a.collected_at > now() - interval '30 days'
  and not exists (
    select 1 from read_articles r
    where r.article_id = a.id and r.user_id = auth.uid()
  )
group by a.source_id;
