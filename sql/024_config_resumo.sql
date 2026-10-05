-- ============================================================
-- 024_config_resumo.sql
-- Configurações do resumo diário por usuário (Configurações > Resumo
-- diário, no hub): ligado/desligado, horário de envio e quais coleções
-- entram no resumo.
--
-- Quem não tem linha aqui usa o padrão (ligado, 6h, todas as coleções).
-- Por isso não precisa preencher nada pra quem já existe.
-- ============================================================

create table digest_settings (
    user_id    uuid primary key references auth.users(id) on delete cascade,
    ativo      boolean not null default true,
    -- hora cheia no horário de Brasília (0 a 23)
    hora_envio smallint not null default 6 check (hora_envio between 0 and 23),
    -- null = todas as coleções; senão, só as desses tópicos.
    -- Array em vez de tabela de ligação: é uma lista curta, sempre lida
    -- e gravada inteira. Tópico apagado depois só deixa de casar com nada.
    topic_ids  uuid[],
    updated_at timestamptz not null default now()
);

alter table digest_settings enable row level security;

create policy "usuarios veem sua config de resumo"
  on digest_settings for select using (auth.uid() = user_id);
create policy "usuarios criam sua config de resumo"
  on digest_settings for insert with check (auth.uid() = user_id);
create policy "usuarios alteram sua config de resumo"
  on digest_settings for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
