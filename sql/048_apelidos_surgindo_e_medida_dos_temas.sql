-- ============================================================
-- 048_apelidos_surgindo_e_medida_dos_temas.sql
-- Rode ANTES de subir o coletor e o hub desta leva.
--
-- Próximas fases do plano de temas (log de 15/10, parte 2):
-- 1) apelidos: "lula" = "luiz inacio lula da silva", "trump" = "donald
--    trump". O classificar.py descobre de hora em hora (o nome curto que
--    quase sempre aparece junto do mesmo nome longo, só pessoas) e grava
--    as duas chaves nas notícias: quem segue um acha as do outro.
-- 2) sugestoes_seguir.em_alta: nomes que surgiram (muito mais citados nas
--    últimas 24h do que nos 6 dias antes, em 2+ histórias e 3+ sites).
--    A aba Temas mostra "Surgindo agora".
-- 3) relacionados(): os temas e nomes que mais aparecem junto de um tema
--    (Marvel -> Super-heróis, Filmes...). A página do tema mostra.
-- 4) Medir os temas:
--    - relatorio_temas(): quantas notícias ganham tema, os temas sem
--      notícia, exemplos sem tema (Relatórios, chave secreta);
--    - temas_avaliados: amostra de notícias com os temas que receberam,
--      marcada à mão em Relatórios › Temas certos? (quais estão errados).
-- ============================================================

set lock_timeout = '5s';

begin;

-- 1) apelidos ----------------------------------------------------------------

create table apelidos (
  curto text primary key,            -- "lula"
  longo text not null,               -- "luiz inacio lula da silva"
  vezes int not null,                -- notícias com os dois juntos (7 dias)
  atualizado_em timestamptz not null default now()
);
alter table apelidos enable row level security;
revoke all on apelidos from anon, authenticated;

-- 2) surgindo agora ------------------------------------------------------------

alter table sugestoes_seguir add column em_alta real;

-- 3) temas relacionados --------------------------------------------------------
-- Nas notícias dos últimos 7 dias com o tema (ou nome), os outros temas e
-- nomes que mais aparecem. Das fontes da pessoa e do catálogo.

create function relacionados(p_tipo text, p_chave text)
returns table (tipo text, chave text, rotulo text, noticias int)
language sql
stable
security invoker
set search_path = public
as $$
  with alvo as (
    select a.url, a.temas, a.entidades from artigos_do_usuario a
    where a.collected_at > now() - interval '7 days'
      and ((p_tipo = 'tema' and p_chave = any(a.temas)) or (p_tipo = 'nome' and p_chave = any(a.palavras_chave)))
    union
    select c.url, c.temas, c.entidades from catalog_articles c
    where c.collected_at > now() - interval '7 days'
      and ((p_tipo = 'tema' and p_chave = any(c.temas)) or (p_tipo = 'nome' and p_chave = any(c.palavras_chave)))
  ),
  temas as (
    select 'tema'::text, t, t, count(distinct a.url)::int as n
    from alvo a, unnest(a.temas) t
    where not (p_tipo = 'tema' and t = p_chave)
    group by t
    order by n desc
    limit 6
  ),
  nomes as (
    select 'nome'::text, e->>'chave', mode() within group (order by e->>'nome'), count(distinct a.url)::int as n
    from alvo a, jsonb_array_elements(coalesce(a.entidades, '[]')) e
    where not (p_tipo = 'nome' and e->>'chave' = p_chave)
    group by e->>'chave'
    having count(distinct a.url) >= 2
    order by n desc
    limit 8
  )
  select * from temas
  union all
  select * from nomes;
$$;

revoke execute on function relacionados(text, text) from public, anon;
grant execute on function relacionados(text, text) to authenticated;

-- 4) medir os temas ------------------------------------------------------------

-- a amostra: o coletor sorteia notícias com tema; quem administra marca os errados
create table temas_avaliados (
  id bigint generated always as identity primary key,
  url text not null unique,
  titulo text not null,
  trecho text,
  fonte text,
  categoria text,
  temas text[] not null,             -- os que o classificar.py deu (sem o amplo)
  errados text[],                    -- os que a pessoa marcou como errados
  faltou text,                       -- tema que deveria ter vindo (texto livre)
  respondido_em timestamptz,
  criado_em timestamptz not null default now()
);
create index idx_temas_avaliados_pendentes on temas_avaliados (id) where respondido_em is null;

alter table temas_avaliados enable row level security;
revoke all on temas_avaliados from anon, authenticated;

-- Os temas amplos (as categorias) não contam como "tema específico"
create function relatorio_temas()
returns jsonb
language sql
stable
security invoker
set search_path = public
as $$
  with amplos as (
    select array['Política', 'Mundo', 'Finanças', 'Tecnologia', 'Games', 'Cinema', 'Entretenimento',
                 'Esportes', 'Saúde', 'Ciência', 'Humor'] as nomes
  ),
  noticias as (
    select n.title, n.temas, n.collected_at,
           exists (select 1 from unnest(n.temas) t, amplos where not (t = any(amplos.nomes))) as tem_especifico
    from (
      select title, temas, collected_at from articles where collected_at > now() - interval '3 days'
      union all
      select title, temas, collected_at from catalog_articles where collected_at > now() - interval '3 days'
    ) n
  )
  select jsonb_build_object(
    'total', (select count(*) from noticias),
    'com_tema', (select count(*) from noticias where tem_especifico),
    'sem_noticia', (
      select coalesce(jsonb_agg(c.nome order by c.ordem), '[]') from catalogo_temas c, amplos
      where not (c.nome = any(amplos.nomes))
        and not exists (select 1 from sugestoes_seguir s where s.tipo = 'tema' and s.chave = c.nome)
    ),
    'exemplos_sem_tema', (
      select coalesce(jsonb_agg(title), '[]') from (
        select title from noticias where not tem_especifico order by collected_at desc limit 15
      ) x
    ),
    'avaliacao', (
      select coalesce(jsonb_agg(jsonb_build_object('tema', tema, 'avaliados', avaliados, 'errados', errados)
                                order by avaliados desc), '[]')
      from (
        select t as tema, count(*)::int as avaliados, count(*) filter (where t = any(a.errados))::int as errados
        from temas_avaliados a, unnest(a.temas) t
        where a.respondido_em is not null
        group by t
      ) x
    )
  );
$$;

-- relatorio_temas lê temas_avaliados: só com a chave secreta
revoke execute on function relatorio_temas() from public, anon, authenticated;
grant execute on function relatorio_temas() to service_role;

commit;
