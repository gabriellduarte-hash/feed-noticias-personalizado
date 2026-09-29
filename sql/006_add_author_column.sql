-- ============================================================
-- 006_add_author_column.sql
-- Adiciona coluna de autor em articles. Nullable porque nem todo
-- feed RSS ou página raspada informa autor de forma confiável.
-- ============================================================

alter table articles add column author text;
