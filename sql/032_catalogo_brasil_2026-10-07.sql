-- ============================================================
-- 032_catalogo_brasil_2026-10-07.sql
-- Gerado por catalogo/catalogar.py em 07/10/2026 20:05.
-- Cada feed abaixo foi baixado e validado (entradas, títulos, publicação
-- recente nos últimos 45 dias). Revise nomes/descrições antes de rodar.
-- on conflict (url) do nothing: rodar duas vezes não duplica nada.
--
-- Entram só no mapa (vitrine = false, o padrão do sql/031): não são
-- coletadas de hora em hora. Quando alguém segue, viram fonte normal.
-- ============================================================

-- kind: 'rss' (inclui o RSS de busca do Google Notícias) ou 'sitemap' (sql/021).

insert into feed_catalog (category, name, url, description, kind, idioma, regiao) values
    -- via RSS do site: 15 entradas, última em 07/10/2026
    ('Notícias', 'Agência Gov', 'https://agenciagov.ebc.com.br/RSS', null, 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Agência Lupa', 'https://www.agencialupa.org/feed/', 'Decidir começa com se informar', 'rss', 'pt', null),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Notícias', 'Aos Fatos', 'https://www.aosfatos.org/noticias/feed/', 'Aos Fatos é uma organização jornalística dedicada ao combate à desinformação.', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 06/10/2026
    ('Notícias', 'AzMina', 'https://news.google.com/rss/search?q=site%3Aazmina.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Brasil 247', 'https://www.brasil247.com/feed/', 'O que acontece, por que acontece. 24 horas por dia, 7 dias por semana', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 02/10/2026
    ('Notícias', 'De Olho nos Ruralistas', 'https://deolhonosruralistas.com.br/feed/', 'Observatório do Agronegócio no Brasil', 'rss', 'pt', null),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Notícias', 'Estadão Brasil', 'https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/brasil/?body=%7B%22layout%22:%22google-news%22%7D', 'As principais e as últimas notícias do Brasil e do mundo com credibilidade na informação sobre política, economia,…', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'Folha Em Cima da Hora', 'https://feeds.folha.uol.com.br/emcimadahora/rss091.xml', 'Primeiro jornal em tempo real em língua portuguesa', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Meio', 'https://www.canalmeio.com.br/feed/', 'Notícias no momento que você precisa, do jeito que você gosta. Assine o Meio agora. É grátis.', 'rss', 'pt', null),
    -- via RSS do site: 15 entradas, última em 04/10/2026
    ('Notícias', 'Núcleo Jornalismo', 'https://nucleo.jor.br/reportagem/rss/', 'Jornalismo por um futuro humano', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Ponte Jornalismo', 'https://ponte.org/feed/', 'entre você e a realidade', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Projeto Colabora', 'https://projetocolabora.com.br/feed/', 'Jornalismo Sustentável', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Repórter Brasil', 'https://reporterbrasil.org.br/feed/', null, 'rss', 'pt', null),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Notícias', 'A Gazeta do Acre', 'https://agazetadoacre.com/feed/', 'Últimas Notícias do Acre, Brasil e do mundo no jornal a Gazeta, sobre política, Economia, Concurso, Emprego, Educação,…', 'rss', 'pt', 'Acre'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Notícias', 'ac24horas', 'https://ac24horas.com/feed/', 'Últimas Notícias do Acre - Cobertura jornalística da capital do Acre, Rio Branco, Cruzeiro do Sul, Xapuri e…', 'rss', 'pt', 'Acre'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'ContilNet', 'https://contilnetnoticias.com.br/feed/', 'Acompanhe as principais notícias do Acre em tempo real. Informação de credibilidade sobre política, polícia, economia…', 'rss', 'pt', 'Acre'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Acre', 'https://g1.globo.com/rss/g1/ac/acre/', 'Últimas notícias do Acre. Acompanhe informações de trânsito, previsão do tempo, agenda cultural, telejornais e…', 'rss', 'pt', 'Acre'),
    -- via RSS do site: 5 entradas, última em 07/10/2026
    ('Notícias', '7Segundos', 'https://www.7segundos.com.br/rss', 'Últimas notícias de Arapiraca, Maceió, Maragogi e Palmeira no portal 7Segundos: política, economia, polícia, esportes…', 'rss', 'pt', 'Alagoas'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Notícias', 'Alagoas 24 Horas', 'https://www.alagoas24horas.com.br/feed/', 'Alagoas, Jornal, Maceió, Homicídios, Portal, Notícias, Brasil, Cinema, Empregos, Classificados, blog, Futebol, Vídeos', 'rss', 'pt', 'Alagoas'),
    -- via RSS do site: 24 entradas, última em 07/10/2026
    ('Notícias', 'Cada Minuto', 'https://www.cadaminuto.com.br/feed.xml', 'Portal de notícias de Alagoas com cobertura local, política, esportes e principais acontecimentos do estado.', 'rss', 'pt', 'Alagoas'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Alagoas', 'https://g1.globo.com/rss/g1/al/alagoas/', 'Últimas notícias de Maceió e o estado de AL. Acompanhe informações de trânsito, previsão do tempo, agenda cultural,…', 'rss', 'pt', 'Alagoas'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Notícias', 'Gazeta de Alagoas', 'https://www.gazetaweb.com/feed', 'Portal GazetaWeb', 'rss', 'pt', 'Alagoas'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Notícias', 'TNH1', 'https://www.tnh1.com.br/feed/', 'Últimas notícias do portal líder em Alagoas que traz tudo na hora sobre política, economia, polícia, esportes,…', 'rss', 'pt', 'Alagoas'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Tribuna Hoje', 'https://news.google.com/rss/search?q=site%3Atribunahoje.com&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Alagoas'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Amazonas Atual', 'https://amazonasatual.com.br/feed/', 'Jornal Online', 'rss', 'pt', 'Amazonas'),
    -- via RSS do site: 27 entradas, última em 07/10/2026
    ('Notícias', 'BNC Amazonas', 'https://bncamazonas.com.br/feed/', null, 'rss', 'pt', 'Amazonas'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Notícias', 'D24AM', 'https://d24am.com/feed/', '24h Interagindo com a Notícia', 'rss', 'pt', 'Amazonas'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Amazonas', 'https://g1.globo.com/rss/g1/am/amazonas/', 'Últimas notícias do Manaus e o estado do AM. Acompanhe informações de trânsito, previsão do tempo, agenda cultural,…', 'rss', 'pt', 'Amazonas'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'Portal do Holanda', 'https://www.portaldoholanda.com.br/feed.xml', 'Últimas notícias de Portal do Holanda', 'rss', 'pt', 'Amazonas'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Notícias', 'Aratu On', 'https://aratuon.com.br/rss.xml', 'Notícias de Salvador, da Bahia e do Brasil no Aratu On', 'rss', 'pt', 'Bahia'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Notícias', 'Bahia Econômica', 'https://bahiaeconomica.com.br/wp/rsslatest.xml', 'O maior portal de Economia da Bahia', 'rss', 'pt', 'Bahia'),
    -- via RSS do site: 39 entradas, última em 07/10/2026
    ('Notícias', 'Bahia Notícias', 'https://cdn.bahianoticias.com.br/rss.xml', 'Bahia Noticias', 'rss', 'pt', 'Bahia'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Bahia.ba', 'https://news.google.com/rss/search?q=site%3Abahia.ba&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Bahia'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Notícias', 'BNews', 'https://www.bnews.com.br/feed/', 'Últimas notícias do portal mais ágil da Bahia.', 'rss', 'pt', 'Bahia'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Bahia', 'https://g1.globo.com/rss/g1/ba/bahia/', 'Últimas notícias de Salvador todo o estado da BA. Acompanhe informações de trânsito, previsão do tempo, agenda…', 'rss', 'pt', 'Bahia'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Notícias', 'iBahia', 'https://www.ibahia.com/rss', 'Portal iBahia', 'rss', 'pt', 'Bahia'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Metro1', 'https://www.metro1.com.br/rss', 'Últimas Notícias - Metro 1', 'rss', 'pt', 'Bahia'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Política Livre', 'https://news.google.com/rss/search?q=site%3Apoliticalivre.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Bahia'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Tribuna da Bahia', 'https://news.google.com/rss/search?q=site%3Atribunadabahia.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Bahia'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Ceará Agora', 'https://cearaagora.com.br/feed/', 'Política, Economia, Cotidiano, Policial, Aposentadoria, Cultura, Interior, Esporte. Nada fica pela metade.', 'rss', 'pt', 'Ceará'),
    -- via RSS do site: 5 entradas, última em 07/10/2026
    ('Notícias', 'CN7', 'https://cn7.com.br/feed/', 'Portal de notícias do Ceará com cobertura especializada em política, segurança pública e desenvolvimento regional.…', 'rss', 'pt', 'Ceará'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Ceará', 'https://g1.globo.com/rss/g1/ce/ceara/', 'Últimas notícias de Fortaleza e todo o estado do CE. Acompanhe informações de trânsito, previsão do tempo, agenda…', 'rss', 'pt', 'Ceará'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Notícias', 'GC Mais', 'https://gcmais.com.br/sitemap-news.xml', null, 'sitemap', 'pt', 'Ceará'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Miséria', 'https://www.miseria.com.br/feed/', 'Aconteceu, virou notícia.', 'rss', 'pt', 'Ceará'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'O Estado CE', 'https://oestadoce.com.br/feed/', null, 'rss', 'pt', 'Ceará'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Distrito Federal', 'https://g1.globo.com/rss/g1/df/distrito-federal/', 'Últimas notícias de Brasília e todo o Distrito Federal. Acompanhe também informações de trânsito, previsão do tempo,…', 'rss', 'pt', 'Distrito Federal'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Notícias', 'Jornal de Brasília', 'https://jornaldebrasilia.com.br/feed/', 'Informação e Opinião', 'rss', 'pt', 'Distrito Federal'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'A Gazeta', 'https://www.agazeta.com.br/rss', 'RSS últimos posts', 'rss', 'pt', 'Espírito Santo'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Notícias', 'A Tribuna ES', 'https://tribunaonline.com.br/rss', 'Portal Tribuna Online', 'rss', 'pt', 'Espírito Santo'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'ES Hoje', 'https://eshoje.com.br/feed/', 'A gente te conecta com a notícia', 'rss', 'pt', 'Espírito Santo'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Folha Vitória', 'https://www.folhavitoria.com.br/feed/', 'O Jornal Online do Espírito Santo', 'rss', 'pt', 'Espírito Santo'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Espírito Santo', 'https://g1.globo.com/rss/g1/es/espirito-santo/', 'Últimas notícias de Vitória e todo o estado do ES. Acompanhe informações de trânsito, previsão do tempo, agenda…', 'rss', 'pt', 'Espírito Santo'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Século Diário', 'https://news.google.com/rss/search?q=site%3Aseculodiario.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Espírito Santo'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'A Redação', 'https://aredacao.com.br/feed/', 'Notícias de Goiânia e Goiás', 'rss', 'pt', 'Goiás'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Diário da Manhã', 'https://news.google.com/rss/search?q=site%3Adm.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Goiás'),
    -- via Google Notícias: 99 entradas, última em 07/10/2026
    ('Notícias', 'Diário de Goiás', 'https://news.google.com/rss/search?q=site%3Adiariodegoias.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Goiás'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Goiás', 'https://g1.globo.com/rss/g1/go/goias/', 'Últimas notícias de Goiânia e todo o estado de GO. Acompanhe informações de trânsito, previsão do tempo, agenda…', 'rss', 'pt', 'Goiás'),
    -- via Google Notícias: 97 entradas, última em 07/10/2026
    ('Notícias', 'Jornal Opção', 'https://news.google.com/rss/search?q=site%3Ajornalopcao.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Goiás'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Mais Goiás', 'https://www.maisgoias.com.br/feed/', 'Tudo sobre política, saúde, justiça, comportamento e entretenimento. Confira os fatos mais relevantes de Goiás, do…', 'rss', 'pt', 'Goiás'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Portal 6', 'https://portal6.com.br/feed/', 'Notícias de Anápolis', 'rss', 'pt', 'Goiás'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Sagres', 'https://sagresonline.com.br/feed/', 'Em tom maior', 'rss', 'pt', 'Goiás'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Blog do Gilberto Léda', 'https://gilbertoleda.com.br/feed/', 'Política, Esporte e Variedades', 'rss', 'pt', 'Maranhão'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Maranhão', 'https://g1.globo.com/rss/g1/ma/maranhao/', 'Últimas notícias de São Luís e todo o estado de MA. Acompanhe informações de trânsito, previsão do tempo, agenda…', 'rss', 'pt', 'Maranhão'),
    -- via RSS do site: 1000 entradas, última em 07/10/2026
    ('Notícias', 'Imirante', 'https://imirante.com/rss', 'O Portal do Maranhão', 'rss', 'pt', 'Maranhão'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Jornal Pequeno', 'https://jornalpequeno.com.br/feed/', 'O portal do Brasil', 'rss', 'pt', 'Maranhão'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Maranhão Hoje', 'https://mahoje.com.br/feed/', 'Reportagens, política, esporte, economia e as principais notícias da cidade de São Luís e região', 'rss', 'pt', 'Maranhão'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Notícias', 'O Imparcial', 'https://oimparcial.com.br/feed/', 'Há 90 anos em circulação no Maranhão', 'rss', 'pt', 'Maranhão'),
    -- via RSS do site: 20 entradas, última em 06/10/2026
    ('Notícias', 'O Progresso', 'https://oprogressonet.com/rss.xml', 'O maior portal de notícias da Região Tocantina. 55 anos escrevendo a sua história!', 'rss', 'pt', 'Maranhão'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Notícias', 'Diário de Cuiabá', 'https://www.diariodecuiaba.com.br/rss.php', 'RSS do Portal Diario de Cuiabá', 'rss', 'pt', 'Mato Grosso'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Mato Grosso', 'https://g1.globo.com/rss/g1/mt/mato-grosso/', 'Últimas notícias de Cuiabá e todo o estado de MT. Acompanhe informações de trânsito, previsão do tempo, agenda…', 'rss', 'pt', 'Mato Grosso'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Notícias', 'HiperNotícias', 'https://www.hnt.com.br/rss.php', 'RSS do Portal HiperNotícias - Você bem informado', 'rss', 'pt', 'Mato Grosso'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'MidiaNews', 'https://news.google.com/rss/search?q=site%3Amidianews.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Mato Grosso'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Olhar Direto', 'https://news.google.com/rss/search?q=site%3Aolhardireto.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Mato Grosso'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Primeira Página', 'https://primeirapagina.com.br/feed/', 'Notícias do Grupo RMC (MT e MS)', 'rss', 'pt', 'Mato Grosso'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Notícias', 'RD News', 'https://www.rdnews.com.br/rss.php', 'RSS do Portal Rdnews - Principais notícias de Cuiabá, Várzea Grande e Mato grosso', 'rss', 'pt', 'Mato Grosso'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Notícias', 'Repórter MT', 'https://www.reportermt.com/rss.php', 'RSS do Portal RepórterMT - Notícias de Mato Grosso e Cuiabá Hoje', 'rss', 'pt', 'Mato Grosso'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Notícias', 'Correio do Estado', 'https://correiodoestado.com.br/sitemap/news/', null, 'sitemap', 'pt', 'Mato Grosso do Sul'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Notícias', 'Dourados News', 'https://www.douradosnews.com.br/sitemap/', null, 'sitemap', 'pt', 'Mato Grosso do Sul'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Enfoque MS', 'https://www.enfoquems.com.br/feed/', 'Notícias de Campo Grande - MS', 'rss', 'pt', 'Mato Grosso do Sul'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Mato Grosso do Sul', 'https://g1.globo.com/rss/g1/ms/mato-grosso-do-sul/', 'Últimas notícias de Campo Grande e todo o estado de MS. Acompanhe informações de trânsito, previsão do tempo, agenda…', 'rss', 'pt', 'Mato Grosso do Sul'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Notícias', 'JD1 Notícias', 'https://www.jd1noticias.com/feed', 'Feed de notícias do JD1 Notícias', 'rss', 'pt', 'Mato Grosso do Sul'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Notícias', 'TopMídiaNews', 'https://www.topmidianews.com.br/sitemap/', null, 'sitemap', 'pt', 'Mato Grosso do Sul'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Notícias', 'BHAZ', 'https://bhaz.com.br/feed/', 'Informações e notícias de Belo Horizonte', 'rss', 'pt', 'Minas Gerais'),
    -- via Google Notícias: 100 entradas, última em 06/10/2026
    ('Notícias', 'Diário do Aço', 'https://news.google.com/rss/search?q=site%3Adiariodoaco.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Minas Gerais'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Minas Gerais', 'https://g1.globo.com/rss/g1/mg/minas-gerais/', 'Últimas notícias de Belo Horizonte e todo o estado de MG. Informações de trânsito, previsão do tempo, agenda cultural,…', 'rss', 'pt', 'Minas Gerais'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Hoje em Dia', 'https://news.google.com/rss/search?q=site%3Ahojeemdia.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Minas Gerais'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Notícias', 'Itatiaia', 'https://www.itatiaia.com.br/sitemap-news.xml', null, 'sitemap', 'pt', 'Minas Gerais'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Jornal de Uberaba', 'https://www.jornaldeuberaba.com.br/rss.xml', 'Notícias de Uberaba, politica, esportes, entretenimento e muito mais em um só lugar!', 'rss', 'pt', 'Minas Gerais'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'O Fator', 'https://ofator.com.br/feed/', 'Apuração. Informação. Opinião.', 'rss', 'pt', 'Minas Gerais'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Portal UAI', 'https://www.uai.com.br/feed/', 'Acompanhe as últimas notícias e fique bem informado sobre tudo o que acontece no Brasil e no mundo.', 'rss', 'pt', 'Minas Gerais'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Banda B', 'https://www.bandab.com.br/feed/', 'Aconteceu, deu na Banda B. As principais notícias da Grande Curitiba e Paraná.', 'rss', 'pt', 'Paraná'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Notícias', 'Catve', 'https://catve.com/json/sitemap-news.xml', null, 'sitemap', 'pt', 'Paraná'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'CGN', 'https://cgn.inf.br/feed', 'Notícias de Cascavel, Paraná e Brasil', 'rss', 'pt', 'Paraná'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Diário dos Campos', 'https://dcmais.com.br/feed/', 'Notícias de Ponta Grossa e muito mais.', 'rss', 'pt', 'Paraná'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Notícias', 'Folha de Londrina', 'https://www.folhadelondrina.com.br/feed', 'Portal Folha de Londrina', 'rss', 'pt', 'Paraná'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Paraná', 'https://g1.globo.com/rss/g1/pr/parana/', 'Últimas notícias locais de Curitiba e do estado do Paraná. Acompanhe informações de trânsito, previsão do tempo,…', 'rss', 'pt', 'Paraná'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Massa News', 'https://massa.com.br/feed/', null, 'rss', 'pt', 'Paraná'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'O Paraná', 'https://oparana.com.br/feed/', 'Notícias de Cascavel, do Paraná e do Brasil. 50 anos de história e jornalismo de fato que não cabem só na memória.', 'rss', 'pt', 'Paraná'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'RIC Mais', 'https://ric.com.br/feed/', 'As notícias de hoje do Paraná, do Brasil e do mundo', 'rss', 'pt', 'Paraná'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Tribuna do Paraná', 'https://www.tribunapr.com.br/feed/', 'Últimas notícias de Curitiba, região metropolitana e futebol', 'rss', 'pt', 'Paraná'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Notícias', 'ClickPB', 'https://www.clickpb.com.br/feed', 'Acompanhe as últimas notícias da Paraíba, do Brasil e do mundo no ClickPB.', 'rss', 'pt', 'Paraíba'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Paraíba', 'https://g1.globo.com/rss/g1/pb/paraiba/', 'Últimas notícias de João Pessoa e todo o estado da PB. Acompanhe informações de trânsito, tempo, agenda cultural,…', 'rss', 'pt', 'Paraíba'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Notícias', 'Jornal da Paraíba', 'https://jornaldaparaiba.com.br/rss', 'Portal Jornal da Paraíba', 'rss', 'pt', 'Paraíba'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'MaisPB', 'https://www.maispb.com.br/feed', 'Soma de conteúdo com credibilidade', 'rss', 'pt', 'Paraíba'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Paraíba Online', 'https://paraibaonline.com.br/feed/', 'Notícias da Paraíba e do Brasil', 'rss', 'pt', 'Paraíba'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Polêmica Paraíba', 'https://www.polemicaparaiba.com.br/feed/', 'Acompanhe as últimas notícias de todo o estado da Paraíba, do Brasil e do mundo, Política, Esportes, Entretenimento,…', 'rss', 'pt', 'Paraíba'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Portal T5', 'https://thmais.com.br/feed/', 'THMais é um portal de notícias com abrangência em várias cidades e que preza por um jornalismo de credibilidade. Muita…', 'rss', 'pt', 'Paraíba'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'WSCOM', 'https://wscom.com.br/feed/', 'O jornalismo que você confia, agora ainda mais completo e inovador. Acesse conteúdos exclusivos, análises profundas e…', 'rss', 'pt', 'Paraíba'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'DOL – Diário do Pará', 'https://dol.com.br/feed', 'Portal DOL - Diário Online - Portal de NotÍcias', 'rss', 'pt', 'Pará'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Pará', 'https://g1.globo.com/rss/g1/pa/para/', 'Últimas notícias de Belém e todo o estado do PA. Acompanhe informações de trânsito, previsão do tempo, agenda…', 'rss', 'pt', 'Pará'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Roma News', 'https://news.google.com/rss/search?q=site%3Aromanews.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Pará'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Ver-o-Fato', 'https://ver-o-fato.com.br/feed/', 'Portal de Notícias', 'rss', 'pt', 'Pará'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Notícias', 'Blog do Jamildo', 'https://jamildo.com/feed/', 'Notícias de política, economia e negócios de Pernambuco e do Brasil. Editadas por Jamildo Melo, criador do Blog de…', 'rss', 'pt', 'Pernambuco'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Notícias', 'Folha de Pernambuco', 'https://www.folhape.com.br/sitemap/news/', null, 'sitemap', 'pt', 'Pernambuco'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Pernambuco', 'https://g1.globo.com/rss/g1/pe/pernambuco/', 'Últimas notícias do Recife e todo o estado de PE. Informações de trânsito, previsão do tempo, agenda cultural,…', 'rss', 'pt', 'Pernambuco'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'LeiaJá', 'https://news.google.com/rss/search?q=site%3Aleiaja.com&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Pernambuco'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Marco Zero Conteúdo', 'https://marcozero.org/feed/', 'Jornalismo investigativo que aposta em matérias aprofundadas, independentes e de interesse público.', 'rss', 'pt', 'Pernambuco'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', '180graus', 'https://news.google.com/rss/search?q=site%3A180graus.com&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Piauí'),
    -- via RSS do site: 200 entradas, última em 07/10/2026
    ('Notícias', 'Cidade Verde', 'https://cidadeverde.com/rss', 'A gente tem conteúdo! Portal da TV Cidade Verde - Teresina - PI', 'rss', 'pt', 'Piauí'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Piauí', 'https://g1.globo.com/rss/g1/pi/piaui/', 'Últimas notícias de Teresina e todo o estado do PI. Acompanhe informações de trânsito, tempo, agenda cultural,…', 'rss', 'pt', 'Piauí'),
    -- via RSS do site: 20 entradas, última em sem data
    ('Notícias', 'GP1', 'https://feeds.feedburner.com/portalgp1', 'Fique sempre bem informado sobre tudo o que acontece no Piaui, no Brasil e no Mundo. Acesse já!', 'rss', 'pt', 'Piauí'),
    -- via Google Notícias: 11 entradas, última em 07/10/2026
    ('Notícias', 'Meio Norte', 'https://news.google.com/rss/search?q=site%3Ameionorte.com&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Piauí'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Notícias', 'O Dia', 'https://portalodia.com/rss', 'No Portalodia.com você encontra as últimas notícias do Piauí, do Brasil e do mundo, além de notícias e comentários…', 'rss', 'pt', 'Piauí'),
    -- via RSS do site: 12 entradas, última em 07/10/2026
    ('Notícias', 'OitoMeia', 'https://www.oitomeia.com.br/feed/', 'Portal OitoMeia utiliza as novas tecnologias para contar histórias, resgatando a raiz do bom e velho jornalismo.…', 'rss', 'pt', 'Piauí'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Portal AZ', 'https://news.google.com/rss/search?q=site%3Aportalaz.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Piauí'),
    -- via Google Notícias: 99 entradas, última em 07/10/2026
    ('Notícias', 'Viagora', 'https://news.google.com/rss/search?q=site%3Aviagora.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Piauí'),
    -- via RSS do site: 16 entradas, última em 07/10/2026
    ('Notícias', '98 FM Natal', 'https://98fmnatal.com.br/feed/', 'A toda hora, em todo lugar!', 'rss', 'pt', 'Rio Grande do Norte'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Agora RN', 'https://agorarn.com.br/feed/', 'Notícias, reportagens, imagens e fatos de Natal, RN e Brasil', 'rss', 'pt', 'Rio Grande do Norte'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Notícias', 'Blog do BG', 'https://www.blogdobg.com.br/feed/', 'O blog mais acessado do RN', 'rss', 'pt', 'Rio Grande do Norte'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'DeFato', 'https://news.google.com/rss/search?q=site%3Adefato.com&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Rio Grande do Norte'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Rio Grande do Norte', 'https://g1.globo.com/rss/g1/rn/rio-grande-do-norte/', 'Últimas notícias de Natal e todo o estado do RN. Acompanhe informações de trânsito, tempo, agenda cultural,…', 'rss', 'pt', 'Rio Grande do Norte'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Saiba Mais', 'https://saibamais.jor.br/feed/', null, 'rss', 'pt', 'Rio Grande do Norte'),
    -- via RSS do site: 5 entradas, última em 07/10/2026
    ('Notícias', 'Tribuna do Norte', 'https://tribunadonorte.com.br/feed/', 'O maior portal de notícias do RN', 'rss', 'pt', 'Rio Grande do Norte'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'ABC+', 'https://www.abcmais.com/feed/', null, 'rss', 'pt', 'Rio Grande do Sul'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Diário Gaúcho', 'https://news.google.com/rss/search?q=site%3Adiariogaucho.clicrbs.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Rio Grande do Sul'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Rio Grande do Sul', 'https://g1.globo.com/rss/g1/rs/rio-grande-do-sul/', 'Últimas notícias de Porto Alegre e todo o estado do RS. Acompanhe informações de trânsito, previsão do tempo, agenda…', 'rss', 'pt', 'Rio Grande do Sul'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Leouve', 'https://leouve.com.br/feed/', 'Notícias da Serra Gaúcha, do Rio Grande do Sul, do Brasil e do mundo, além da transmissão ao vivo das rádios do Grupo…', 'rss', 'pt', 'Rio Grande do Sul'),
    -- via RSS do site: 15 entradas, última em 07/10/2026
    ('Notícias', 'Matinal', 'https://www.matinal.org/rss/', 'Jornalismo e cultura de Porto Alegre', 'rss', 'pt', 'Rio Grande do Sul'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'O Nacional', 'https://www.onacional.com.br/rss.xml', null, 'rss', 'pt', 'Rio Grande do Sul'),
    -- via RSS do site: 400 entradas, última em 07/10/2026
    ('Notícias', 'O Sul', 'https://www.osul.com.br/feed/', 'A fonte notícias, esporte e entretenimento dos gaúchos.', 'rss', 'pt', 'Rio Grande do Sul'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Sul21', 'https://sul21.com.br/feed/', 'Um jornal independente comprometido com a defesa da diversidade, dos direitos, do meio ambiente e da democracia.', 'rss', 'pt', 'Rio Grande do Sul'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Notícias', 'A Voz da Serra', 'https://avozdaserra.com.br/rss', null, 'rss', 'pt', 'Rio de Janeiro'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Diário de Petrópolis', 'https://news.google.com/rss/search?q=site%3Adiariodepetropolis.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Rio de Janeiro'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Notícias', 'Diário do Rio', 'https://diariodorio.com/feed', 'Acompanhe as notícias e fique bem informado sobre tudo que acontece.', 'rss', 'pt', 'Rio de Janeiro'),
    -- via RSS do site: 12 entradas, última em 07/10/2026
    ('Notícias', 'Enfoco', 'https://enfoco.com.br/feed', 'O seu site de notícias', 'rss', 'pt', 'Rio de Janeiro'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Notícias', 'Eu, Rio!', 'https://eurio.com.br/feed', 'Portal Eu, Rio!', 'rss', 'pt', 'Rio de Janeiro'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'Folha dos Lagos', 'https://www.folhadoslagos.com/ultimas-noticias/rss/', null, 'rss', 'pt', 'Rio de Janeiro'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Rio de Janeiro', 'https://g1.globo.com/rss/g1/rj/rio-de-janeiro/', 'Últimas notícias da cidade do Rio de Janeiro, Baixada Fluminense e de todo o estado. Acompanhe também informações de…', 'rss', 'pt', 'Rio de Janeiro'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Notícias', 'O São Gonçalo', 'https://www.osaogoncalo.com.br/rss', 'Portal O São Gonçalo', 'rss', 'pt', 'Rio de Janeiro'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'SRzd', 'https://srzd.com/feed/', 'Notícias sobre o Brasil, Entretenimento, Carnaval e muito mais!', 'rss', 'pt', 'Rio de Janeiro'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Diário da Amazônia', 'https://news.google.com/rss/search?q=site%3Adiariodaamazonia.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Rondônia'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Rondônia', 'https://g1.globo.com/rss/g1/ro/rondonia/', 'Últimas notícias de Rondônia e da cidade de Porto Velho. Acompanhe informações de trânsito, previsão do tempo, agenda…', 'rss', 'pt', 'Rondônia'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Notícias', 'News Rondônia', 'https://newsrondonia.com.br/feed', 'Notícias de Rondônia | Últimas Notícias de Rondônia', 'rss', 'pt', 'Rondônia'),
    -- via Google Notícias: 62 entradas, última em 07/10/2026
    ('Notícias', 'Rondoniaovivo', 'https://news.google.com/rss/search?q=site%3Arondoniaovivo.com&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Rondônia'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Rondônia Dinâmica', 'https://news.google.com/rss/search?q=site%3Arondoniadinamica.com&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Rondônia'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Tudo Rondônia', 'https://news.google.com/rss/search?q=site%3Atudorondonia.com&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Rondônia'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', '4oito', 'https://news.google.com/rss/search?q=site%3A4oito.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Santa Catarina'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Engeplus', 'https://news.google.com/rss/search?q=site%3Aengeplus.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Santa Catarina'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Santa Catarina', 'https://g1.globo.com/rss/g1/sc/santa-catarina/', 'Últimas notícias de Florianópolis e todo o estado de SC. Informações sobre trânsito, tempo e clima, além dos…', 'rss', 'pt', 'Santa Catarina'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Informe Blumenau', 'https://www.informeblumenau.com/feed/', 'O Informe Blumenau é um portal de conteúdo multimídia com notícias diárias da cidade, do Brasil e do mundo, de forma…', 'rss', 'pt', 'Santa Catarina'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Notícias', 'ND Mais', 'https://ndmais.com.br/feed/', 'Notícias de Santa Catarina', 'rss', 'pt', 'Santa Catarina'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Notícias', 'O Município', 'https://omunicipio.com.br/feed/', 'Brusque e região', 'rss', 'pt', 'Santa Catarina'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Notícias', 'OCP News', 'https://ocp.news/feed', 'O maior Portal de notícias de Jaraguá do Sul, Blumenau, Joinville, Florianópolis, SC e Brasil', 'rss', 'pt', 'Santa Catarina'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'SCC10', 'https://scc10.com.br/feed/', 'O portal da notícia em Santa Catarina', 'rss', 'pt', 'Santa Catarina'),
    -- via Google Notícias: 61 entradas, última em 30/06/2026
    ('Notícias', 'F5 News', 'https://news.google.com/rss/search?q=site%3Af5news.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Sergipe'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Sergipe', 'https://g1.globo.com/rss/g1/se/sergipe/', 'Últimas notícias de Aracaju e todo o estado do SE. Acompanhe informações de trânsito, previsão do tempo, agenda…', 'rss', 'pt', 'Sergipe'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Infonet', 'https://infonet.com.br/feed/', null, 'rss', 'pt', 'Sergipe'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'JL Política', 'https://news.google.com/rss/search?q=site%3Ajlpolitica.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Sergipe'),
    -- via Google Notícias: 100 entradas, última em 18/09/2026
    ('Notícias', 'Jornal da Cidade', 'https://news.google.com/rss/search?q=site%3Ajornaldacidade.net&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Sergipe'),
    -- via RSS do site: 15 entradas, última em 07/10/2026
    ('Notícias', 'NE Notícias', 'https://www.nenoticias.com.br/feed/', 'Leia agora as notícias de amanhã', 'rss', 'pt', 'Sergipe'),
    -- via RSS do site: 200 entradas, última em 07/10/2026
    ('Notícias', 'Portal A8SE', 'https://a8se.com/rss.xml', 'a8se.com', 'rss', 'pt', 'Sergipe'),
    -- via RSS do site: 10 entradas, última em 01/10/2026
    ('Notícias', 'A Cidade ON', 'https://www.acidadeon.com/feed/', 'Maior portal de notícias do interior do estado de São Paulo. Regiões de Araraquara, Campinas, Piracicaba, Ribeirão…', 'rss', 'pt', 'São Paulo'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'ABC do ABC', 'https://news.google.com/rss/search?q=site%3Aabcdoabc.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'São Paulo'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Agência Mural', 'https://agenciamural.org.br/feed/', 'A Agência Mural produz jornalismo sobre, para e pelas periferias, com correspondentes locais que combatem estereótipos…', 'rss', 'pt', 'São Paulo'),
    -- via Google Notícias: 100 entradas, última em 04/10/2026
    ('Notícias', 'Correio Popular', 'https://news.google.com/rss/search?q=site%3Acorreio.rac.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'São Paulo'),
    -- via RSS do site: 40 entradas, última em 07/10/2026
    ('Notícias', 'Diário da Região', 'https://www.diariodaregiao.com.br/rss.xml', 'Notícias de São José do Rio Preto e região', 'rss', 'pt', 'São Paulo'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Notícias', 'Diário do Grande ABC', 'https://www.dgabc.com.br/rss', 'Notícias da região do Grande ABC - Santo André, São Bernardo, São Caetano, Mauá, Diadema, Ribeirão Pires e Rio Grande…', 'rss', 'pt', 'São Paulo'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 São Paulo', 'https://g1.globo.com/rss/g1/sp/sao-paulo/', 'Últimas notícias da cidade e do estado de São Paulo. Acompanhe também informações de trânsito, previsão do tempo,…', 'rss', 'pt', 'São Paulo'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Gazeta de São Paulo', 'https://www.gazetasp.com.br/feed/', 'As notícias mais importantes da cidade de São Paulo.', 'rss', 'pt', 'São Paulo'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Notícias', 'Jornal Cruzeiro do Sul', 'https://www.jornalcruzeiro.com.br/sitemap-news.xml', null, 'sitemap', 'pt', 'São Paulo'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Notícias', 'Jornal de Jundiaí', 'https://sampi.net.br/sitemap-news.xml', null, 'sitemap', 'pt', 'São Paulo'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Notícias', 'AF Notícias', 'https://afnoticias.com.br/sitemap.xml', null, 'sitemap', 'pt', 'Tocantins'),
    -- via RSS do site: 40 entradas, última em sem data
    ('Notícias', 'Conexão Tocantins', 'https://conexaoto.com.br//feed/', 'O Brasil que se encontra aqui é visto pelo mundo!', 'rss', 'pt', 'Tocantins'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Notícias', 'g1 Tocantins', 'https://g1.globo.com/rss/g1/to/tocantins/', 'Últimas notícias de Tocantins. Acompanhe informações, previsão do tempo, agenda cultural e telejornais da TV Anhanguera', 'rss', 'pt', 'Tocantins'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Notícias', 'Gazeta do Cerrado', 'https://gazetadocerrado.com.br/feed/', 'Notícias do Tocantins e do Brasil. Antes de ser notícia, tem que ser verdade', 'rss', 'pt', 'Tocantins'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Notícias', 'Jornal do Tocantins', 'https://news.google.com/rss/search?q=site%3Ajornaldotocantins.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Tocantins'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Notícias', 'Surgiu', 'https://surgiu.com.br/feed/', 'Notícias do Tocantins para o Brasil e o mundo, com informação rápida, confiável e sempre atualizada.', 'rss', 'pt', 'Tocantins'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Política', 'Consultor Jurídico (ConJur)', 'https://conjur.com.br/feed/', 'O mais completo veículo independente sobre Direito e Justiça em língua portuguesa. Dezenas de notícias, artigos e…', 'rss', 'pt', null),
    -- via RSS do site: 15 entradas, última em 02/10/2026
    ('Política', 'Crusoé', 'https://crusoe.com.br/feed/', 'Uma ilha no jornalismo.', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Política', 'Diário do Centro do Mundo', 'https://www.diariodocentrodomundo.com.br/feed', 'O que interessa e nada mais.', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Política', 'Diário do Poder', 'https://diariodopoder.com.br/feed', 'Poder, política e bastidores', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Política', 'Folha Poder', 'https://feeds.folha.uol.com.br/poder/rss091.xml', 'Primeiro jornal em tempo real em língua portuguesa', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Política', 'ICL Notícias', 'https://iclnoticias.com.br/feed/', 'O veículo de informação mais confiável do Brasil', 'rss', 'pt', null),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Política', 'Migalhas', 'https://www.migalhas.com.br/news-sitemap.xml', null, 'sitemap', 'pt', null),
    -- via RSS do site: 15 entradas, última em 07/10/2026
    ('Política', 'O Antagonista', 'https://oantagonista.com.br/feed/', 'O mais influente site jornalístico de política do Brasil', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 06/10/2026
    ('Política', 'O Bastidor', 'https://news.google.com/rss/search?q=site%3Aobastidor.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Política', 'O Cafezinho', 'https://www.ocafezinho.com/feed', 'Portal de noticias e análises sobre política brasileira, geopolítica, economia, tecnologia, sempre numa perspectiva…', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 30/09/2026
    ('Política', 'Planalto', 'https://news.google.com/rss/search?q=site%3Agov.br/planalto/pt-br/acompanhe-o-planalto/noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Política', 'PlatôBR', 'https://platobr.com.br/feed', 'Conteúdo político com clareza e independência', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Política', 'Revista Fórum', 'https://revistaforum.com.br/feed', 'Descubra a trajetória da Revista Fórum, sua influência e legado na mídia brasileira desde 2001 até sua última edição…', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Política', 'Revista Oeste', 'https://revistaoeste.com/feed/', 'Direto ao Ponto', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 06/10/2026
    ('Política', 'STF', 'https://news.google.com/rss/search?q=site%3Aportal.stf.jus.br/noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Política', 'TSE', 'https://news.google.com/rss/search?q=site%3Atse.jus.br/comunicacao/noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 06/10/2026
    ('Finanças', 'Agência IBGE', 'https://news.google.com/rss/search?q=site%3Aagenciadenoticias.ibge.gov.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via Google Notícias: 41 entradas, última em 06/10/2026
    ('Finanças', 'Banco Central', 'https://news.google.com/rss/search?q=site%3Abcb.gov.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Finanças', 'CVM', 'https://news.google.com/rss/search?q=site%3Agov.br/cvm/pt-br/assuntos/noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Finanças', 'Folha Mercado', 'https://feeds.folha.uol.com.br/mercado/rss091.xml', 'Primeiro jornal em tempo real em língua portuguesa', 'rss', 'pt', null),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Finanças', 'Investidor10', 'https://investidor10.com.br/sitemap-news.xml#caminho=/noticias', null, 'sitemap', 'pt', null),
    -- via Google Notícias: 99 entradas, última em 06/10/2026
    ('Finanças', 'Ipea', 'https://news.google.com/rss/search?q=site%3Aipea.gov.br/portal&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Finanças', 'Mercado & Consumo', 'https://mercadoeconsumo.com.br/news-sitemap.xml', null, 'sitemap', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Finanças', 'Ministério da Fazenda', 'https://news.google.com/rss/search?q=site%3Agov.br/fazenda/pt-br/assuntos/noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Finanças', 'Pequenas Empresas & Grandes Negócios', 'https://revistapegn.globo.com/rss/pegn', 'Pequenas Empresas & Grandes Negócios', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Finanças', 'Pipeline', 'https://pipelinevalor.globo.com/rss/pipelinevalor', 'Aqui, você encontra notícias, análises e bastidores do mercado. Isso tudo com histórias, entrevistas e abordagens dos…', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Finanças', 'Receita Federal', 'https://news.google.com/rss/search?q=site%3Agov.br/receitafederal/pt-br/assuntos/noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Finanças', 'Seu Crédito Digital', 'https://seucreditodigital.com.br/feed/', 'Bancos, Crédito e Programas Sociais', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Finanças', 'Startupi', 'https://startupi.com.br/feed/', 'Inovação, Investimentos e empreendedorismo.', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'CISO Advisor', 'https://www.cisoadvisor.com.br/feed/', 'Alertas de Cibersegurança e Segurança da Informação', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'Fast Company Brasil', 'https://fastcompanybrasil.com/feed/', 'O Futuro dos Negócios | Inovação, Tecnologia, Business, Work Life, Design', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Tecnologia', 'g1 Tecnologia', 'https://g1.globo.com/rss/g1/tecnologia/', 'Confira notícias sobre inovações tecnológicas e internet, além de dicas sobre segurança e como usar melhor seu celular', 'rss', 'pt', null),
    -- via RSS do site: 12 entradas, última em 07/10/2026
    ('Tecnologia', 'Hardware.com.br', 'https://www.hardware.com.br/feed/', 'Tudo sobre tecnologia, games e gadgets', 'rss', 'pt', null),
    -- via Google Notícias: 98 entradas, última em 07/10/2026
    ('Tecnologia', 'IT Forum', 'https://news.google.com/rss/search?q=site%3Aitforum.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'MIT Technology Review Brasil', 'https://mittechreview.com.br/feed/', 'Informação especializada, influente e confiável.', 'rss', 'pt', null),
    -- via RSS do site: 12 entradas, última em 07/10/2026
    ('Tecnologia', 'Security Leaders', 'https://securityleaders.com.br/feed/', 'Segurança de redes e computadores', 'rss', 'pt', null),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Ciência', 'Agência Bori', 'https://abori.com.br/feed/', 'A Bori conecta a ciência brasileira à sociedade por meio da comunicação. Divulgamos pesquisas, aproximamos jornalistas…', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 01/10/2026
    ('Ciência', 'ComCiência', 'https://www.comciencia.br/feed/', '_revista de jornalismo científico do Labjor', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Ciência', 'Folha Ciência', 'https://feeds.folha.uol.com.br/ciencia/rss091.xml', 'Primeiro jornal em tempo real em língua portuguesa', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Ciência', 'IHU Unisinos', 'https://news.google.com/rss/search?q=site%3Aihu.unisinos.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Ciência', 'Inpe', 'https://news.google.com/rss/search?q=site%3Agov.br/inpe/pt-br/assuntos/ultimas-noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 12 entradas, última em 07/10/2026
    ('Meio ambiente', '((o))eco', 'https://oeco.org.br/feed/', 'Jornalismo Ambiental', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Meio ambiente', 'Amazônia Latitude', 'https://www.amazonialatitude.com/feed/', 'Ciência e Jornalismo pela Floresta', 'rss', 'pt', null),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Meio ambiente', 'Amazônia Real', 'https://amazoniareal.com.br/feed/', 'Agência de jornalismo independente na Amazônia', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Meio ambiente', 'CicloVivo', 'https://ciclovivo.com.br/feed/', '#PorUmMundoMelhor', 'rss', 'pt', null),
    -- via RSS do site: 12 entradas, última em 07/10/2026
    ('Meio ambiente', 'ClimaInfo', 'https://climainfo.org.br/feed/', 'tudo sobre eventos extremos, transição energética e muito mais!', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 06/10/2026
    ('Meio ambiente', 'EcoDebate', 'https://news.google.com/rss/search?q=site%3Aecodebate.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Meio ambiente', 'Envolverde', 'https://envolverde.com.br/404?from=/feed/', 'Agência de notícias especializada em jornalismo socioambiental e sustentabilidade.', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Meio ambiente', 'Folha Ambiente', 'https://feeds.folha.uol.com.br/ambiente/rss091.xml', 'Primeiro jornal em tempo real em língua portuguesa', 'rss', 'pt', null),
    -- via RSS do site: 20 entradas, última em 01/10/2026
    ('Meio ambiente', 'InfoAmazonia', 'https://infoamazonia.org/feed/', null, 'rss', 'pt', null),
    -- via RSS do site: 20 entradas, última em sem data
    ('Meio ambiente', 'Mongabay Brasil', 'https://brasil.mongabay.com/feed/', 'Notícias sobre vida selvagem e natureza', 'rss', 'pt', null),
    -- via Google Notícias: 82 entradas, última em 07/10/2026
    ('Meio ambiente', 'Observatório do Clima', 'https://news.google.com/rss/search?q=site%3Aoc.eco.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Meio ambiente', 'Reset', 'https://capitalreset.uol.com.br/feed/', 'Notícias sobre economia verde, transição energética e ESG', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Meio ambiente', 'Um Só Planeta', 'https://umsoplaneta.globo.com/rss/umsoplaneta', 'Um Só Planeta é o maior movimento editorial brasileiro para promover práticas sustentáveis e enfrentar a crise…', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 06/10/2026
    ('Saúde', 'Agência Fiocruz', 'https://agencia.fiocruz.br/rss.xml', null, 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 06/10/2026
    ('Saúde', 'Anvisa', 'https://news.google.com/rss/search?q=site%3Agov.br/anvisa/pt-br/assuntos/noticias-anvisa&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Saúde', 'Conass', 'https://www.conass.org.br/feed/', 'Conass promover a articulação e a representação política da gestão estadual do SUS, proporcionando apoio técnico às…', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Saúde', 'Conselho Federal de Medicina', 'https://news.google.com/rss/search?q=site%3Aportal.cfm.org.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Saúde', 'Folha Equilíbrio e Saúde', 'https://feeds.folha.uol.com.br/equilibrioesaude/rss091.xml', 'Primeiro jornal em tempo real em língua portuguesa', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Saúde', 'Futuro da Saúde', 'https://futurodasaude.com.br/feed/', 'Ideias, inovações e desafios da saúde', 'rss', 'pt', null),
    -- via Google Notícias: 99 entradas, última em 02/10/2026
    ('Saúde', 'ICTQ', 'https://news.google.com/rss/search?q=site%3Aictq.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Saúde', 'Medicina S/A', 'https://medicinasa.com.br/feed/', 'Gestão, Inovação e Boas Práticas na Saúde', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Saúde', 'Ministério da Saúde', 'https://news.google.com/rss/search?q=site%3Agov.br/saude/pt-br/assuntos/noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Saúde', 'Saúde Business', 'https://www.saudebusiness.com/feed/', 'Notícias, insights, tendências e reflexões para informar o executivo de saúde no Brasil.', 'rss', 'pt', null),
    -- via sitemap de notícias: 14 entradas, última em 07/10/2026
    ('Saúde', 'UOL VivaBem', 'https://www.uol.com.br/vivabem/sitemap/v2/news-01.xml#caminho=/vivabem', null, 'sitemap', 'pt', null),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Esportes', 'F1Mania', 'https://www.f1mania.net/feed/', 'F1, Fórmula 1, F2, MotoGP - Últimas Notícias', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Esportes', 'Folha Esporte', 'https://feeds.folha.uol.com.br/esporte/rss091.xml', 'Primeiro jornal em tempo real em língua portuguesa', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Esportes', 'Futebol Interior', 'https://www.futebolinterior.com.br/feed/rss2/', null, 'rss', 'pt', null),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Esportes', 'Grande Prêmio', 'https://grandepremio.com/br/sitemap-news.xml', null, 'sitemap', 'pt', null),
    -- via RSS do site: 10 entradas, última em 15/09/2026
    ('Esportes', 'Jumper Brasil', 'https://jumperbrasil.com.br/feed/', 'Notícias de basquete, NBA, Rumores, Draft, Vídeos e muito mais', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Esportes', 'Máquina do Esporte', 'https://maquinadoesporte.com.br/feed/', null, 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Esportes', 'Surto Olímpico', 'https://surtoolimpico.com.br/api/public/r7-feed.xml', 'Notícias, resultados e cobertura completa do esporte olímpico e paralímpico brasileiro.', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 22/09/2026
    ('Esportes', 'The Playoffs', 'https://theplayoffs.news/feed/', 'O Portal dos Esportes Americanos no Brasil', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 07/09/2026
    ('Esportes', 'TNT Sports Brasil', 'https://news.google.com/rss/search?q=site%3Atntsports.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Esportes', 'UOL Esporte', 'https://www.uol.com.br/esporte/sitemap/v2/news-01.xml#caminho=/esporte', null, 'sitemap', 'pt', null),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Esportes', 'No Ataque', 'https://noataque.com.br/feed/', 'Notícias esportivas nacionais e internacionais. Futebol, basquete, vôlei, automobilismo e mais. Análises, resultados,…', 'rss', 'pt', 'Minas Gerais'),
    -- via RSS do site: 10 entradas, última em 06/10/2026
    ('Esportes', 'Rádio Grenal', 'https://www.radiogrenal.com.br/feed/', 'Só mais um site WordPress', 'rss', 'pt', 'Rio Grande do Sul'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Esportes', 'Coluna do Fla', 'https://colunadofla.com/feed/', 'Notícias do Flamengo de hoje. Mercado da bola, bastidores e jogos ao vivo. Acompanhe tudo sobre o Mengão!', 'rss', 'pt', 'Rio de Janeiro'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Esportes', 'NetFlu', 'https://www.netflu.com.br/feed/', 'Site de notícias do Fluminense Football Club', 'rss', 'pt', 'Rio de Janeiro'),
    -- via RSS do site: 10 entradas, última em sem data
    ('Esportes', 'SuperVasco', 'https://www.supervasco.com/rss/noticias_geral.xml', 'Confira no Supervasco as últimas notícias sobre o Vasco futebol do Vasco da Gama', 'rss', 'pt', 'Rio de Janeiro'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Esportes', 'Vasco Notícias', 'https://vasconoticias.com.br/feed/', null, 'rss', 'pt', 'Rio de Janeiro'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Esportes', 'Central do Timão', 'https://centraldotimao.com.br/feed/', 'Confira as últimas notícias do dia do Corinthians. Acompanhe nossas redes sociais e a TV Central do Timão.', 'rss', 'pt', 'São Paulo'),
    -- via RSS do site: 10 entradas, última em 17/09/2026
    ('Esportes', 'Diário do Peixe', 'https://www.diariodopeixe.com.br/feed/', 'Aqui quem dá bola é o Santos', 'rss', 'pt', 'São Paulo'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Esportes', 'Nosso Palestra', 'https://nossopalestra.com.br/feed/', 'Palmeirenses que escrevem, analisam, gravam, opinam e noticiam o Palmeiras. Paixão e honestidade.', 'rss', 'pt', 'São Paulo'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Esportes', 'Palmeiras Online', 'https://palmeirasonline.com/feed/', 'O primeiro site do Palmeiras da internet brasileira. Notícias, informações, opiniões e muito mais sobre o Verdão.', 'rss', 'pt', 'São Paulo'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Esportes', 'SPFC.net', 'https://spfc.net/rss/news.xml', null, 'sitemap', 'pt', 'São Paulo'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Esportes', 'Verdazzo', 'https://www.verdazzo.com.br/feed/', 'VAMOS PALMEIRAS!', 'rss', 'pt', 'São Paulo'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Entretenimento', 'Arkade', 'https://arkade.com.br/feed/', 'Jogos, Tecnologia e Cultura', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'Caras', 'https://caras.com.br/feed', null, 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'Combo Infinito', 'https://www.comboinfinito.com.br/principal/feed/', 'Opinião e o mundo nerd é o nosso Combo!', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'Contigo!', 'https://contigo.com.br/feed', null, 'rss', 'pt', null),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Entretenimento', 'Critical Hits', 'https://criticalhits.com.br/feed/', 'As últimas notícias em games, anime, cinema e tv e cultura geek', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'Flow Games', 'https://flowgames.gg/feed/', null, 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Entretenimento', 'Folha Ilustrada', 'https://feeds.folha.uol.com.br/ilustrada/rss091.xml', 'Primeiro jornal em tempo real em língua portuguesa', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'GameVicio', 'https://www.gamevicio.com/feed/', 'Notícias sobre games, jogos e tecnologia', 'rss', 'pt', null),
    -- via RSS do site: 15 entradas, última em 07/10/2026
    ('Entretenimento', 'Hugo Gloss', 'https://hugogloss.uol.com.br/feed/', null, 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Entretenimento', 'NaTelinha', 'https://news.google.com/rss/search?q=site%3Anatelinha.uol.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Entretenimento', 'Notícias da TV', 'https://noticiasdatv.uol.com.br/feed', 'Notícias e Artigos mais recentes', 'rss', 'pt', null),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Entretenimento', 'Observatório da TV', 'https://observatoriodatv.uol.com.br/sitemap-news.xml', null, 'sitemap', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'PSX Brasil', 'https://psxbrasil.com.br/feed/', null, 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'Quatro Cinco Um', 'https://quatrocincoum.com.br/feed', 'A Revista dos Livros', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 06/10/2026
    ('Entretenimento', 'Revista Cult', 'https://revistacult.uol.com.br/home/feed/', null, 'rss', 'pt', null),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Entretenimento', 'Splash UOL', 'https://www.uol.com.br/splash/sitemap/news-01.xml#caminho=/splash', null, 'sitemap', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Automóveis', 'Autoesporte', 'https://autoesporte.globo.com/rss/autoesporte', 'Fique por dentro das últimas notícias sobre lançamentos de carros, avaliações, comparativos, melhores compras e muito…', 'rss', 'pt', null),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Automóveis', 'AutoPapo', 'https://autopapo.com.br/feed/', 'Boris Feldman e equipe explicam tudo sobre carros, motos e mobilidade', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Automóveis', 'FlatOut', 'https://flatout.com.br/feed/', 'Sua overdose de cultura automotiva - de carros antigos a lançamentos', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Automóveis', 'g1 Carros', 'https://g1.globo.com/rss/g1/carros/', 'As últimas notícias sobre lançamentos de carros e motos, as listas dos mais vendidos e dicas sobre como tirar o melhor…', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Automóveis', 'Garagem 360', 'https://garagem360.com.br/feed/', 'Sua Oficina Virtual', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Automóveis', 'InsideEVs Brasil', 'https://news.google.com/rss/search?q=site%3Ainsideevs.uol.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Automóveis', 'Jornal do Carro', 'https://news.google.com/rss/search?q=site%3Ajornaldocarro.estadao.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Automóveis', 'Mobiauto', 'https://news.google.com/rss/search?q=site%3Amobiauto.com.br/revista&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 20 entradas, última em 06/10/2026
    ('Automóveis', 'Motor Show', 'https://motorshow.com.br/feed/rss2', 'Notícias, segredos, avaliações e comparativos de carros', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Automóveis', 'Motor1 Brasil', 'https://news.google.com/rss/search?q=site%3Amotor1.uol.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Automóveis', 'Notícias Automotivas', 'https://www.noticiasautomotivas.com.br/feed/', 'Noticias de carros', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Automóveis', 'Quatro Rodas', 'https://quatrorodas.abril.com.br/ultimas-noticias/feed/', 'Saiba tudo sobre o mercado de automóveis: últimas notícias, testes e comparativos, modelos, serviços, guia de compras…', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Automóveis', 'Revista Carro', 'https://revistacarro.com.br/feed/', 'O site do seu Carro', 'rss', 'pt', null),
    -- via sitemap de notícias: 15 entradas, última em 07/10/2026
    ('Automóveis', 'UOL Carros', 'https://www.uol.com.br/carros/sitemap/v2/news-01.xml#caminho=/carros', null, 'sitemap', 'pt', null),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Mundo', 'Euronews', 'https://pt.euronews.com/rss', 'Latest news from Euronews', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Mundo', 'Folha Mundo', 'https://feeds.folha.uol.com.br/mundo/rss091.xml', 'Primeiro jornal em tempo real em língua portuguesa', 'rss', 'pt', null),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'Expresso', 'https://expresso.pt/sitemap/news.xml', null, 'sitemap', 'pt', 'Portugal'),
    -- via RSS do site: 51 entradas, última em 07/10/2026
    ('Mundo', 'Observador', 'https://observador.pt/feed/', 'Feed com os últimos artigos publicados', 'rss', 'pt', 'Portugal'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Mundo', 'Público', 'https://news.google.com/rss/search?q=site%3Apublico.pt&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', 'Portugal'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'RTP Notícias', 'http://www.rtp.pt/noticias/sitemap#caminho=/noticias', null, 'sitemap', 'pt', 'Portugal'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'SIC Notícias', 'https://sicnoticias.pt/sitemap/news.xml', null, 'sitemap', 'pt', 'Portugal'),
    -- via RSS do site: 24 entradas, última em 07/10/2026
    ('Outros', 'ArchDaily Brasil', 'http://feeds.feedburner.com/Archdaily', 'ArchDaily | Broadcasting Architecture Worldwide', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Outros', 'Casa e Jardim', 'https://revistacasaejardim.globo.com/rss/casaejardim', 'Casa e Jardim | Home', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Outros', 'Casa Vogue', 'https://casavogue.globo.com/rss/casavogue', 'Acompanhe aqui todas as notícias sobre interiores, design, arquitetura, lazer & cultura, colunas, arquitetura,…', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 06/10/2026
    ('Outros', 'Casa.com.br', 'https://casa.abril.com.br/feed/', 'Acompanhe dicas de design de interiores, arquitetura, decoração de casa em um só lugar. Inspirações com ambientes…', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Outros', 'Claudia', 'https://claudia.abril.com.br/feed/', 'Comportamento, saúde, entretenimento, carreira, maternidade e mais. CLAUDIA recebe convidados para conversar sobre…', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Outros', 'Elle Brasil', 'https://elle.com.br/feed', 'A moda, só que diferente', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Outros', 'g1 Educação', 'https://g1.globo.com/rss/g1/educacao/', 'Notícias sobre a educação no Brasil, o calendário dos vestibulares e do Enem, Guia de Carreiras e Teste vocacional', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 29/09/2026
    ('Outros', 'g1 Turismo e Viagem', 'https://g1.globo.com/rss/g1/turismo-e-viagem/', 'Conheça os lugares e atrações que estão em alta no mundo do turismo ou que estão sendo descobertos, além de dicas de…', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Outros', 'Glamour Brasil', 'https://glamour.globo.com/rss/glamour', 'home', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Outros', 'GQ Brasil', 'https://gq.globo.com/rss/gq', 'O guia definitivo para o homem moderno com dicas de estilo, as últimas sobre cultura, esportes, saúde e mais', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Outros', 'Guia do Estudante', 'https://guiadoestudante.abril.com.br/ultimas-noticias/feed/', 'Descubra sua profissão, escolha sua faculdade, entenda os acontecimentos do dia e fique por dentro do Enem e dos…', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Outros', 'Marie Claire', 'https://revistamarieclaire.globo.com/rss/marieclaire', 'Marie Claire - Se importa para a mulher, está em Marie Claire', 'rss', 'pt', null),
    -- via Google Notícias: 92 entradas, última em 06/10/2026
    ('Outros', 'Na Prática', 'https://news.google.com/rss/search?q=site%3Anapratica.org.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Outros', 'Porvir', 'https://porvir.org/feed/', 'Jornalismo e soluções de comunicação para uma educação inovadora', 'rss', 'pt', null),
    -- via RSS do site: 9 entradas, última em 07/10/2026
    ('Outros', 'Revista Educação', 'https://revistaeducacao.com.br/feed/', null, 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 22/09/2026
    ('Outros', 'Todos Pela Educação', 'https://todospelaeducacao.org.br/feed/', 'Produzir estudos e pesquisas, mobilizar a sociedade pela melhoria da qualidade da Educação e articular com o poder…', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Outros', 'Vida Simples', 'https://vidasimples.co/feed/', 'Viva a sua vida mais simples: reflexões sobre bem-estar, saúde, autoconhecimento e propósito.', 'rss', 'pt', null),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Outros', 'Viva Decora', 'https://casaeconstrucao.vivadecora.com.br/feed/', 'Dicas Casa e Construção', 'rss', 'pt', null),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Outros', 'Vogue Brasil', 'https://vogue.globo.com/rss/vogue', 'Últimas notícias do mundo da moda, desfiles, dicas de moda, beleza e lifestyle, red carpet, tendências, estilo das…', 'rss', 'pt', null),
    -- segunda passada (o plano B usava o caminho do feed na busca do Google Notícias; corrigido)
    -- via Google Notícias: 99 entradas, última em 07/10/2026
    ('Notícias', 'Estadão', 'https://news.google.com/rss/search?q=site%3Aestadao.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Meio ambiente', 'g1 Meio Ambiente', 'https://news.google.com/rss/search?q=site%3Ag1.globo.com&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Via Google Notícias', 'rss', 'pt', null)
on conflict (url) do nothing;
