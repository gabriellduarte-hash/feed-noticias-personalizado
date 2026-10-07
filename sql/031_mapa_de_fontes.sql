-- ============================================================
-- 031_mapa_de_fontes.sql
-- O catálogo vira um mapa de fontes: centenas de veículos (do Brasil e
-- em inglês) catalogados e validados, mas coletados só quando alguém
-- segue. Rodar ANTES dos SQL de catálogo seguintes (032 e 033), que usam
-- as colunas novas.
--
-- 1) vitrine: as fontes que o coletar_catalogo.py busca de hora em hora
--    pra aba Explorar do Início. As 51 originais continuam (true); as 84
--    do sql/030 e as que entrarem daqui em diante ficam só no mapa
--    (false, o padrão). A separação é pela data de criação: as 84 do 030
--    entraram em 07/10 às 19:54.
-- 2) idioma ('pt' ou 'en') e regiao ("Minas Gerais", "EUA"...), pra busca
--    achar por lugar e pra mostrar de onde é a fonte.
-- 3) importar_noticias_existentes (sql/023): ao seguir uma fonte, traz só
--    as notícias das últimas 24 horas que já estavam no banco (antes
--    trazia tudo). Daí em diante a fonte é coletada como qualquer outra.
-- ============================================================

set lock_timeout = '5s';

begin;

alter table feed_catalog add column vitrine boolean not null default false;
alter table feed_catalog add column idioma text not null default 'pt'
  check (idioma in ('pt', 'en'));
alter table feed_catalog add column regiao text;

update feed_catalog set vitrine = true where created_at < '2026-10-07 22:00:00+00';

-- região das fontes regionais que já entraram pelo sql/030 (sem a coluna)
update feed_catalog set regiao = 'Amazonas' where regiao is null and url ~ '(://(www\.)?|site%3A)acritica\.com(/|&|$)';
update feed_catalog set regiao = 'Bahia' where regiao is null and url ~ '(://(www\.)?|site%3A)atarde\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Bahia' where regiao is null and url ~ '(://(www\.)?|site%3A)correio24horas\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Ceará' where regiao is null and url ~ '(://(www\.)?|site%3A)diariodonordeste\.verdesmares\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Ceará' where regiao is null and url ~ '(://(www\.)?|site%3A)opovo\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Distrito Federal' where regiao is null and url ~ '(://(www\.)?|site%3A)correiobraziliense\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Goiás' where regiao is null and url ~ '(://(www\.)?|site%3A)opopular\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Mato Grosso' where regiao is null and url ~ '(://(www\.)?|site%3A)gazetadigital\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Mato Grosso do Sul' where regiao is null and url ~ '(://(www\.)?|site%3A)campograndenews\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Minas Gerais' where regiao is null and url ~ '(://(www\.)?|site%3A)diariodocomercio\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Minas Gerais' where regiao is null and url ~ '(://(www\.)?|site%3A)em\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Minas Gerais' where regiao is null and url ~ '(://(www\.)?|site%3A)otempo\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Paraná' where regiao is null and url ~ '(://(www\.)?|site%3A)bemparana\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Paraná' where regiao is null and url ~ '(://(www\.)?|site%3A)gazetadopovo\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Pará' where regiao is null and url ~ '(://(www\.)?|site%3A)oliberal\.com(/|&|$)';
update feed_catalog set regiao = 'Pernambuco' where regiao is null and url ~ '(://(www\.)?|site%3A)diariodepernambuco\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Pernambuco' where regiao is null and url ~ '(://(www\.)?|site%3A)jc\.uol\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Rio Grande do Sul' where regiao is null and url ~ '(://(www\.)?|site%3A)correiodopovo\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Rio Grande do Sul' where regiao is null and url ~ '(://(www\.)?|site%3A)gauchazh\.clicrbs\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Rio Grande do Sul' where regiao is null and url ~ '(://(www\.)?|site%3A)jornaldocomercio\.com(/|&|$)';
update feed_catalog set regiao = 'Rio de Janeiro' where regiao is null and url ~ '(://(www\.)?|site%3A)extra\.globo\.com(/|&|$)';
update feed_catalog set regiao = 'Rio de Janeiro' where regiao is null and url ~ '(://(www\.)?|site%3A)jb\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Rio de Janeiro' where regiao is null and url ~ '(://(www\.)?|site%3A)odia\.ig\.com\.br(/|&|$)';
update feed_catalog set regiao = 'Santa Catarina' where regiao is null and url ~ '(://(www\.)?|site%3A)nsctotal\.com\.br(/|&|$)';
update feed_catalog set regiao = 'São Paulo' where regiao is null and url ~ '(://(www\.)?|site%3A)atribuna\.com\.br(/|&|$)';
update feed_catalog set regiao = 'São Paulo' where regiao is null and url ~ '(://(www\.)?|site%3A)meutimao\.com\.br(/|&|$)';

create or replace function importar_noticias_existentes(p_source_id uuid)
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  v_url text;
  v_total integer := 0;
  v_linhas integer;
begin
  select s.url into v_url
  from sources s
  join topics t on t.id = s.topic_id
  where s.id = p_source_id and t.user_id = auth.uid();

  if v_url is null then
    raise exception 'fonte não encontrada';
  end if;

  -- a) mesma URL de feed em outra fonte (outra coleção, outro usuário).
  --    Leva junto categoria e resumo da IA, que já foram pagos.
  insert into articles (source_id, title, url, content, published_at, author, image_url, category, ai_summary)
  select distinct on (a.url)
         p_source_id, a.title, a.url, a.content, a.published_at, a.author, a.image_url, a.category, a.ai_summary
  from articles a
  join sources s on s.id = a.source_id
  where s.url = v_url and s.id <> p_source_id
    and coalesce(a.published_at, a.collected_at) > now() - interval '24 hours'
  order by a.url, a.collected_at desc
  on conflict (source_id, url) do nothing;
  get diagnostics v_linhas = row_count;
  v_total := v_total + v_linhas;

  -- b) notícias do catálogo dessa mesma fonte (só existem pras da vitrine;
  --    sem resumo da IA: o resumir.py faz na próxima rodada)
  insert into articles (source_id, title, url, content, published_at, author, image_url)
  select p_source_id, c.title, c.url, c.content, c.published_at, c.author, c.image_url
  from catalog_articles c
  join feed_catalog f on f.id = c.catalog_id
  where f.url = v_url
    and coalesce(c.published_at, c.collected_at) > now() - interval '24 hours'
  on conflict (source_id, url) do nothing;
  get diagnostics v_linhas = row_count;
  v_total := v_total + v_linhas;

  return v_total;
end;
$$;

commit;
