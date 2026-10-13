-- ============================================================
-- 043_relatorios_de_uso.sql
-- Rode ANTES de subir o hub desta leva.
--
-- Base pros relatórios de uso (página Relatórios, só pra quem administra):
-- o que as pessoas leem, buscam e seguem, pra decidir o que entra no
-- catálogo e na vitrine. Tudo agregado: o relatório nunca mostra o que
-- uma pessoa específica fez.
--
-- 1) eventos: o mínimo que faltava registrar.
--    - abriu:            notícia aberta no leitor, e de onde (feed,
--                        explorar, trending, busca, salvos, lidos);
--    - buscou:           termo e quantos resultados (busca de notícias e
--                        de fontes; busca sem resultado = fonte faltando);
--    - seguiu / deixou_de_seguir: o feed, e por qual caminho (catálogo,
--                        link colado, busca na web).
--    Some com a conta (cascade) e depois de 90 dias (coletor apaga).
--    Cada um só grava os próprios; ninguém lê direto (nem a própria
--    pessoa): só a função do relatório, chamada com a chave secreta.
-- 2) read_articles.origem: "lida" deixa de misturar abrir a notícia com
--    "marcar tudo como lido". As antigas gravadas em lote (mesmo instante)
--    viram "tudo".
-- 3) relatorio_uso(dias): todos os números num jsonb só.
-- ============================================================

set lock_timeout = '5s';

begin;

-- 1) eventos --------------------------------------------------------------

create table eventos (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  tipo text not null check (tipo in ('abriu', 'buscou', 'seguiu', 'deixou_de_seguir')),
  origem text check (origem is null or length(origem) <= 20),
  categoria text check (categoria is null or length(categoria) <= 40),
  -- abriu: o site da notícia; seguiu/deixou: a URL do feed
  fonte text check (fonte is null or length(fonte) <= 300),
  -- articles.id ou catalog_articles.id (sem chave estrangeira: a notícia
  -- do catálogo é apagada depois de alguns dias, o evento fica)
  noticia_id uuid,
  termo text check (termo is null or length(termo) <= 120),
  resultados int,
  criado_em timestamptz not null default now()
);
create index idx_eventos_tipo_data on eventos (tipo, criado_em desc);

alter table eventos enable row level security;
revoke all on eventos from anon, authenticated;
grant insert on eventos to authenticated;
create policy "cada um registra os próprios eventos" on eventos
  for insert to authenticated
  with check (user_id = (select auth.uid()));

-- A mesma busca refeita na mesma meia hora (a página recarrega ao seguir
-- uma fonte, ao trocar de filtro) conta uma vez só. Definer porque
-- ninguém lê a tabela de eventos direto.
create function registrar_busca(p_termo text, p_origem text, p_resultados int) returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  v_termo text := lower(btrim(left(p_termo, 120)));
begin
  if auth.uid() is null or v_termo = '' or p_origem not in ('noticias', 'fontes') then
    return;
  end if;
  if exists (
    select 1 from eventos
    where user_id = auth.uid() and tipo = 'buscou' and origem = p_origem and termo = v_termo
      and criado_em > now() - interval '30 minutes'
  ) then
    return;
  end if;
  insert into eventos (user_id, tipo, origem, termo, resultados)
  values (auth.uid(), 'buscou', p_origem, v_termo, p_resultados);
end;
$$;
revoke execute on function registrar_busca(text, text, int) from public, anon;
grant execute on function registrar_busca(text, text, int) to authenticated;

-- 2) origem do "lido" ---------------------------------------------------------

alter table read_articles add column origem text
  check (origem is null or origem in ('abriu', 'marcou', 'tudo'));

update read_articles r set origem = 'tudo'
from (
  select user_id, read_at from read_articles group by 1, 2 having count(*) > 3
) lote
where lote.user_id = r.user_id and lote.read_at = r.read_at;

-- 3) relatório ----------------------------------------------------------------

