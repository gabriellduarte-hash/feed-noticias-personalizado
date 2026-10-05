-- ============================================================
-- 019_catalogo_2026-10-01.sql
-- Gerado por catalogo/catalogar.py em 01/10/2026 23:39.
-- Cada feed abaixo foi baixado e validado (entradas, títulos, publicação
-- recente nos últimos 45 dias). Revise nomes/descrições antes de rodar.
-- on conflict (url) do nothing: rodar duas vezes não duplica nada.
-- ============================================================

insert into feed_catalog (category, name, url, description) values
    -- 40 entradas, última em 02/10/2026
    ('Tecnologia', 'Adrenaline', 'https://www.adrenaline.com.br/feed/', 'Fonte de informação sobre Tecnologia e Jogos'),
    -- 10 entradas, última em 01/10/2026
    ('Tecnologia', 'Meio Bit', 'https://meiobit.com/feed/', 'O blog de tecnologia de quem tem opinião'),
    -- 100 entradas, última em 01/10/2026
    ('Tecnologia', 'TechTudo', 'https://www.techtudo.com.br/rss/techtudo', 'O TechTudo reúne as principais notícias de tecnologia, reviews de celulares, TVs e computadores, além de dicas sobre…'),
    -- 20 entradas, última em 02/10/2026
    ('Tecnologia', 'TecMundo', 'https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/tecmundo/?body=%7B%22layout%22:%22google-news%22%7D', 'As principais e as últimas notícias do Brasil e do mundo com credibilidade na informação sobre política, economia,…'),
    -- 20 entradas, última em 01/10/2026
    ('Tecnologia', 'TudoCelular.com', 'https://www.tudocelular.com/feed/', 'O site brasileiro de Telefonia'),
    -- 100 entradas, última em 01/10/2026
    ('Finanças', 'IstoÉ Dinheiro', 'https://istoedinheiro.com.br/feed/rss2', 'Portal de notícias e análises de economia, negócios, finanças, tecnologia e investimentos'),
    -- 10 entradas, última em 01/10/2026
    ('Finanças', 'Seu Dinheiro', 'https://www.seudinheiro.com/feed/', 'Invista com Inteligência'),
    -- 10 entradas, última em 02/10/2026
    ('Finanças', 'Suno Notícias', 'https://www.suno.com.br/noticias/feed/', 'Seu portal de informação sobre o mundo dos investimentos'),
    -- 20 entradas, última em 02/10/2026
    ('Política', 'CartaCapital', 'https://www.cartacapital.com.br/feed/', 'Jornalismo crítico e transparente. Notícias sobre política, economia e sociedade.'),
    -- 20 entradas, última em 02/10/2026
    ('Política', 'Congresso em Foco', 'https://www.congressoemfoco.com.br/feed', 'Congresso em Foco | Política, Economia e Poder'),
    -- 100 entradas, última em 02/10/2026
    ('Política', 'G1 Política', 'https://g1.globo.com/rss/g1/politica/', 'As últimas informações sobre a política no Brasil. Veja o que acontece de importante no Planalto, Congresso,…'),
    -- 10 entradas, última em 02/10/2026
    ('Política', 'Poder360', 'https://www.poder360.com.br/feed/', 'Notícias do poder e da política. Editado por Fernando Rodrigues e equipe'),
    -- 100 entradas, última em 01/10/2026
    ('Ciência', 'G1 Ciência', 'https://g1.globo.com/rss/g1/ciencia/', 'As notícias sobre pesquisas e descobertas científicas.'),
    -- 20 entradas, última em 01/10/2026
    ('Ciência', 'Jornal da USP', 'https://jornal.usp.br/feed/', 'Universidade de São Paulo'),
    -- 30 entradas, última em 01/10/2026
    ('Ciência', 'Revista Pesquisa FAPESP', 'https://revistapesquisa.fapesp.br/feed/', 'Revista Pesquisa FAPESP'),
    -- 43 entradas, última em 01/10/2026
    ('Ciência', 'Superinteressante', 'https://super.abril.com.br/feed/', 'Ciência, história, tecnologia, cultura, curiosidades e tudo mais o que for interessante, de um jeito que só a SUPER…'),
    -- 30 entradas, última em 01/10/2026
    ('Saúde', 'Drauzio Varella', 'https://drauziovarella.uol.com.br/feed/', 'Informação sobre saúde para todos'),
    -- 100 entradas, última em 01/10/2026
    ('Saúde', 'G1 Bem Estar', 'https://g1.globo.com/rss/g1/bemestar/', 'O Bem-Estar é um programa da TV Globo sobre saúde, bem-estar e alimentação'),
    -- 48 entradas, última em 01/10/2026
    ('Saúde', 'Veja Saúde', 'https://saude.abril.com.br/feed/', null),
    -- 24 entradas, última em 02/10/2026
    ('Esportes', 'ESPN Brasil', 'https://www.espn.com.br/rss', 'Latest news from www.espn.com.br'),
    -- 25 entradas, última em 02/10/2026
    ('Entretenimento', 'GameBlast', 'https://www.gameblast.com.br/feeds/posts/default', 'Nintendo, PlayStation, Xbox, PC, Mobile, tudo sobre games, franquias, colunas, notícias, dicas, detonados, downloads e…'),
    -- 40 entradas, última em 01/10/2026
    ('Entretenimento', 'IGN Brasil', 'https://br.ign.com/feed.xml', null),
    -- 25 entradas, última em 02/10/2026
    ('Entretenimento', 'Nintendo Blast', 'https://www.nintendoblast.com.br/feeds/posts/default', 'Tudo sobre Nintendo, Switch, Wii U, 3DS, Wii, DS e suas franquias como Mario, Zelda, Metroid e Pokémon. Blog, fórum,…'),
    -- 10 entradas, última em 01/10/2026
    ('Entretenimento', 'PlayStation.Blog BR', 'http://feeds.feedburner.com/playstationblogbr', 'O blog oficial do PlayStation, com notícias sobre PS5, PS VR2, PS4, PlayStation Plus e PlayStation Store'),
    -- 20 entradas, última em 01/10/2026
    ('Entretenimento', 'Voxel', 'https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/voxel/?body=%7B%22layout%22:%22google-news%22%7D', 'As principais e as últimas notícias do Brasil e do mundo com credibilidade na informação sobre política, economia,…'),
    -- 100 entradas, última em 01/10/2026
    ('Mundo', 'G1 Mundo', 'https://g1.globo.com/rss/g1/mundo/', 'As notícias internacionais mais urgentes e importantes, além de análises e contextualização dos principais assuntos da…'),
    -- 22 entradas, última em 01/10/2026
    ('Mundo', 'RFI Brasil', 'https://www.rfi.fr/br/rss', 'Acompanhe na RFI todas as notícias de política, cultura e esporte, ao vivo e 24 horas. As últimas notícias e destaques…')
on conflict (url) do nothing;
