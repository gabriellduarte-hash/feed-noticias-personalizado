-- ============================================================
-- 034_feedback_e_conta.sql
-- Feedback pelas Configurações e "Excluir minha conta".
--
-- 1) feedback: o que as pessoas mandam em Configurações › Feedback. O hub
--    também manda por e-mail pro projeto; a tabela é o registro (e serve
--    pro limite de envios por hora). Cada um só grava e vê o próprio.
--    Some junto com a conta (on delete cascade).
--
-- 2) excluir_minha_conta(): apaga o usuário logado de auth.users. Todo o
--    resto (coleções, fontes, notícias, lidos, salvos, resumos,
--    destinatários, feedback) sai junto, em cascata. security definer
--    porque quem está logado não tem permissão direta em auth.users; a
--    função só apaga o próprio auth.uid(), nunca outro usuário.
-- ============================================================

set lock_timeout = '5s';

begin;

create table feedback (
    id        uuid primary key default gen_random_uuid(),
    user_id   uuid not null references auth.users(id) on delete cascade,
    tipo      text not null check (tipo in ('sugestao', 'problema', 'elogio', 'outro')),
    mensagem  text not null check (char_length(mensagem) between 1 and 2000),
    criado_em timestamptz not null default now()
);

alter table feedback enable row level security;

create policy "cada um envia o próprio feedback" on feedback
  for insert to authenticated with check (user_id = auth.uid());
create policy "cada um vê o próprio feedback" on feedback
  for select to authenticated using (user_id = auth.uid());

create function excluir_minha_conta()
returns void
language sql
security definer
set search_path = public
as $$
  delete from auth.users where id = auth.uid();
$$;

revoke all on function excluir_minha_conta() from public;
grant execute on function excluir_minha_conta() to authenticated;

commit;
