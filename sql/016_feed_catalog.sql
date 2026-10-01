-- ============================================================
-- 016_feed_catalog.sql
-- Catálogo de feeds conhecidos pra "Explorar/Seguir" (tipo a tela de
-- descoberta da Feedly). Tabela compartilhada entre todos os usuários
-- (não é dado de ninguém específico) — leitura pública, gerenciada só
-- por SQL direto por enquanto (sem tela de admin).
--
-- As 15 URLs abaixo foram testadas de verdade (feedparser, confirmando
-- que cada uma retorna entradas) antes de entrar aqui — nenhuma
-- inventada. Categorias batem com a mesma lista fixa usada em
-- resumo/resumir.py, pra ter uma taxonomia só no produto inteiro.
-- ============================================================

create table feed_catalog (
    id          uuid primary key default gen_random_uuid(),
    category    text not null,
    name        text not null,
    url         text not null unique,
    description text,
    created_at  timestamptz not null default now()
);

alter table feed_catalog enable row level security;

create policy "qualquer usuario ve o catalogo"
  on feed_catalog for select
  using (true);

insert into feed_catalog (category, name, url, description) values
    ('Tecnologia', 'Tecnoblog', 'https://tecnoblog.net/feed/', 'Tecnologia, smartphones e aplicativos.'),
    ('Tecnologia', 'Canaltech', 'https://canaltech.com.br/rss/', 'Notícias de tecnologia no Brasil.'),
    ('Tecnologia', 'Olhar Digital', 'https://olhardigital.com.br/feed/', 'Tecnologia, ciência e inovação.'),
    ('Tecnologia', 'Showmetech', 'https://www.showmetech.com.br/feed/', 'Tecnologia e cultura geek.'),

    ('Finanças', 'Exame', 'https://exame.com/feed/', 'Economia, negócios e mercado financeiro.'),
    ('Finanças', 'InfoMoney', 'https://www.infomoney.com.br/feed/', 'Mercado financeiro e investimentos.'),
    ('Finanças', 'G1 Economia', 'https://g1.globo.com/rss/g1/economia/', 'Economia no G1.'),
    ('Finanças', 'Money Times', 'https://www.moneytimes.com.br/feed/', 'Mercado financeiro e investimentos.'),

    ('Esportes', 'Trivela', 'https://trivela.com.br/feed/', 'Análise e cultura de futebol.'),
    ('Esportes', 'Revista PLACAR', 'https://www.placar.com.br/feed', 'Futebol brasileiro e internacional.'),
    ('Esportes', 'Gazeta Esportiva', 'https://www.gazetaesportiva.com/feed/', 'Esportes em geral.'),

    ('Entretenimento', 'CinePOP', 'https://www.cinepop.com.br/feed/', 'Cinema, séries e streaming.'),
    ('Entretenimento', 'PAPELPOP', 'https://www.papelpop.com/feed/', 'Entretenimento e cultura pop.'),
    ('Entretenimento', 'B9', 'https://www.b9.com.br/feed/', 'Cultura, tecnologia e internet.'),
    ('Entretenimento', 'G1 Pop & Arte', 'https://g1.globo.com/rss/g1/pop-arte/', 'Entretenimento e cultura no G1.');
