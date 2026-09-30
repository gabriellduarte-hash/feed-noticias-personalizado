-- ============================================================
-- 007_enable_rls.sql
-- Ativa Row Level Security nas 4 tabelas, com políticas por dono
-- (auth.uid()). Isso passa a valer só pra conexões que passam pelo
-- anon/authenticated role (a API do Supabase, usada pelo Next.js) —
-- o coletor/resumo/envio em Python conectam direto via DATABASE_URL
-- (role postgres) e continuam ignorando RLS normalmente, sem mudança
-- de comportamento pra eles.
-- ============================================================

-- topics: dono direto via user_id
alter table topics enable row level security;

create policy "usuarios veem seus proprios topicos"
  on topics for select
  using (auth.uid() = user_id);

create policy "usuarios criam topicos pra si mesmos"
  on topics for insert
  with check (auth.uid() = user_id);

create policy "usuarios atualizam seus proprios topicos"
  on topics for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "usuarios apagam seus proprios topicos"
  on topics for delete
  using (auth.uid() = user_id);


-- sources: dono indireto, via topics.user_id
alter table sources enable row level security;

create policy "usuarios veem fontes dos seus topicos"
  on sources for select
  using (
    exists (
      select 1 from topics
      where topics.id = sources.topic_id
        and topics.user_id = auth.uid()
    )
  );

create policy "usuarios criam fontes nos seus topicos"
  on sources for insert
  with check (
    exists (
      select 1 from topics
      where topics.id = sources.topic_id
        and topics.user_id = auth.uid()
    )
  );

create policy "usuarios apagam fontes dos seus topicos"
  on sources for delete
  using (
    exists (
      select 1 from topics
      where topics.id = sources.topic_id
        and topics.user_id = auth.uid()
    )
  );


-- articles: dono indireto, via sources -> topics.user_id (só leitura
-- pelo app; quem insere artigo é sempre o coletor Python, fora do RLS)
alter table articles enable row level security;

create policy "usuarios veem artigos dos seus topicos"
  on articles for select
  using (
    exists (
      select 1 from sources
      join topics on topics.id = sources.topic_id
      where sources.id = articles.source_id
        and topics.user_id = auth.uid()
    )
  );


-- digests: dono direto via user_id (só leitura; quem grava é sempre o
-- resumo/envio em Python, fora do RLS)
alter table digests enable row level security;

create policy "usuarios veem seus proprios digests"
  on digests for select
  using (auth.uid() = user_id);


-- Confere: todas as 4 tabelas devem aparecer com rowsecurity = true
select tablename, rowsecurity
from pg_tables
where schemaname = 'public'
order by tablename;
