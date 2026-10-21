-- ============================================================
-- 050_endereco_de_fonte.sql
-- Pode rodar quando quiser (não depende do push).
--
-- Auditoria de 20/10: a seguir_fonte (sql/038 e 040) é chamada direto
-- pela API por qualquer usuário logado, sem passar pelo filtro de
-- endereços do hub (leitor-feeds.ts). Ela aceitava qualquer texto como
-- endereço, e o coletor no GitHub abria e gravava o que viesse: dava pra
-- seguir "http://localhost:..." ou um IP da rede interna e ler a resposta
-- como notícia.
--
-- Agora o endereço precisa ser http(s), com um nome de site de verdade:
-- nada de localhost, .local, .internal nem IP digitado (nenhum site de
-- notícias usa). A outra metade da correção está no coletor (rede.py),
-- que confere pra qual IP o nome aponta antes de abrir.
-- ============================================================

create or replace function seguir_fonte(p_topic_id uuid, p_url text, p_tipo text default 'rss', p_nome text default null)
returns table (fonte_id uuid, feed uuid, feed_novo boolean)
language plpgsql
security definer
set search_path = public
as $$
declare
  v_feed uuid;
  v_fonte uuid;
  v_host text;
begin
  if not exists (select 1 from topics where id = p_topic_id and user_id = auth.uid()) then
    raise exception 'coleção não encontrada';
  end if;

  -- o site do endereço, sem usuário:senha@, porta e ponto final
  v_host := regexp_replace(lower(substring(p_url from '^[A-Za-z]+://(?:[^@/?#]*@)?([^:/?#]+)')), '\.$', '');
  if p_url is null or length(p_url) > 2000 or p_url !~* '^https?://' or v_host is null
     or v_host ~ '^(localhost|.*\.localhost|.*\.local|.*\.internal)$'
     or v_host ~ '^[0-9.]+$'      -- IP digitado (e "2130706433", que também é IP)
     or v_host ~ '^0x'            -- IP em hexadecimal
     or v_host ~ '^\['            -- IP v6
     or v_host !~ '\.' then       -- nome sem domínio ("intranet")
    raise exception 'endereço não permitido';
  end if;

  insert into feeds (url, type, name, coletar_pelo_hub)
  values (
    p_url, coalesce(p_tipo, 'rss'), p_nome,
    coalesce((select c.coletar_pelo_hub from feed_catalog c where c.url = p_url), false)
  )
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

-- (o "create or replace" mantém as permissões do sql/038: só usuários
-- logados chamam)
