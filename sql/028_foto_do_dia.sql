-- ============================================================
-- 028_foto_do_dia.sql
-- Foto de capa do e-mail do resumo diário, vinda do Unsplash.
--
-- Uma foto por dia, igual pra todo mundo: o enviar.py busca na primeira
-- vez que precisa no dia e guarda aqui; os outros envios do dia (cada
-- usuário recebe no seu horário) reaproveitam. Assim fica 1 chamada por
-- dia à API do Unsplash (o modo de teste deles permite 50 por hora).
--
-- As regras da API do Unsplash pedem crédito ao fotógrafo com link pro
-- perfil, por isso o nome e o link dele ficam guardados junto.
--
-- Só o coletor (conexão direta, sem RLS) lê e escreve aqui; pelo hub
-- ninguém acessa: RLS ligada e nenhuma policy.
-- ============================================================

create table foto_do_dia (
    dia           date primary key,
    url           text not null,   -- endereço da imagem devolvido pela API (as regras exigem usar esse)
    fotografo     text not null,
    fotografo_url text not null,   -- perfil no Unsplash
    unsplash_url  text not null,   -- página da foto
    criado_em     timestamptz not null default now()
);

alter table foto_do_dia enable row level security;
