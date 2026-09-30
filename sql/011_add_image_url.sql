-- ============================================================
-- 011_add_image_url.sql
-- Capa do artigo. Nullable — muitos feeds/páginas não expõem imagem
-- de jeito nenhum (confirmado na prática com nossas 2 fontes atuais).
-- ============================================================

alter table articles add column image_url text;
