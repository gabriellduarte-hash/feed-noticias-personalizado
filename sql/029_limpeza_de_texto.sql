-- ============================================================
-- 029_limpeza_de_texto.sql
-- Texto das notícias sem anúncio, cookies e chamadas do site
-- (coletor/texto.py e coletor/limpar_textos.py), e resumo da IA só
-- quando há texto de verdade (resumo/resumir.py).
--
-- 1) trechos_repetidos: parágrafos que o limpar_textos.py descobriu que
--    se repetem em várias matérias da mesma fonte (pedido de assinatura,
--    bio do autor, "Siga no WhatsApp", lista de outras matérias). Ficam
--    guardados pra sair das próximas matérias logo de cara, mesmo de
--    fontes que publicam pouco.
--    fonte_id é sources.id (fontes dos usuários) ou feed_catalog.id
--    (catálogo). Só o coletor usa: RLS ligada e nenhuma policy.
--    visto_em: última vez que o trecho saiu de alguma matéria. Trecho que
--    passa 30 dias sem aparecer é apagado sozinho (assim um acerto por
--    engano, como um parágrafo de contexto repetido numa série de
--    matérias, não fica pra sempre). Pra tirar um na hora, é só apagar
--    a linha.
--
-- 2) Apaga os resumos da IA feitos sem texto, só com o título (a maioria
--    das notícias que chegam pelo Google Notícias). Eram paráfrase do
--    título, e a IA podia inventar detalhe. A categoria fica; no hub a
--    notícia aparece com título e link.
-- ============================================================

set lock_timeout = '5s';

begin;

create table trechos_repetidos (
    fonte_id  uuid not null,
    trecho    text not null,
    visto_em  timestamptz not null default now(),
    primary key (fonte_id, trecho)
);

alter table trechos_repetidos enable row level security;

update articles
set ai_summary = null
where ai_summary is not null
  and length(coalesce(content, '')) < 400;

commit;
