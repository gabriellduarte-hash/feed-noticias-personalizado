-- ============================================================
-- 026_reserva_resumo.sql
-- Reserva pro resumo da IA. A coleta de hora em hora e o workflow
-- "Fonte nova" podem rodar ao mesmo tempo; sem reserva, os dois pegariam
-- os mesmos artigos sem resumo e a IA seria paga duas vezes.
--
-- O resumir.py "reserva" um lote (resumo_reservado_em = agora) antes de
-- chamar a IA. Reserva com mais de 30 min conta como abandonada (o job
-- caiu) e pode ser pega de novo. resumo_tentativas evita insistir pra
-- sempre num artigo que a IA nunca consegue resumir (desiste após 3).
--
-- O resumir.py novo DEPENDE destas colunas: rode este SQL antes do push.
-- ============================================================

-- ALTER TABLE precisa de acesso exclusivo à tabela. Se algum job estiver
-- com ela ocupada, é melhor falhar em 5s (e rodar de novo depois) do que
-- ficar na fila: enquanto espera, o ALTER segura também quem chega
-- depois (inclusive as leituras do hub). Foi o que travou o 025 da
-- primeira vez.
set lock_timeout = '5s';

begin;

alter table articles add column resumo_reservado_em timestamptz;
alter table articles add column resumo_tentativas smallint not null default 0;

-- O resumir.py procura artigos sem categoria; índice parcial, só deles.
create index idx_articles_sem_resumo on articles (collected_at) where category is null;

commit;
