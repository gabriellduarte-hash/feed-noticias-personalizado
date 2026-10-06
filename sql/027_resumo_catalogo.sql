-- ============================================================
-- 027_resumo_catalogo.sql
-- Resumo da IA também para as notícias do catálogo (aba Explorar),
-- com a mesma reserva do 026 (dois jobs não pegam a mesma notícia).
--
-- Só vale a pena resumir notícia com texto de verdade (que veio no feed
-- ou pelo enriquecimento): resumir só um título gera texto vazio de
-- sentido. Por isso o índice abaixo já considera só as que têm conteúdo.
--
-- Custo: o resumir.py tem um teto por hora pro catálogo
-- (MAX_CATALOGO_POR_RODADA), porque o catálogo recebe mil ou mais
-- notícias por dia.
-- ============================================================

set lock_timeout = '5s';

begin;

alter table catalog_articles add column ai_summary text;
alter table catalog_articles add column resumo_reservado_em timestamptz;
alter table catalog_articles add column resumo_tentativas smallint not null default 0;

create index idx_catalog_articles_sem_resumo
  on catalog_articles (collected_at desc)
  where ai_summary is null and content is not null;

commit;
