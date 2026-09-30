-- ============================================================
-- 010_unique_topic_url.sql
-- Impede cadastrar a mesma URL duas vezes no mesmo tópico — é o que
-- causou a duplicata de 28/09 (rodamos sql/002 e sql/003 duas vezes
-- sem querer). Por tópico, não global: a mesma URL pode fazer sentido
-- em tópicos diferentes.
-- ============================================================

alter table sources add constraint sources_topic_id_url_key unique (topic_id, url);
