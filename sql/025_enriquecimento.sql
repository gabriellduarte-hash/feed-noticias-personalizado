-- ============================================================
-- 025_enriquecimento.sql
-- Enriquecimento: a maioria dos feeds manda só um resumo curto (no
-- banco, só 28% das notícias de RSS tinham texto de verdade, e as de
-- sitemap/Google Notícias, nenhum). O coletor/enriquecer.py abre a página
-- de cada notícia nova e guarda o texto completo e a imagem.
--
-- enriquecido_em marca que a notícia JÁ FOI TENTADA (com sucesso ou
-- não). Sem isso, uma página que dá erro (site que bloqueia robôs) seria
-- tentada de novo a cada hora, pra sempre.
--
-- (Esta é a versão que rodou no banco em 05/10. A reserva do resumo da
-- IA, pensada depois, ficou no 026.)
-- ============================================================

alter table articles add column enriquecido_em timestamptz;
alter table catalog_articles add column enriquecido_em timestamptz;

-- O enriquecer.py procura "ainda não tentadas", das mais novas pras mais
-- antigas. Índice parcial: só guarda as linhas pendentes (as que
-- importam pra essa busca), então fica pequeno mesmo com a tabela grande.
create index idx_articles_enriquecer on articles (collected_at desc) where enriquecido_em is null;
create index idx_catalog_articles_enriquecer on catalog_articles (collected_at desc) where enriquecido_em is null;
