-- ============================================================
-- 023_noticias_ao_adicionar_fonte.sql
-- Faz uma fonte recém-adicionada já aparecer com notícias, sem esperar
-- a coleta das 6h:
--   1. aproveita notícias que já estão no banco (mesma fonte em outra
--      coleção, de outro usuário, ou no catálogo);
--   2. deixa o hub coletar na hora e gravar os artigos.
--
-- ATENÇÃO À ORDEM: o coletor (coletar.py) usa "on conflict (source_id,
-- url)" a partir do commit que acompanha este arquivo. Rode este SQL e
-- suba o coletor antes da próxima execução do workflow.
-- ============================================================

begin;

-- 1) Unicidade por fonte, não no banco todo -------------------------
-- Com unique(url), se duas fontes (de usuários ou coleções diferentes)
-- seguem o mesmo feed, só a primeira recebe os artigos: o insert da
-- segunda bate na mesma URL e é ignorado. Cada fonte precisa ter a sua
-- cópia (com o seu lido/salvo), então a regra passa a ser "uma URL por
-- fonte".
alter table articles drop constraint articles_url_key;
alter table articles add constraint articles_source_url_key unique (source_id, url);


-- 2) O hub pode inserir artigos, mas só nas fontes do próprio usuário
-- (mesma regra de "dono" do select). É o que permite coletar na hora
-- em que a fonte é adicionada.
create policy "usuarios inserem artigos nas suas fontes"
  on articles for insert
  with check (
    exists (
      select 1 from sources
      join topics on topics.id = sources.topic_id
      where sources.id = articles.source_id
        and topics.user_id = auth.uid()
    )
  );


-- 3) Importar notícias já carregadas --------------------------------
-- security definer: roda com permissão de dono da função, então
-- enxerga artigos de outras fontes (que a RLS esconderia). Por isso
-- ela mesma confere, logo no começo, que a fonte de destino é de quem
-- chamou — sem essa checagem, qualquer um poderia encher a fonte de
-- outra pessoa.
-- set search_path: evita que alguém crie uma tabela "articles" em outro
-- schema e engane a função (cuidado padrão com security definer).
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
  order by a.url, a.collected_at desc
  on conflict (source_id, url) do nothing;
  get diagnostics v_linhas = row_count;
  v_total := v_total + v_linhas;

  -- b) notícias do catálogo dessa mesma fonte (sem resumo da IA: o
  --    resumir.py faz na próxima rodada, porque a categoria fica nula)
  insert into articles (source_id, title, url, content, published_at, author, image_url)
  select p_source_id, c.title, c.url, c.content, c.published_at, c.author, c.image_url
  from catalog_articles c
  join feed_catalog f on f.id = c.catalog_id
  where f.url = v_url
  on conflict (source_id, url) do nothing;
  get diagnostics v_linhas = row_count;
  v_total := v_total + v_linhas;

  return v_total;
end;
$$;

-- Por padrão, função nova pode ser chamada por qualquer um (public).
-- Só quem está logado precisa.
revoke all on function importar_noticias_existentes(uuid) from public;
grant execute on function importar_noticias_existentes(uuid) to authenticated;

commit;
