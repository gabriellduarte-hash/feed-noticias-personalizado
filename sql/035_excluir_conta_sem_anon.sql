-- ============================================================
-- 035_excluir_conta_sem_anon.sql
-- O revoke ... from public do sql/034 não tira a permissão que o Supabase
-- dá direto ao papel anon em funções novas do schema public. Sem efeito
-- prático (sem login, auth.uid() é nulo e a função não apaga nada), mas
-- quem não entrou não tem por que poder chamar "excluir minha conta".
-- ============================================================

revoke execute on function excluir_minha_conta() from anon;