create function relatorio_uso(p_dias int default 30) returns jsonb
language sql
stable
security definer
set search_path = public
as $$
  with
  periodo as (select now() - make_interval(days => greatest(1, least(p_dias, 365))) as desde),
  aberturas as (
    select e.* from eventos e, periodo p where e.tipo = 'abriu' and e.criado_em > p.desde
  ),
  buscas as (
    select e.* from eventos e, periodo p where e.tipo = 'buscou' and e.criado_em > p.desde
  ),
  ativos as (
    select e.user_id, e.criado_em as quando from eventos e
    union all
    select r.user_id, r.read_at from read_articles r where r.origem is distinct from 'tudo'
  ),
  seguidores as (
    select f.url, f.name, count(s.id) as n,
           exists (select 1 from feed_catalog c where c.url = f.url) as no_catalogo,
           exists (select 1 from feed_catalog c where c.url = f.url and c.vitrine) as na_vitrine
    from feeds f join sources s on s.feed_id = f.id
    group by f.id
  )
  select jsonb_build_object(
    'dias', greatest(1, least(p_dias, 365)),
    'gerado_em', now(),
    'usuarios', (
      select jsonb_build_object(
        'total', count(*),
        'novos', count(*) filter (where u.created_at > (select desde from periodo)),
        'ativos_7d', (select count(distinct user_id) from ativos where quando > now() - interval '7 days'),
        'ativos_periodo', (select count(distinct user_id) from ativos where quando > (select desde from periodo)),
        'resumo_ligado', (select count(*) from auth.users u2
                          where coalesce((select d.ativo from digest_settings d where d.user_id = u2.id), true)),
        'resumos_enviados', (select count(*) from digests d where d.sent_at > (select desde from periodo))
      )
      from auth.users u
    ),
    'aberturas', (select count(*) from aberturas),
    'aberturas_por_origem', (
      select coalesce(jsonb_agg(jsonb_build_object('nome', origem, 'total', n) order by n desc), '[]')
      from (select coalesce(origem, '?') as origem, count(*) as n from aberturas group by 1) t
    ),
    'categorias', (
      select coalesce(jsonb_agg(jsonb_build_object('nome', categoria, 'total', n, 'pessoas', pessoas) order by n desc), '[]')
      from (select categoria, count(*) as n, count(distinct user_id) as pessoas
            from aberturas where categoria is not null group by 1 order by 2 desc limit 15) t
    ),
    -- antes dos eventos: o que foi lido no feed (sem o "marcar tudo")
    'categorias_lidas_no_feed', (
      select coalesce(jsonb_agg(jsonb_build_object('nome', categoria, 'total', n) order by n desc), '[]')
      from (select a.category as categoria, count(*) as n
            from read_articles r join articles a on a.id = r.article_id, periodo p
            where r.read_at > p.desde and r.origem is distinct from 'tudo' and a.category is not null
            group by 1 order by 2 desc limit 15) t
    ),
    'sites_mais_abertos', (
      select coalesce(jsonb_agg(jsonb_build_object('nome', fonte, 'total', n, 'pessoas', pessoas) order by n desc), '[]')
      from (select fonte, count(*) as n, count(distinct user_id) as pessoas
            from aberturas where fonte is not null group by 1 order by 2 desc limit 15) t
    ),
    'assuntos', (
      select coalesce(jsonb_agg(jsonb_build_object('nome', p, 'total', n) order by n desc), '[]')
      from (
        select p, count(*) as n
        from aberturas e
        left join articles a on a.id = e.noticia_id
        left join catalog_articles c on c.id = e.noticia_id
        cross join lateral unnest(coalesce(a.palavras_chave, c.palavras_chave, '{}')) as p
        group by 1 order by 2 desc limit 20
      ) t
    ),
    'horarios', (
      select coalesce(jsonb_agg(jsonb_build_object('hora', h, 'total', n) order by h), '[]')
      from (select extract(hour from criado_em at time zone 'America/Sao_Paulo')::int as h, count(*) as n
            from aberturas group by 1) t
    ),
    'fontes_mais_seguidas', (
      select coalesce(jsonb_agg(jsonb_build_object('nome', coalesce(name, url), 'url', url, 'seguidores', n,
                                                   'no_catalogo', no_catalogo, 'na_vitrine', na_vitrine) order by n desc), '[]')
      from (select * from seguidores order by n desc limit 20) t
    ),
    -- seguidas por link e que não estão no catálogo: candidatas a entrar
    'candidatas_ao_catalogo', (
      select coalesce(jsonb_agg(jsonb_build_object('nome', coalesce(name, url), 'url', url, 'seguidores', n) order by n desc), '[]')
      from (select * from seguidores where not no_catalogo order by n desc limit 20) t
    ),
    -- no catálogo, seguidas, mas fora da vitrine (aba Explorar): candidatas à vitrine
    'candidatas_a_vitrine', (
      select coalesce(jsonb_agg(jsonb_build_object('nome', coalesce(name, url), 'url', url, 'seguidores', n) order by n desc), '[]')
      from (select * from seguidores where no_catalogo and not na_vitrine order by n desc limit 20) t
    ),
    'seguiram_por_caminho', (
      select coalesce(jsonb_agg(jsonb_build_object('nome', origem, 'total', n) order by n desc), '[]')
      from (select coalesce(e.origem, '?') as origem, count(*) as n
            from eventos e, periodo p where e.tipo = 'seguiu' and e.criado_em > p.desde group by 1) t
    ),
    'deixaram_de_seguir', (
      select coalesce(jsonb_agg(jsonb_build_object('nome', fonte, 'total', n) order by n desc), '[]')
      from (select e.fonte, count(*) as n from eventos e, periodo p
            where e.tipo = 'deixou_de_seguir' and e.criado_em > p.desde and e.fonte is not null
            group by 1 order by 2 desc limit 10) t
    ),
    'buscas', (
      select coalesce(jsonb_agg(jsonb_build_object('termo', termo, 'onde', origem, 'pessoas', pessoas, 'vezes', n,
                                                   'resultados', resultados) order by pessoas desc, n desc), '[]')
      from (select lower(termo) as termo, origem, count(distinct user_id) as pessoas, count(*) as n,
                   round(avg(resultados))::int as resultados
            from buscas where termo is not null group by 1, 2 order by 3 desc, 4 desc limit 20) t
    ),
    -- buscou e não achou: o sinal mais direto de fonte ou assunto faltando
    'buscas_sem_resultado', (
      select coalesce(jsonb_agg(jsonb_build_object('termo', termo, 'onde', origem, 'pessoas', pessoas, 'vezes', n)
                                order by pessoas desc, n desc), '[]')
      from (select lower(termo) as termo, origem, count(distinct user_id) as pessoas, count(*) as n
            from buscas where termo is not null and coalesce(resultados, 0) = 0
            group by 1, 2 order by 3 desc, 4 desc limit 20) t
    ),
    'colecoes', (
      select coalesce(jsonb_agg(jsonb_build_object('nome', nome, 'total', n) order by n desc), '[]')
      from (select lower(btrim(name)) as nome, count(*) as n from topics group by 1 order by 2 desc limit 15) t
    )
  );
$$;

revoke execute on function relatorio_uso(int) from public, anon, authenticated;
grant execute on function relatorio_uso(int) to service_role;

commit;
