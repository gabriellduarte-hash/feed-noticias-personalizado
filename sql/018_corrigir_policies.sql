-- ============================================================
-- 018_corrigir_policies.sql
-- As policies que estão no banco não batem com o 007_enable_rls.sql
-- (conferido em pg_policies, 01/10):
--
--   sources: só tem SELECT e UPDATE. Faltam INSERT e DELETE — por isso
--            "Deixar de seguir" e o "x" do Organizar não apagavam nada,
--            e "Seguir" no catálogo não adicionava a fonte.
--   topics:  tem INSERT com o nome "atualizam" e um SELECT duplicado com
--            o nome "criam". Falta UPDATE (renomear coleção).
--
-- Detalhe importante: com RLS, um DELETE/UPDATE que nenhuma policy
-- permite NÃO dá erro — só afeta 0 linhas. Por isso a falha era
-- silenciosa. O hub agora confere quantas linhas mudaram e avisa.
--
-- Pra conferir antes e depois:
--   select tablename, cmd, policyname from pg_policies
--   where tablename in ('topics', 'sources') order by 1, 2;
-- ============================================================

begin;

-- topics -----------------------------------------------------
-- SELECT duplicado (mesma regra do "usuarios veem seus proprios topicos")
drop policy "usuarios criam topicos pra si mesmo" on topics;

-- A policy de INSERT existe, só está com o nome de outra
alter policy "usuarios atualizam seus proprios topicos" on topics
  rename to "usuarios criam topicos pra si mesmos";

create policy "usuarios atualizam seus proprios topicos"
  on topics for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- sources ----------------------------------------------------
create policy "usuarios criam fontes nos seus topicos"
  on sources for insert
  with check (
    exists (select 1 from topics where topics.id = sources.topic_id and topics.user_id = auth.uid())
  );

create policy "usuarios apagam fontes dos seus topicos"
  on sources for delete
  using (
    exists (select 1 from topics where topics.id = sources.topic_id and topics.user_id = auth.uid())
  );

commit;
