-- ============================================================
-- 039_fontes_compartilhadas_limpeza.sql  (parte 2 de 2: CONTRAIR)
-- Rode SÓ DEPOIS do push do coletor e do hub desta leva, com o deploy
-- novo da Vercel no ar. Tira o que o 038 deixou pra transição.
-- ============================================================

set lock_timeout = '5s';

begin;

-- gatilhos da transição (o código antigo não grava mais)
drop trigger sources_preencher_feed on sources;
drop trigger articles_preencher_feed on articles;
drop function preencher_feed();

-- políticas e função que usavam articles.source_id. O hub novo não grava
-- notícias com a sessão do usuário: a coleta na hora usa a chave secreta
-- no servidor (com o feed compartilhado, um usuário não pode inserir
-- notícia que outra pessoa vai ler).
drop policy "usuarios inserem artigos nas suas fontes" on articles;
drop policy "usuarios veem artigos dos seus topicos" on articles;
drop function importar_noticias_existentes(uuid);

-- trechos repetidos aprendidos por fonte passam a ser por feed
insert into trechos_repetidos (fonte_id, trecho, visto_em)
select s.feed_id, t.trecho, t.visto_em
from trechos_repetidos t
join sources s on s.id = t.fonte_id
on conflict (fonte_id, trecho)
  do update set visto_em = greatest(trechos_repetidos.visto_em, excluded.visto_em);
delete from trechos_repetidos t using sources s where s.id = t.fonte_id;

-- some junto: a chave estrangeira, o unique (source_id, url) e o índice
alter table articles drop column source_id;

commit;
