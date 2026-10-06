-- ============================================================
-- 025_enriquecimento.sql
-- Duas coisas que o volume maior de notícias pediu:
--
-- 1) Enriquecimento: a maioria dos feeds manda só um resumo curto (só
--    28% das notícias de RSS tinham texto de verdade). O
--    coletor/enriquecer.py abre a página de cada notícia nova e guarda o
--    texto completo e a imagem. enriquecido_em marca que a notícia já
--    foi tentada, com ou sem sucesso (senão, um site que bloqueia seria
--    tentado a cada hora, pra sempre).
--
-- 2) Reserva pro resumo da IA: a coleta de hora em hora e o workflow
--    "Fonte nova" podem rodar ao mesmo tempo. Sem reserva, os dois
--    pegariam os mesmos artigos sem resumo e a IA seria paga duas vezes.
--    O resumir.py "reserva" um lote (resumo_reservado_em = agora) antes
--    de chamar a IA; reserva com mais de 30 min conta como abandonada
--    (o job caiu) e pode ser pega de novo. resumo_tentativas evita
--    insistir pra sempre num artigo que a IA nunca consegue resumir.
-- ============================================================

-- ALTER TABLE precisa de acesso exclusivo à tabela. Se algum job estiver
-- com ela ocupada, é melhor falhar em 5s (e rodar de novo depois) do que
-- ficar na fila: enquanto espera, o ALTER segura também quem chega
-- depois (inclusive as leituras do hub).
set lock_timeout = '5s';

begin;

alter table articles add column enriquecido_em timestamptz;
alter table catalog_articles add column enriquecido_em timestamptz;

alter table articles add column resumo_reservado_em timestamptz;
alter table articles add column resumo_tentativas smallint not null default 0;

-- Índices parciais: só guardam as linhas pendentes (as que as buscas
-- dos scripts procuram), então ficam pequenos mesmo com a tabela grande.
create index idx_articles_enriquecer on articles (collected_at desc) where enriquecido_em is null;
create index idx_catalog_articles_enriquecer on catalog_articles (collected_at desc) where enriquecido_em is null;
create index idx_articles_sem_resumo on articles (collected_at) where category is null;

commit;

-- (O limite pra transação parada fica nos próprios scripts, em db.py, e
-- não no banco: assim não afeta mais nada que use o usuário postgres.)
