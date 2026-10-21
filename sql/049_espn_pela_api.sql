-- ============================================================
-- 049_espn_pela_api.sql
-- Rode ANTES de subir o coletor desta leva.
--
-- A ESPN barra as máquinas do GitHub no site, e o RSS dela não traz nem
-- resumo nem foto: ela ia pro hub (Vercel), que lia o RSS e abria as
-- páginas. Agora o coletor lê pela API pública de conteúdo da ESPN
-- (coletor/apis.py): lista, texto completo e foto numa chamada só, sem
-- o hub. Se a API também barrar o GitHub, o coletor marca a fonte pro hub
-- de novo, sozinho (o caminho de antes).
-- ============================================================

update feeds set coletar_pelo_hub = false
where url ~* '^https?://(www\.)?espn\.com(\.br)?/';

update feed_catalog set coletar_pelo_hub = false
where url ~* '^https?://(www\.)?espn\.com(\.br)?/';
