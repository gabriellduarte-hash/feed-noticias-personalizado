-- ============================================================
-- 038_fontes_compartilhadas.sql  (parte 1 de 2: EXPANDIR)
-- Rode DEPOIS do 037 e ANTES de subir o coletor e o hub desta leva.
-- A parte 2 (039) só depois do push, quando o código novo estiver no ar.
--
-- Até aqui, cada pessoa tinha a sua cópia da fonte: se duas seguiam o
-- mesmo site, ele era coletado duas vezes e as notícias ficavam
-- duplicadas. Agora:
--   feeds    a fonte em si, uma por URL, coletada uma vez só;
--   sources  "seguir": o vínculo de uma pessoa com um feed, numa coleção
--            (nome personalizado, favorita e a última visita ficam aqui);
--   articles pertencem ao feed. Quem segue vê; quem deixa de seguir apaga
--            só o próprio vínculo, as notícias continuam pra quem segue.
-- "Lido" e "salvo" já eram por pessoa (read_articles, saved_articles).
--
-- Por que em duas partes: esta só ACRESCENTA (tabela, colunas, view,
-- funções), então o código antigo continua funcionando até o push. Os
-- gatilhos preenchem o feed do que o código antigo gravar nesse meio
-- tempo. A 039 tira o que ficou velho.
--
-- Contador do site: deixa de ser "não lidas dos últimos 30 dias" e vira
-- "novas desde a última visita" (sources.visto_em, view novas_por_fonte).
-- ============================================================

set lock_timeout = '5s';

begin;

-- 1) feeds ----------------------------------------------------------------

create table feeds (
  id uuid primary key default gen_random_uuid(),
  url text not null unique,
  type text not null default 'rss' check (type in ('rss', 'scrape', 'sitemap')),
  name text,
  created_at timestamptz not null default now()
);

-- Sem políticas: o hub não lê feeds direto (usa sources e a view abaixo).
-- O coletor (postgres) e as funções security definer passam pelo RLS.
alter table feeds enable row level security;
revoke all on feeds from anon, authenticated;

insert into feeds (url, type, name, created_at)
select distinct on (url) url, type, name, created_at
from sources
order by url, created_at;

-- 2) sources vira "seguir" ------------------------------------------------

alter table sources add column feed_id uuid references feeds (id) on delete cascade;
-- última visita: começa agora, pra ninguém abrir o site com "999 novas"
alter table sources add column visto_em timestamptz not null default now();

update sources s set feed_id = f.id from feeds f where f.url = s.url;
alter table sources alter column feed_id set not null;
create index idx_sources_feed_id on sources (feed_id);

-- 3) articles passam a ser do feed ---------------------------------------

alter table articles add column feed_id uuid references feeds (id) on delete cascade;
update articles a set feed_id = s.feed_id from sources s where s.id = a.source_id;

-- A mesma notícia em duas fontes que agora são o mesmo feed (hoje não
-- há nenhuma, mas a regra vale): fica a mais antiga, e "lido"/"salvo" de
-- quem marcou a outra vão pra ela.
create temporary table duplicadas on commit drop as
select id, first_value(id) over (partition by feed_id, url order by collected_at, id) as fica
from articles;
delete from duplicadas where id = fica;

insert into read_articles (user_id, article_id, read_at)
select r.user_id, d.fica, r.read_at
from read_articles r join duplicadas d on d.id = r.article_id
on conflict do nothing;

insert into saved_articles (user_id, article_id, created_at)
select sv.user_id, d.fica, sv.created_at
from saved_articles sv join duplicadas d on d.id = sv.article_id
on conflict do nothing;

delete from articles a using duplicadas d where a.id = d.id;

alter table articles alter column feed_id set not null;
-- o código novo grava sem source_id; a coluna sai na 039
alter table articles alter column source_id drop not null;
alter table articles add constraint articles_feed_url_key unique (feed_id, url);
create index idx_articles_feed_collected on articles (feed_id, collected_at desc);

-- 4) transição: o código antigo grava sem feed_id --------------------------

create function preencher_feed() returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  if tg_table_name = 'sources' then
    if new.feed_id is null then
      insert into feeds (url, type, name)
      values (new.url, coalesce(new.type, 'rss'), new.name)
      on conflict (url) do nothing;
      select id into new.feed_id from feeds where url = new.url;
    end if;
  elsif new.feed_id is null and new.source_id is not null then
    select feed_id into new.feed_id from sources where id = new.source_id;
  end if;
  return new;
end;
$$;
revoke execute on function preencher_feed() from public, anon, authenticated;

create trigger sources_preencher_feed before insert on sources
  for each row execute function preencher_feed();
create trigger articles_preencher_feed before insert on articles
  for each row execute function preencher_feed();

-- 5) quem vê o quê ------------------------------------------------------

create policy "usuarios veem artigos dos feeds que seguem" on articles
  for select to authenticated
  using (exists (
    select 1
    from sources s
    join topics t on t.id = s.topic_id
    where s.feed_id = articles.feed_id and t.user_id = (select auth.uid())
  ));

