-- ============================================================
-- 015_digest_recipients.sql
-- Lista de e-mails extras pra receber o digest diário, além do dono
-- (FEED_TO_EMAIL). Limite de 10 por usuário é conferido no código
-- (Server Action), não aqui — não precisa de trigger pra esse volume.
-- ============================================================

create table digest_recipients (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    email text not null,
    created_at timestamptz not null default now(),
    unique (user_id, email)
);

alter table digest_recipients enable row level security;

create policy "usuarios veem seus proprios destinatarios"
  on digest_recipients for select
  using (auth.uid() = user_id);

create policy "usuarios adicionam destinatarios pra si mesmos"
  on digest_recipients for insert
  with check (auth.uid() = user_id);

create policy "usuarios removem seus proprios destinatarios"
  on digest_recipients for delete
  using (auth.uid() = user_id);