-- Notícias com a fonte de quem está vendo (nome personalizado, coleção).
-- security_invoker: valem o RLS de articles e de sources de quem consulta.
create view artigos_do_usuario with (security_invoker = true) as
select a.id, a.title, a.url, a.author, a.content, a.ai_summary, a.category, a.image_url,
       a.published_at, a.collected_at, a.palavras_chave, a.feed_id,
       s.id as source_id, s.name as fonte_nome, s.url as fonte_url, s.topic_id
from articles a
join sources s on s.feed_id = a.feed_id;
revoke all on artigos_do_usuario from anon;
grant select on artigos_do_usuario to authenticated;

-- 6) contadores -----------------------------------------------------------

-- Não lidas (30 dias): continua existindo pro "marcar todas como lidas".
-- Mesmas colunas de antes, então o código antigo segue funcionando.
create or replace view unread_counts with (security_invoker = true) as
select s.id as source_id, count(*)::integer as nao_lidos
from sources s
join articles a on a.feed_id = s.feed_id
where a.collected_at > now() - interval '30 days'
  and not exists (
    select 1 from read_articles r
    where r.article_id = a.id and r.user_id = (select auth.uid())
  )
group by s.id;

-- O número do menu: o que chegou desde a última visita àquela fonte.
create view novas_por_fonte with (security_invoker = true) as
select s.id as source_id, count(*)::integer as novas
from sources s
join articles a on a.feed_id = s.feed_id
where a.collected_at > s.visto_em
group by s.id;
revoke all on novas_por_fonte from anon;
grant select on novas_por_fonte to authenticated;

-- 7) funções do hub -------------------------------------------------------

-- Seguir: acha (ou cria) o feed da URL e cria o vínculo na coleção.
-- feed_novo = ninguém seguia: o hub coleta na hora e importa do catálogo.
create function seguir_fonte(p_topic_id uuid, p_url text, p_tipo text default 'rss', p_nome text default null)
returns table (fonte_id uuid, feed uuid, feed_novo boolean)
language plpgsql
security definer
set search_path = public
as $$
declare
  v_feed uuid;
  v_fonte uuid;
begin
  if not exists (select 1 from topics where id = p_topic_id and user_id = auth.uid()) then
    raise exception 'coleção não encontrada';
  end if;

  insert into feeds (url, type, name)
  values (p_url, coalesce(p_tipo, 'rss'), p_nome)
  on conflict (url) do nothing
  returning id into v_feed;
  feed_novo := v_feed is not null;
  if v_feed is null then
    select id into v_feed from feeds where url = p_url;
  end if;

  insert into sources (topic_id, url, type, name, feed_id)
  values (p_topic_id, p_url, coalesce(p_tipo, 'rss'), p_nome, v_feed)
  returning id into v_fonte;

  fonte_id := v_fonte;
  feed := v_feed;
  return next;
end;
$$;

-- Ao seguir um feed novo que está no catálogo: as notícias das últimas
-- 24h que o catálogo já tem (sem resumo: a IA faz na próxima rodada).
create function importar_do_catalogo(p_fonte_id uuid) returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  v_feed uuid;
  v_url text;
  v_total integer;
begin
  select s.feed_id, s.url into v_feed, v_url
  from sources s
  join topics t on t.id = s.topic_id
  where s.id = p_fonte_id and t.user_id = auth.uid();

  if v_feed is null then
    raise exception 'fonte não encontrada';
  end if;

  insert into articles (feed_id, title, url, content, published_at, author, image_url)
  select v_feed, c.title, c.url, c.content, c.published_at, c.author, c.image_url
  from catalog_articles c
  join feed_catalog f on f.id = c.catalog_id
  where f.url = v_url
    and coalesce(c.published_at, c.collected_at) > now() - interval '24 hours'
  on conflict (feed_id, url) do nothing;
  get diagnostics v_total = row_count;
  return v_total;
end;
$$;

-- Abriu uma fonte, uma coleção ou o feed todo: zera o contador de novas.
create function registrar_visita(p_fonte uuid default null, p_topico uuid default null) returns void
language sql
security invoker
set search_path = public
as $$
  update sources s
  set visto_em = now()
  from topics t
  where t.id = s.topic_id
    and t.user_id = auth.uid()
    and (p_fonte is null or s.id = p_fonte)
    and (p_topico is null or s.topic_id = p_topico);
$$;

revoke execute on function seguir_fonte(uuid, text, text, text) from public, anon;
revoke execute on function importar_do_catalogo(uuid) from public, anon;
revoke execute on function registrar_visita(uuid, uuid) from public, anon;
grant execute on function seguir_fonte(uuid, text, text, text) to authenticated;
grant execute on function importar_do_catalogo(uuid) to authenticated;
grant execute on function registrar_visita(uuid, uuid) to authenticated;

commit;
