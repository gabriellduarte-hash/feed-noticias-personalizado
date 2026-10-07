-- ============================================================
-- 033_catalogo_ingles_2026-10-07.sql
-- Gerado por catalogo/catalogar.py em 07/10/2026 20:10.
-- Cada feed abaixo foi baixado e validado (entradas, títulos, publicação
-- recente nos últimos 45 dias). Revise nomes/descrições antes de rodar.
-- on conflict (url) do nothing: rodar duas vezes não duplica nada.
--
-- Entram só no mapa (vitrine = false, o padrão do sql/031): não são
-- coletadas de hora em hora. Quando alguém segue, viram fonte normal.
-- ============================================================

-- kind: 'rss' (inclui o RSS de busca do Google Notícias) ou 'sitemap' (sql/021).

insert into feed_catalog (category, name, url, description, kind, idioma, regiao) values
    -- via Google Notícias: 83 entradas, última em 07/10/2026
    ('Política', 'AEI', 'https://news.google.com/rss/search?q=site%3Aaei.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Política', 'Axios', 'https://api.axios.com/feed/', 'Axios', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Política', 'Breitbart', 'https://feeds.feedburner.com/breitbart', 'HomePage', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 06/10/2026
    ('Política', 'Brennan Center', 'https://news.google.com/rss/search?q=site%3Abrennancenter.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 89 entradas, última em 07/10/2026
    ('Política', 'Cato Institute', 'https://news.google.com/rss/search?q=site%3Acato.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 85 entradas, última em 06/10/2026
    ('Política', 'Center for American Progress', 'https://news.google.com/rss/search?q=site%3Aamericanprogress.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 40 entradas, última em 07/10/2026
    ('Política', 'Democracy Now!', 'https://www.democracynow.org/democracynow.rss', 'Democracy Now! is an independent daily TV & radio news program, hosted by award-winning journalists Amy Goodman and…', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Política', 'Gallup', 'https://news.google.com/rss/search?q=site%3Anews.gallup.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Política', 'Heritage Foundation', 'https://www.heritage.org/rss', 'Content from www.heritage.org.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Política', 'Jacobin', 'https://jacobin.com/feed/', 'Jacobin is a leading voice of the American left, offering socialist perspectives on politics, economics, and culture.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Política', 'Mother Jones', 'https://www.motherjones.com/feed/', 'Smart, fearless journalism', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Política', 'National Review', 'https://www.nationalreview.com/feed/', null, 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 12 entradas, última em 07/10/2026
    ('Política', 'New York Magazine – Intelligencer', 'https://nymag.com/news.xml#caminho=/intelligencer', null, 'sitemap', 'en', 'EUA'),
    -- via RSS do site: 11 entradas, última em 01/10/2026
    ('Política', 'OpenSecrets', 'https://www.opensecrets.org/news/feed/', 'News, original reporting, and investigative journalism on money in politics from OpenSecrets.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Política', 'Pew Research Center', 'https://www.pewresearch.org/feed/', 'Numbers, Facts and Trends Shaping Your World', 'rss', 'en', 'EUA'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Política', 'Politico', 'https://rss.politico.com/politics-news.xml', 'News, Analysis and Opinion from POLITICO', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Política', 'ProPublica', 'https://www.propublica.org/feeds/propublica/main', 'Latest Articles and Investigations from ProPublica, an independent, non-profit newsroom that produces investigative…', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 98 entradas, última em 07/10/2026
    ('Política', 'RealClearPolitics', 'https://news.google.com/rss/search?q=site%3Arealclearpolitics.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 48 entradas, última em 07/10/2026
    ('Política', 'Reason', 'https://reason.com/feed/', 'Free Minds and Free Markets', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Política', 'Roll Call', 'https://rollcall.com/feed/', 'Covering Capitol Hill Since 1955', 'rss', 'en', 'EUA'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Política', 'Slate', 'https://slate.com/feeds/all.rss', 'Slate RSS', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Política', 'Talking Points Memo', 'https://talkingpointsmemo.com/feed', 'Breaking News and Analysis', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Política', 'The American Conservative', 'https://www.theamericanconservative.com/feed/', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Política', 'The American Prospect', 'https://prospect.org/feed/', 'Ideas, Politics & Power', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Política', 'The Cook Political Report', 'https://news.google.com/rss/search?q=site%3Acookpolitical.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Política', 'The Daily Caller', 'https://dailycaller.com/feed/', 'The Daily Caller features breaking news, opinion, research, and entertainment 24 hours a day.', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 92 entradas, última em 07/10/2026
    ('Política', 'The Daily Wire', 'https://news.google.com/rss/search?q=site%3Adailywire.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Política', 'The Federalist', 'https://thefederalist.com/feed/', 'Culture, Politics, Religion', 'rss', 'en', 'EUA'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Política', 'The Hill', 'https://thehill.com/feed/?feed=partnerfeed-news-feed&format=rss', 'Unbiased Politics News', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Política', 'The Intercept', 'https://theintercept.com/feed/?rss', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Política', 'The Marshall Project', 'https://www.themarshallproject.org/rss/recent', 'The Marshall Project is a nonprofit, nonpartisan news organization covering America''s criminal justice system.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Política', 'The Nation', 'https://www.thenation.com/feed/?post_type=article', 'The Nation Magazine', 'rss', 'en', 'EUA'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Política', 'The New Republic', 'https://newrepublic.com/rss.xml', 'The New Republic', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 28 entradas, última em 29/09/2026
    ('Política', 'Urban Institute', 'https://news.google.com/rss/search?q=site%3Aurban.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Política', 'Vox', 'https://www.vox.com/rss/index.xml', 'Our world has too much noise and too little context. Vox helps you understand what matters.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 06/10/2026
    ('Política', 'Bellingcat', 'https://www.bellingcat.com/feed/', 'the home of online investigations', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 11 entradas, última em 07/10/2026
    ('Política', 'ICIJ', 'https://www.icij.org/feed/', 'International Consortium of Investigative Journalists', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 60 entradas, última em 07/10/2026
    ('Política', 'OCCRP', 'https://www.occrp.org/en/feed', 'Feed, delivered straight to you. Well, your RSS reader anyway.', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Política', 'Documented', 'https://documentedny.com/feed/', null, 'rss', 'en', 'Nova York (EUA)'),
    -- via Google Notícias: 99 entradas, última em 05/10/2026
    ('Política', 'The Bureau of Investigative Journalism', 'https://news.google.com/rss/search?q=site%3Athebureauinvestigates.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Reino Unido'),
    -- via sitemap de notícias: 30 entradas, última em 08/10/2026
    ('Finanças', 'Australian Financial Review', 'https://www.afr.com/sitemaps/news/brands/afr', null, 'sitemap', 'en', 'Austrália'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Finanças', 'SmartCompany', 'https://www.smartcompany.com.au/feed/', 'Business news, business advice and information for Australian SMEs, startups and entrepreneurs', 'rss', 'en', 'Austrália'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Finanças', 'Financial Post', 'https://financialpost.com/feed', 'Canada Business News | Financial Updates & Information', 'rss', 'en', 'Canadá'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Finanças', 'American Banker', 'https://www.americanbanker.com/feed?rss=true', 'The Latest', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Finanças', 'Banking Dive', 'https://www.bankingdive.com/feeds/news/', 'Banking news', 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Finanças', 'Barron''s', 'https://www.barrons.com/bol_news_sitemap.xml', null, 'sitemap', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Finanças', 'Benzinga', 'https://www.benzinga.com/feed', null, 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Finanças', 'Bloomberg', 'https://www.bloomberg.com/sitemaps/news/latest.xml', null, 'sitemap', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Finanças', 'Business Insider', 'https://feeds.businessinsider.com/custom/all', 'All Content from Business Insider Excluding Premium', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Finanças', 'CFO Dive', 'https://www.cfodive.com/feeds/news/', 'CFO news', 'rss', 'en', 'EUA'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Finanças', 'CNBC', 'https://www.cnbc.com/id/100003114/device/rss/rss.html', 'CNBC is the world leader in business news and real-time financial market coverage. Find fast, actionable information.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Finanças', 'Construction Dive', 'https://www.constructiondive.com/feeds/news/', 'Construction industry news, trends and jobs for building professionals who want mobile-friendly content.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Finanças', 'Entrepreneur', 'https://www.entrepreneur.com/rss-feed/latest', 'The latest small business tips and advice from Entrepreneur', 'rss', 'en', 'EUA'),
    -- via RSS do site: 19 entradas, última em 07/10/2026
    ('Finanças', 'Fast Company', 'https://www.fastcompany.com/latest/rss', 'Fast Company inspires a new breed of innovative and creative thought leaders who are actively inventing the future of…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Finanças', 'Federal Reserve', 'https://www.federalreserve.gov/feeds/press_all.xml', 'All recent press releases from the Federal Reserve Board', 'rss', 'en', 'EUA'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Finanças', 'Forbes', 'https://www.forbes.com/business/feed/', 'Forbes - Business', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Finanças', 'Fortune', 'https://fortune.com/feed/fortune-feeds/?id=3230629', 'Fortune 500 Daily & Breaking Business News', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 73 entradas, última em 07/10/2026
    ('Finanças', 'Harvard Business Review', 'https://news.google.com/rss/search?q=site%3Ahbr.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 40 entradas, última em 07/10/2026
    ('Finanças', 'Inc.', 'https://www.inc.com/rss/', 'Inc.com, the daily resource for entrepreneurs.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Finanças', 'Investor''s Business Daily', 'https://www.investors.com/feed/', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Finanças', 'Kiplinger', 'https://www.kiplinger.com/feed/all', 'All the latest content from the Kiplinger team', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Finanças', 'MarketWatch', 'https://feeds.content.dowjones.io/public/rss/mw_topstories', 'MarketWatch, a leading publisher of business and financial news, offers users up-to-the minute news, investment tools,…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Finanças', 'MIT Sloan Management Review', 'https://sloanreview.mit.edu/feed/', 'The New Business of Innovation', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Finanças', 'Payments Dive', 'https://www.paymentsdive.com/feeds/news/', 'Payments News', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 06/10/2026
    ('Finanças', 'Peterson Institute (PIIE)', 'https://news.google.com/rss/search?q=site%3Apiie.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 17 entradas, última em 07/10/2026
    ('Finanças', 'Quartz', 'https://qz.com/rss', 'Quartz is a guide to the new global economy for people who are excited by change. We cover business, finance,…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Finanças', 'Restaurant Business', 'https://www.restaurantbusinessonline.com/feed/', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Finanças', 'Retail Dive', 'https://www.retaildive.com/feeds/news/', 'Retail industry news, voices and jobs. Optimized for your mobile phone.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 25 entradas, última em 06/10/2026
    ('Finanças', 'SEC', 'https://www.sec.gov/news/pressreleases.rss', 'Official announcements highlighting recent actions taken by the SEC and other newsworthy information.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Finanças', 'Supply Chain Dive', 'https://www.supplychaindive.com/feeds/news/', 'Supply chain and logistics news', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em sem data
    ('Finanças', 'Tax Foundation', 'https://taxfoundation.org/feed/', 'Principled Research. Insightful Analysis. Engaged Experts.', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Finanças', 'The Information', 'https://news.google.com/rss/search?q=site%3Atheinformation.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Finanças', 'The Motley Fool', 'https://www.fool.com/a/feeds/foolwatch?apikey=foolwatch-feed', 'The Motley Fool provides leading insight and analysis about stocks, helping investors stay informed.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Finanças', 'Investing.com', 'https://www.investing.com/rss/news.rss', null, 'rss', 'en', 'Internacional'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Finanças', 'City A.M.', 'https://www.cityam.com/feed/', 'London''s Business Newspaper', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Finanças', 'Financial Times', 'https://www.ft.com/rss/home/international', 'International homepage', 'rss', 'en', 'Reino Unido'),
    -- via Google Notícias: 29 entradas, última em 07/10/2026
    ('Finanças', 'Business Standard', 'https://news.google.com/rss/search?q=site%3Abusiness-standard.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Índia'),
    -- via RSS do site: 35 entradas, última em 07/10/2026
    ('Finanças', 'Mint', 'https://www.livemint.com/rss/news', 'Get the latest news and analysis on business, finance, politics from mint, the website of the Mint newspaper, one of…', 'rss', 'en', 'Índia'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Finanças', 'Moneycontrol', 'https://news.google.com/rss/search?q=site%3Amoneycontrol.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Índia'),
    -- via RSS do site: 76 entradas, última em 07/10/2026
    ('Finanças', 'The Economic Times', 'https://economictimes.indiatimes.com/rssfeedsdefault.cms', 'The Economic Times: Latest business, finance, markets, stocks, company news from India.', 'rss', 'en', 'Índia'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'The Decoder', 'https://the-decoder.com/feed/', 'AI, Menschen, Wirtschaft', 'rss', 'en', 'Alemanha'),
    -- via RSS do site: 150 entradas, última em 07/10/2026
    ('Tecnologia', 'BetaKit', 'https://betakit.com/feed/', 'Canadian Tech & Startup News', 'rss', 'en', 'Canadá'),
    -- via RSS do site: 15 entradas, última em 07/10/2026
    ('Tecnologia', '404 Media', 'https://www.404media.co/rss/', '404 Media is an independent media company founded by technology journalists Jason Koebler, Emanuel Maiberg, Samantha…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Tecnologia', '9to5Google', 'https://9to5google.com/feed/', 'Google news, Pixel, Android, Gemini, Home, more', 'rss', 'en', 'EUA'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Tecnologia', '9to5Mac', 'https://9to5mac.com/feed/', 'Apple News & Mac Rumors Breaking All Day', 'rss', 'en', 'EUA'),
    -- via RSS do site: 80 entradas, última em 07/10/2026
    ('Tecnologia', 'Android Authority', 'https://www.androidauthority.com/feed/', 'Android News, Reviews, How To', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Tecnologia', 'Android Central', 'https://www.androidcentral.com/feeds.xml', 'All the latest content from the Android Central team', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'Android Police', 'https://www.androidpolice.com/feed/', 'All the latest mobile tech news, deals, reviews, guides, editorials, and more. Embracing the green bubble since 2009.', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 06/10/2026
    ('Tecnologia', 'Anthropic News', 'https://news.google.com/rss/search?q=site%3Aanthropic.com/news&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Tecnologia', 'AppleInsider', 'https://appleinsider.com/rss/news/', 'AppleInsider News Feed', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Tecnologia', 'Ars Technica', 'https://feeds.arstechnica.com/arstechnica/index', 'All Ars Technica stories', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Tecnologia', 'AWS Machine Learning Blog', 'https://aws.amazon.com/blogs/machine-learning/feed/', 'Official Machine Learning Blog of Amazon Web Services', 'rss', 'en', 'EUA'),
    -- via RSS do site: 15 entradas, última em 07/10/2026
    ('Tecnologia', 'BleepingComputer', 'https://www.bleepingcomputer.com/feed/', 'BleepingComputer - All Stories', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Tecnologia', 'CIO', 'https://www.cio.com/feed/', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'CISA', 'https://www.cisa.gov/rss.xml', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 15 entradas, última em 07/10/2026
    ('Tecnologia', 'Cisco Talos', 'https://blog.talosintelligence.com/rss/', 'Talos intelligence and world-class threat research team better protects you and your organization against known and…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Tecnologia', 'Cloudflare Blog', 'https://blog.cloudflare.com/rss/', 'Technical deep dives, product updates, and insights from the teams that are helping to build a better Internet.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Tecnologia', 'CNET', 'https://www.cnet.com/rss/news/', 'Product reviews, advice, how-tos and the latest news', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Tecnologia', 'Computerworld', 'https://www.computerworld.com/feed/', 'Making technology work for business', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'Crunchbase News', 'https://news.crunchbase.com/feed/', 'Data-driven reporting on private markets, startups, founders, and investors', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Tecnologia', 'CSO Online', 'https://www.csoonline.com/feed/', 'Security at the speed of business', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'CyberScoop', 'https://cyberscoop.com/feed/', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Tecnologia', 'Dark Reading', 'https://www.darkreading.com/rss.xml', 'Public RSS feed', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Tecnologia', 'Engadget', 'https://www.engadget.com/rss.xml', 'Breaking news from the worlds of technology and entertainment, and expert reviews of the latest consumer tech products.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Tecnologia', 'ExtremeTech', 'https://www.extremetech.com/feed', 'ExtremeTech is the Web''s top destination for news and analysis of emerging science and technology trends, and…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Tecnologia', 'Gizmodo', 'https://gizmodo.com/feed', 'The Future Is Here', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Tecnologia', 'Google AI Blog', 'https://blog.google/innovation-and-ai/technology/ai/rss/', 'AI', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 06/10/2026
    ('Tecnologia', 'Google Project Zero', 'https://projectzero.google/feed.xml', 'Make zeroday hard', 'rss', 'en', 'EUA'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Tecnologia', 'IEEE Spectrum', 'https://spectrum.ieee.org/feeds/feed.rss', 'IEEE Spectrum', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 05/10/2026
    ('Tecnologia', 'Import AI', 'https://importai.substack.com/feed', 'Import AI is a weekly newsletter about artificial intelligence based on detailed analysis of cutting-edge research.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 26/10/2026
    ('Tecnologia', 'InformationWeek', 'https://www.informationweek.com/rss.xml', 'Public RSS feed', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Tecnologia', 'InfoWorld', 'https://www.infoworld.com/feed/', 'Technology insight for the enterprise', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'KrebsOnSecurity', 'https://krebsonsecurity.com/feed/', 'In-depth security news and investigation', 'rss', 'en', 'EUA'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Tecnologia', 'Lifehacker', 'https://lifehacker.com/feed/rss', 'Do everything better.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Tecnologia', 'MacRumors', 'https://feeds.macrumors.com/MacRumors-All', 'Apple, iPhone, iPad, Mac News and Rumors', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'MakeUseOf', 'https://www.makeuseof.com/feed/', 'MUO is your guide to modern tech. Learn how to make use of the tech and gadgets around you, and discover cool stuff on…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'MarkTechPost', 'https://www.marktechpost.com/feed/', 'An Artificial Intelligence News Platform', 'rss', 'en', 'EUA'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Tecnologia', 'Mashable', 'https://mashable.com/feeds/rss/all', 'Mashable is a global, multi-platform media and entertainment company.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'Microsoft Security Blog', 'https://www.microsoft.com/en-us/security/blog/feed/', 'Expert coverage of cybersecurity topics', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'MIT Technology Review', 'https://www.technologyreview.com/feed/', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 40 entradas, última em 07/10/2026
    ('Tecnologia', 'Neowin', 'https://www.neowin.net/news/rss/', 'Neowin', 'rss', 'en', 'EUA'),
    -- via RSS do site: 18 entradas, última em 07/10/2026
    ('Tecnologia', 'NVIDIA Blog', 'https://blogs.nvidia.com/feed/', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 1254 entradas, última em 07/10/2026
    ('Tecnologia', 'OpenAI News', 'https://openai.com/news/rss.xml', 'The OpenAI blog', 'rss', 'en', 'EUA'),
    -- via RSS do site: 15 entradas, última em 07/10/2026
    ('Tecnologia', 'Palo Alto Networks Unit 42', 'https://unit42.paloaltonetworks.com/feed/', 'Palo Alto Networks', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'SANS Internet Storm Center', 'https://isc.sans.edu/rssfeed.xml', 'SANS Internet Storm Center - Cooperative Cyber Security Monitor', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'SC Media', 'https://www.scworld.com/feed/topic/latest', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'SecurityWeek', 'https://www.securityweek.com/feed/', 'Cybersecurity News, Insights & Analysis', 'rss', 'en', 'EUA'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Tecnologia', 'SiliconANGLE', 'https://siliconangle.com/feed/', 'Extracting the signal from the noise.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Tecnologia', 'TechCrunch', 'https://techcrunch.com/feed/', 'Startup and Technology News', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 02/10/2026
    ('Tecnologia', 'The Batch', 'https://news.google.com/rss/search?q=site%3Adeeplearning.ai/the-batch&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 16/09/2026
    ('Tecnologia', 'The Markup', 'https://themarkup.org/feeds/rss.xml', 'All stories from The Markup', 'rss', 'en', 'EUA'),
    -- via RSS do site: 26 entradas, última em 07/10/2026
    ('Tecnologia', 'The New Stack', 'https://thenewstack.io/feed/', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 5 entradas, última em 07/10/2026
    ('Tecnologia', 'The Record', 'https://therecord.media/feed', 'The Record by Recorded Future News gives exclusive, behind-the-scenes access to leaders, policymakers, researchers,…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Tecnologia', 'The Rundown AI', 'https://www.therundown.ai/feed', 'Get the latest AI news, understand why it matters, and learn how to apply it in your work.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'The Verge', 'https://www.theverge.com/rss/index.xml', 'The Verge is about technology and how it makes us feel. Founded in 2011, we offer our audience everything from…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'Thurrott', 'https://www.thurrott.com/feed', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Tecnologia', 'Tom''s Hardware', 'https://www.tomshardware.com/feeds.xml', 'All the latest content from the Tom''s Hardware team', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Tecnologia', 'Wired', 'https://www.wired.com/feed/rss', 'The latest from www.wired.com', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Tecnologia', 'XDA Developers', 'https://www.xda-developers.com/feed/', 'The world’s best source for computing news, reviews, editorials guides, and more.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Tecnologia', 'ZDNET', 'https://www.zdnet.com/rss/news/', 'News and Advice on the World''s Latest Innovations', 'rss', 'en', 'EUA'),
    -- via RSS do site: 24 entradas, última em 07/10/2026
    ('Tecnologia', 'Sifted', 'https://sifted.eu/feed', 'Quality journalism about Europe''s New Economy', 'rss', 'en', 'Europa'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Tecnologia', 'Tech.eu', 'https://tech.eu/feed/', 'The premier source of European technology news, data, research, analysis and in-depth market intelligence.', 'rss', 'en', 'Europa'),
    -- via RSS do site: 874 entradas, última em 07/10/2026
    ('Tecnologia', 'Hugging Face Blog', 'https://huggingface.co/blog/feed.xml', 'The Hugging Face blog', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 12 entradas, última em 07/10/2026
    ('Tecnologia', 'Rest of World', 'https://restofworld.org/feed/latest', 'Reporting Global Tech Stories', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Tecnologia', 'The Hacker News', 'https://feeds.feedburner.com/TheHackersNews', 'Most trusted, widely-read independent cybersecurity news source for everyone; supported by hackers and IT…', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 20 entradas, última em 06/10/2026
    ('Tecnologia', 'Ben''s Bites', 'https://www.bensbites.com/feed', 'What I''m learning building with agents (plus tools worth trying)', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 100 entradas, última em 06/10/2026
    ('Tecnologia', 'Google DeepMind', 'https://deepmind.google/blog/rss.xml', 'Read the latest articles and stories from DeepMind and find out more about our latest breakthroughs in cutting-edge AI…', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Tecnologia', 'TechRadar', 'https://www.techradar.com/feeds.xml', 'All the latest content from the TechRadar team', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Tecnologia', 'The Register', 'https://api.theregister.com/api/v1/article?orderBy=published&site_id=2&remapper=rss', 'Articles from www.theregister.com', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 24 entradas, última em 07/10/2026
    ('Tecnologia', 'Inc42', 'https://inc42.com/feed/', 'India’s #1 Startup Media & Intelligence Platform', 'rss', 'en', 'Índia'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Tecnologia', 'YourStory', 'https://yourstory.com/feed', 'YourStory.com is India’s biggest and definitive platform for startups and entrepreneurs related stories, resources,…', 'rss', 'en', 'Índia'),
    -- via Google Notícias: 69 entradas, última em 07/10/2026
    ('Ciência', 'EurekAlert!', 'https://news.google.com/rss/search?q=site%3Aeurekalert.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Ciência', 'Greater Good Magazine', 'https://greatergood.berkeley.edu/site/rss', 'Greater Good Articles, Videos and Podcasts', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Ciência', 'Live Science', 'https://www.livescience.com/feeds.xml', 'All the latest content from the Live Science team', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Ciência', 'NASA', 'https://www.nasa.gov/news-release/feed/', 'Official National Aeronautics and Space Administration Website', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 73 entradas, última em 07/10/2026
    ('Ciência', 'National Geographic', 'https://news.google.com/rss/search?q=site%3Anationalgeographic.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Ciência', 'Nautilus', 'https://nautil.us/feed', 'Science Connected', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 12 entradas, última em 24/09/2026
    ('Ciência', 'NOAA', 'https://news.google.com/rss/search?q=site%3Anoaa.gov/news&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 80 entradas, última em 07/10/2026
    ('Ciência', 'Popular Science', 'https://www.popsci.com/feed/', 'Awe-inspiring science reporting, technology news, and DIY projects. Skunks to space robots, primates to climates.…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Ciência', 'PsyPost', 'https://www.psypost.org/feed/', 'Reporting the latest scientific research on behavior, cognition and society', 'rss', 'en', 'EUA'),
    -- via RSS do site: 5 entradas, última em 07/10/2026
    ('Ciência', 'Quanta Magazine', 'https://www.quantamagazine.org/feed/', 'Illuminating science', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Ciência', 'Science News', 'https://www.sciencenews.org/feed', 'INDEPENDENT JOURNALISM SINCE 1921', 'rss', 'en', 'EUA'),
    -- via RSS do site: 60 entradas, última em 07/10/2026
    ('Ciência', 'ScienceDaily', 'https://www.sciencedaily.com/rss/all.xml', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Ciência', 'Scientific American', 'https://www.scientificamerican.com/platform/syndication/rss/', 'Scientific American is the essential guide to the most awe-inspiring advances in science and technology, explaining…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Ciência', 'Smithsonian Magazine', 'https://www.smithsonianmag.com/rss/latest_articles/', 'RSS feed for with the latest articles', 'rss', 'en', 'EUA'),
    -- via RSS do site: 16 entradas, última em 07/10/2026
    ('Ciência', 'SpaceNews', 'https://spacenews.com/feed/', 'Covering the business and politics of space', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Ciência', 'CERN', 'https://home.cern/feed/', null, 'rss', 'en', 'Europa'),
    -- via RSS do site: 9 entradas, última em 07/10/2026
    ('Ciência', 'European Space Agency', 'https://www.esa.int/rssfeed/Our_Activities/Space_News', 'ESA Top News', 'rss', 'en', 'Europa'),
    -- via RSS do site: 60 entradas, última em 07/10/2026
    ('Ciência', 'New Atlas', 'https://newatlas.com/index.rss', 'Extraordinary ideas and innovations moving the world forward.', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Ciência', 'Phys.org', 'https://phys.org/rss-feed/', 'Phys.org internet news portal provides the latest news on science including: Physics, Nanotechnology, Life Sciences,…', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Ciência', 'The Conversation', 'https://theconversation.com/us/articles.atom', null, 'rss', 'en', 'Internacional'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Ciência', 'Universe Today', 'https://www.universetoday.com/rss.xml', 'Space and Astronomy News from Universe Today', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 75 entradas, última em 07/10/2026
    ('Ciência', 'Nature', 'https://www.nature.com/nature.rss', 'Nature is the foremost international weekly scientific journal in the world and is the flagship journal for Nature…', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Ciência', 'New Scientist', 'https://www.newscientist.com/feed/', 'Science news and science articles from New Scientist', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 11 entradas, última em 07/10/2026
    ('Meio ambiente', 'The Narwhal', 'https://thenarwhal.ca/feed/', 'The Narwhal’s team of investigative journalists dives deep to tell stories about the natural world in Canada you can’t…', 'rss', 'en', 'Canadá'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Meio ambiente', 'Canary Media', 'https://www.canarymedia.com/rss.rss', 'The leading newsroom covering the transition to clean energy, electrification and climate solutions. We report on how…', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 52 entradas, última em 30/09/2026
    ('Meio ambiente', 'Climate Central', 'https://news.google.com/rss/search?q=site%3Aclimatecentral.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 14 entradas, última em 07/10/2026
    ('Meio ambiente', 'EIA', 'https://www.eia.gov/rss/todayinenergy.xml', 'Short, timely articles with graphics on energy facts, issues, and trends.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Meio ambiente', 'Grist', 'https://grist.org/feed/', '25 Years on the Climate Beat', 'rss', 'en', 'EUA'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Meio ambiente', 'Heatmap', 'https://heatmap.news/feeds/feed.rss', 'Heatmap News', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 97 entradas, última em 06/10/2026
    ('Meio ambiente', 'Oil & Gas Journal', 'https://news.google.com/rss/search?q=site%3Aogj.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Meio ambiente', 'Rigzone', 'https://news.google.com/rss/search?q=site%3Arigzone.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Meio ambiente', 'Utility Dive', 'https://www.utilitydive.com/feeds/news/', 'Utility industry news and analysis for energy professionals.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Meio ambiente', 'Yale Climate Connections', 'https://yaleclimateconnections.org/feed/', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 06/10/2026
    ('Meio ambiente', 'Earth.org', 'https://earth.org/feed/', 'Free, non-profit and independent environmental journalism.', 'rss', 'en', 'Internacional'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Meio ambiente', 'IEA', 'https://news.google.com/rss/search?q=site%3Aiea.org/news&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 32 entradas, última em 07/10/2026
    ('Meio ambiente', 'Mongabay', 'https://news.mongabay.com/feed/', 'Environmental science and conservation news', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Meio ambiente', 'PV Magazine', 'https://www.pv-magazine.com/feed/', 'pv magazine Global, the leading solar and energy storage trade media platform. Industry news covering market trends,…', 'rss', 'en', 'Internacional'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Meio ambiente', 'Recharge', 'https://www.rechargenews.com/sitemap.xml', null, 'sitemap', 'en', 'Internacional'),
    -- via RSS do site: 44 entradas, última em 07/10/2026
    ('Meio ambiente', 'World Nuclear News', 'https://www.world-nuclear-news.org/rss', 'World Nuclear News recent stories', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 12 entradas, última em 30/09/2026
    ('Meio ambiente', 'Carbon Brief', 'https://www.carbonbrief.org/feed', null, 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 40 entradas, última em 07/10/2026
    ('Meio ambiente', 'Climate Home News', 'https://www.climatechangenews.com/feed/', 'Climate change news, analysis and commentary focused on developments in global climate politics', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Meio ambiente', 'The Guardian – Environment', 'https://www.theguardian.com/uk/environment/rss', 'Latest Environment news, comment and analysis from the Guardian, the world''s leading liberal voice', 'rss', 'en', 'Reino Unido'),
    -- via Google Notícias: 100 entradas, última em 22/09/2026
    ('Saúde', 'CDC', 'https://news.google.com/rss/search?q=site%3Acdc.gov/media/releases&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 05/10/2026
    ('Saúde', 'FDA', 'https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 25 entradas, última em sem data
    ('Saúde', 'Fierce Healthcare', 'https://www.fiercehealthcare.com/rss/xml', 'a feed of the latest articles on our website', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Saúde', 'Healthcare Dive', 'https://www.healthcaredive.com/feeds/news/', 'Healthcare', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Saúde', 'KFF Health News', 'https://kffhealthnews.org/feed/', 'KFF Health News produces in-depth journalism on health issues and is a core operating program of KFF.', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 96 entradas, última em 06/10/2026
    ('Saúde', 'Medical News Today', 'https://news.google.com/rss/search?q=site%3Amedicalnewstoday.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Saúde', 'MedPage Today', 'https://www.medpagetoday.com/rss/headlines.xml', 'Latest Headlines News', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 97 entradas, última em 06/10/2026
    ('Saúde', 'Modern Healthcare', 'https://news.google.com/rss/search?q=site%3Amodernhealthcare.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 77 entradas, última em 07/10/2026
    ('Saúde', 'NIH', 'https://news.google.com/rss/search?q=site%3Anih.gov/news-events/news-releases&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Saúde', 'NPR Health', 'https://feeds.npr.org/1128/rss.xml', 'Health', 'rss', 'en', 'EUA'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Saúde', 'Psychology Today', 'https://www.psychologytoday.com/us/front/feed', 'The latest blog posts from Psychology Today', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Saúde', 'STAT', 'https://www.statnews.com/feed/', 'Reporting from the frontiers of health and medicine', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 74 entradas, última em 17/09/2026
    ('Saúde', 'WebMD', 'https://news.google.com/rss/search?q=site%3Awebmd.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Saúde', 'Medical Xpress', 'https://medicalxpress.com/rss-feed/', 'Medical Xpress internet news portal provides the latest news on science including: Physics, Nanotechnology, Life…', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 570 entradas, última em 07/10/2026
    ('Esportes', 'Bleacher Report', 'https://feeds.bleacherreport.com/articles', 'Bleacher Report - The latest articles about sports news, rumors, teams, events, and more.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 36 entradas, última em 07/10/2026
    ('Esportes', 'CBS Sports', 'https://www.cbssports.com/rss/headlines/', 'The latest sports news from CBSSports.com', 'rss', 'en', 'EUA'),
    -- via RSS do site: 46 entradas, última em 08/10/2026
    ('Esportes', 'ESPN', 'https://www.espn.com/espn/rss/news', 'Latest TOP news from www.espn.com', 'rss', 'en', 'EUA'),
    -- via RSS do site: 23 entradas, última em 08/10/2026
    ('Esportes', 'ESPN FC', 'https://www.espn.com/espn/rss/soccer/news', 'Latest SOCCER news from www.espn.com', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Esportes', 'Fox Sports', 'https://api.foxsports.com/v2/content/optimized-rss?partnerKey=MB0Wehpmuj2lUhuRhQaafhBjAJqaPU244mlTDK1i&size=30', 'The latest sports videos, news, articles, and stories from FOX Sports.', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 80 entradas, última em 07/10/2026
    ('Esportes', 'MLS', 'https://news.google.com/rss/search?q=site%3Amlssoccer.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 21 entradas, última em 06/10/2026
    ('Esportes', 'NBA', 'https://www.nba.com/sitemap_news.xml#caminho=/news', null, 'sitemap', 'en', 'EUA'),
    -- via RSS do site: 4 entradas, última em 07/10/2026
    ('Esportes', 'NBC Sports', 'https://www.nbcsports.com/index.atom', 'Stay up-to-date with the latest sports news and scores from NBC Sports.', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Esportes', 'NFL', 'https://news.google.com/rss/search?q=site%3Anfl.com/news&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Esportes', 'Pro Football Talk', 'https://www.nbcsports.com/profootballtalk.rss', 'Latest news from ProFootballTalk.com', 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Esportes', 'Sporting News', 'https://www.sportingnews.com/us-es/news-sitemap.xml#caminho=/us', null, 'sitemap', 'en', 'EUA'),
    -- via RSS do site: 89 entradas, última em 07/10/2026
    ('Esportes', 'Sports Illustrated', 'https://www.si.com/feed', null, 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Esportes', 'The Athletic', 'https://www.nytimes.com/sitemaps/new/news.xml.gz#caminho=/athletic', null, 'sitemap', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Esportes', 'Yahoo Sports', 'https://sports.yahoo.com/rss/', 'Yahoo! Sports - Comprehensive news, scores, standings, fantasy games, rumors, and more', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em sem data
    ('Esportes', 'Formula 1', 'https://www.formula1.com/en/latest/all.xml', 'Don''t miss a Formula 1 moment – with the latest news, videos, standings and results. Go behind the scenes and get…', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Esportes', 'Motorsport.com', 'https://www.motorsport.com/rss/all/news/', null, 'rss', 'en', 'Internacional'),
    -- via RSS do site: 263 entradas, última em 07/10/2026
    ('Esportes', 'RacingNews365', 'https://racingnews365.com/feed/news.xml', null, 'rss', 'en', 'Internacional'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Esportes', 'Autosport', 'https://www.autosport.com/rss/all/news/', null, 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 76 entradas, última em 07/10/2026
    ('Esportes', 'BBC Sport', 'https://feeds.bbci.co.uk/sport/rss.xml', 'BBC Sport - Sport Front Page', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Esportes', 'Sky Sports', 'https://www.skysports.com/rss/12040', 'Sports News', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 59 entradas, última em 07/10/2026
    ('Esportes', 'The Guardian – Football', 'https://www.theguardian.com/football/rss', 'Latest Football news, comment and analysis from the Guardian, the world''s leading liberal voice', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 15 entradas, última em 07/10/2026
    ('Esportes', 'The Race', 'https://www.the-race.com/rss/', 'All the latest motorsport news, videos and podcasts - both on track and online with F1, MotoGP, Formula E and more.', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Entretenimento', '/Film', 'https://www.slashfilm.com/feed/', 'The latest movie and television news, reviews, film trailers, exclusive interviews, and opinions - since 2005.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 38 entradas, última em 07/10/2026
    ('Entretenimento', 'Bandcamp Daily', 'https://daily.bandcamp.com/feed', 'Bandcamp Daily is your guide to the artists, fans and labels on Bandcamp.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'Billboard', 'https://www.billboard.com/feed/', 'Music Charts, News, Photos & Video', 'rss', 'en', 'EUA'),
    -- via RSS do site: 15 entradas, última em 06/10/2026
    ('Entretenimento', 'BrooklynVegan', 'https://www.brooklynvegan.com/feed/', 'Music, Photos, News and more', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'Collider', 'https://collider.com/feed/', 'Stay up to date with new movie news, watch the latest movie trailers & get trusted reviews of upcoming movies & more…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 15 entradas, última em 07/10/2026
    ('Entretenimento', 'Consequence', 'https://consequence.net/feed/', 'Music, Film, TV and Pop Culture News for the Mainstream and Underground', 'rss', 'en', 'EUA'),
    -- via RSS do site: 12 entradas, última em 07/10/2026
    ('Entretenimento', 'Deadline', 'https://deadline.com/feed/', 'Hollywood Entertainment Breaking News', 'rss', 'en', 'EUA'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Entretenimento', 'Destructoid', 'https://www.destructoid.com/feed/', 'A Site About Video Games', 'rss', 'en', 'EUA'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Entretenimento', 'E! News', 'https://eol-feeds.eonline.com/rssfeed/us/top_stories', 'News from across the show-biz spectrum-TV, movies, music and celebrities', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Entretenimento', 'Entertainment Weekly', 'https://feeds-api.dotdashmeredith.com/v1/rss/google/06e092d0-4dff-468a-93db-8d6a995730b4', 'Latest Entertainment Weekly Articles and Interviews', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Entretenimento', 'Game Informer', 'https://gameinformer.com/rss.xml', 'Game Informer is your source for the latest in video game news, reviews, previews, podcasts, and features.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 15 entradas, última em 07/10/2026
    ('Entretenimento', 'GameSpot', 'https://www.gamespot.com/feeds/mashup/', 'GameSpot''s Everything Feed! All the latest from GameSpot', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Entretenimento', 'IGN', 'https://feeds.feedburner.com/ign/all', 'The latest IGN news, reviews and videos about video games, movies, TV, tech and comics', 'rss', 'en', 'EUA'),
    -- via RSS do site: 12 entradas, última em 07/10/2026
    ('Entretenimento', 'IndieWire', 'https://www.indiewire.com/feed/', 'The Voice of Creative Independence', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Entretenimento', 'Kotaku', 'https://kotaku.com/feed', 'Gaming Reviews, News, Tips and More.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Entretenimento', 'PC Gamer', 'https://www.pcgamer.com/rss/', null, 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Entretenimento', 'People', 'https://people.com/google-news-sitemap.xml', null, 'sitemap', 'en', 'EUA'),
    -- via RSS do site: 29 entradas, última em 07/10/2026
    ('Entretenimento', 'Pitchfork', 'https://pitchfork.com/feed/feed-news/rss', 'News content RSS feed', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'PlayStation Blog', 'https://blog.playstation.com/feed/', 'Official PlayStation Blog for news and video updates on PlayStation, PS5, PS4, PS VR, PlayStation Plus and more.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'Polygon', 'https://www.polygon.com/feed/', 'Your source for the latest in video games, sci-fi, fantasy, tabletop games, anime, horror, books, and comics.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'Rolling Stone', 'https://www.rollingstone.com/feed/', 'Music, Film, TV and Political News Coverage', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'Screen Rant', 'https://screenrant.com/feed/', 'ScreenRant debuted in 2003 and has grown into the largest source of breaking entertainment news & original features…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'Spin', 'https://www.spinmagazine.com/feed/', 'Music News, Album Reviews, Concert Photos, Videos and More', 'rss', 'en', 'EUA'),
    -- via RSS do site: 40 entradas, última em 07/10/2026
    ('Entretenimento', 'Stereogum', 'https://stereogum.com/feed', 'The world''s best music blog.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 71 entradas, última em 07/10/2026
    ('Entretenimento', 'The A.V. Club', 'https://www.avclub.com/rss.xml', 'AV Club: Pop culture obsessives writing for the pop culture obsessed.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'The Hollywood Reporter', 'https://www.hollywoodreporter.com/feed/', 'Movie news, TV news, awards news, lifestyle news, business news and more from The Hollywood Reporter.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'TheWrap', 'https://www.thewrap.com/feed/', 'Your trusted source for breaking entertainment news, film reviews, TV updates and Hollywood insights. Stay informed…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Entretenimento', 'TMZ', 'https://www.tmz.com/rss.xml', 'Celebrity Gossip and Entertainment News, Covering Celebrity News and Hollywood Rumors. Get All The Latest Gossip at…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'Variety', 'https://variety.com/feed/', 'Entertainment news, film reviews, awards, film festivals, box office, entertainment industry conferences', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'Xbox Wire', 'https://news.xbox.com/en-us/feed/', 'Your source for news, information, product releases, events, sports, entertainment & exclusive content relating to Xbox', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', '80 Level', 'https://80.lv/feed', '80 Level is an industry-leading platform for game developers, digital artists, animators, video game enthusiasts, CGI…', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'Music Business Worldwide', 'https://www.musicbusinessworldwide.com/feed/', 'News, jobs and analysis for the global music industry', 'rss', 'en', 'Internacional'),
    -- via Google Notícias: 61 entradas, última em 07/10/2026
    ('Entretenimento', 'Resident Advisor', 'https://news.google.com/rss/search?q=site%3Ara.co&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Entretenimento', 'DJ Mag', 'https://djmag.com/feed', null, 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 139 entradas, última em 07/10/2026
    ('Entretenimento', 'Empire', 'https://rss.onebauer.media/api/feed-aggregator?hostname=https://www.empireonline.com', 'Latest news and content from www.empireonline.com', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Entretenimento', 'Eurogamer', 'https://www.eurogamer.net/feed', 'This is a feed of the latest articles from Eurogamer.net.', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Entretenimento', 'GamesRadar+', 'https://www.gamesradar.com/feeds.xml', 'All the latest content from the GamesRadar+ team', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Entretenimento', 'Nintendo Life', 'https://www.nintendolife.com/feeds/latest', null, 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'NME', 'https://www.nme.com/feed', 'NME brings you the latest music and pop culture news and reviews, along with videos and galleries, band features,…', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 75 entradas, última em 07/10/2026
    ('Entretenimento', 'PCGamesN', 'https://www.pcgamesn.com/mainrss.xml', 'The latest PC games news, features, updates, guides, and hands-on reviews. Plus all the latest from our hardware…', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Entretenimento', 'Pure Xbox', 'https://www.purexbox.com/feeds/latest', null, 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Entretenimento', 'Push Square', 'https://www.pushsquare.com/feeds/latest', null, 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Entretenimento', 'Rock Paper Shotgun', 'https://www.rockpapershotgun.com/feed', 'This is a feed of the latest articles from Rock Paper Shotgun.', 'rss', 'en', 'Reino Unido'),
    -- via Google Notícias: 99 entradas, última em 07/10/2026
    ('Entretenimento', 'Screen Daily', 'https://news.google.com/rss/search?q=site%3Ascreendaily.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'The Line of Best Fit', 'https://www.thelineofbestfit.com/feed', 'New Music Discovery', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Entretenimento', 'Video Games Chronicle', 'https://www.videogameschronicle.com/feed/', 'Best video game news first, plus reviews and guides', 'rss', 'en', 'Reino Unido'),
    -- via Google Notícias: 97 entradas, última em 07/10/2026
    ('Automóveis', 'Automotive News', 'https://news.google.com/rss/search?q=site%3Aautonews.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Automóveis', 'Car and Driver', 'https://www.caranddriver.com/rss/all.xml/', 'RSS feed for Latest Content - Car and Driver', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Automóveis', 'InsideEVs', 'https://insideevs.com/rss/news/all/', 'Get breaking news, in-depth articles and press releases covering News', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Automóveis', 'Jalopnik', 'https://www.jalopnik.com/feed/', 'From cars to motorcycles, Jalopnik is your go-to site covering everything with an engine—including automotive news,…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Automóveis', 'Road & Track', 'https://www.roadandtrack.com/rss/all.xml/', 'RSS feed for Latest Content - Road & Track', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Automóveis', 'Teslarati', 'https://www.teslarati.com/feed/', 'Tesla news, rumors and reviews. SpaceX, Elon Musk, batteries, energy, premium EV market.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Automóveis', 'The Drive', 'https://www.thedrive.com/feed', 'Car News, Reviews, and Culture', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Automóveis', 'Motor1', 'https://www.motor1.com/rss/news/all/', 'Get breaking news, in-depth articles and press releases covering News', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Automóveis', 'Auto Express', 'https://www.autoexpress.co.uk/feed/all', 'Sitewide RSS feed', 'rss', 'en', 'Reino Unido'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Automóveis', 'Top Gear', 'https://news.google.com/rss/search?q=site%3Atopgear.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 138 entradas, última em 07/10/2026
    ('Mundo', 'Deutsche Welle', 'https://rss.dw.com/rdf/rss-en-all', 'Deutsche Welle', 'rss', 'en', 'Alemanha'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'The Arizona Republic', 'https://www.azcentral.com/news-sitemap.xml', null, 'sitemap', 'en', 'Arizona (EUA)'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Mundo', 'Arab News', 'https://news.google.com/rss/search?q=site%3Aarabnews.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Arábia Saudita'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Mundo', 'ABC News Australia', 'https://www.abc.net.au/news/feed/51120/rss.xml', null, 'rss', 'en', 'Austrália'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'Brisbane Times', 'https://www.brisbanetimes.com.au/rss/feed.xml', 'The top News headlines from The Brisbane Times. For all the news, visit https://www.brisbanetimes.com.au/', 'rss', 'en', 'Austrália'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'Crikey', 'https://www.crikey.com.au/feed/', 'On politics, media, business, the environment and life', 'rss', 'en', 'Austrália'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'Guardian Australia', 'https://www.theguardian.com/australia-news/rss', 'Latest news, breaking news and current affairs coverage from across Australia from theguardian.com', 'rss', 'en', 'Austrália'),
    -- via Google Notícias: 97 entradas, última em 07/10/2026
    ('Mundo', 'news.com.au', 'https://news.google.com/rss/search?q=site%3Anews.com.au&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Austrália'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Mundo', 'SBS News', 'https://news.google.com/rss/search?q=site%3Asbs.com.au/news&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Austrália'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'The Age', 'https://www.theage.com.au/rss/feed.xml', 'The top News headlines from The Age. For all the news, visit https://www.theage.com.au/', 'rss', 'en', 'Austrália'),
    -- via Google Notícias: 97 entradas, última em 07/10/2026
    ('Mundo', 'The Australian', 'https://news.google.com/rss/search?q=site%3Atheaustralian.com.au&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Austrália'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'The Canberra Times', 'https://www.canberratimes.com.au/rss.xml', 'Latest news, sport, football and business news.', 'rss', 'en', 'Austrália'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'The Sydney Morning Herald', 'https://www.smh.com.au/rss/feed.xml', 'The top News headlines from The Sydney Morning Herald. For all the news, visit https://www.smh.com.au', 'rss', 'en', 'Austrália'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'WAtoday', 'https://www.watoday.com.au/rss/feed.xml', 'The top News headlines from WA Today. For all the news, visit https://www.watoday.com.au', 'rss', 'en', 'Austrália'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'Boston.com', 'https://www.boston.com/feed/', 'Boston.com', 'rss', 'en', 'Boston (EUA)'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'The Boston Globe', 'https://www.bostonglobe.com/arc/outboundfeeds/news-sitemap/?outputType=xml', null, 'sitemap', 'en', 'Boston (EUA)'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Mundo', 'WBUR', 'https://rss.wbur.org/wbur/rss', 'A lot happens in Boston every day. To help you keep up, WBUR, Boston''s NPR News station, pulled these stories together…', 'rss', 'en', 'Boston (EUA)'),
    -- via RSS do site: 12 entradas, última em 07/10/2026
    ('Mundo', 'Berkeleyside', 'https://www.berkeleyside.org/feed', 'Nonprofit news. Free for all, funded by readers.', 'rss', 'en', 'Califórnia (EUA)'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'CalMatters', 'https://calmatters.org/feed/', 'California, explained', 'rss', 'en', 'Califórnia (EUA)'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'Calgary Herald', 'https://calgaryherald.com/feed', 'Calgary Latest News, Breaking Headlines & Sports', 'rss', 'en', 'Canadá'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Mundo', 'CityNews', 'https://news.google.com/rss/search?q=site%3Atoronto.citynews.ca&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Canadá'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'CTV News', 'https://www.ctvnews.ca/arc/outboundfeeds/sitemap-news-index/', null, 'sitemap', 'en', 'Canadá'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'Global News', 'https://globalnews.ca/feed/', null, 'rss', 'en', 'Canadá'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'National Post', 'https://nationalpost.com/feed', 'Canadian News, World News and Breaking Headlines', 'rss', 'en', 'Canadá'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'Ottawa Citizen', 'https://ottawacitizen.com/feed', 'Ottawa Latest News, Breaking Headlines & Sports', 'rss', 'en', 'Canadá'),
    -- via Google Notícias: 98 entradas, última em 07/10/2026
    ('Mundo', 'The Globe and Mail', 'https://news.google.com/rss/search?q=site%3Atheglobeandmail.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Canadá'),
    -- via Google Notícias: 89 entradas, última em 07/10/2026
    ('Mundo', 'Toronto Star', 'https://news.google.com/rss/search?q=site%3Athestar.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Canadá'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'Vancouver Sun', 'https://vancouversun.com/feed', 'Vancouver News, Top Stories, Breaking Headlines & Videos', 'rss', 'en', 'Canadá'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Mundo', 'Al Jazeera English', 'https://www.aljazeera.com/xml/rss/all.xml', 'Breaking News, World News and Video from Al Jazeera', 'rss', 'en', 'Catar'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'Block Club Chicago', 'https://blockclubchicago.org/feed/', 'Your Neighborhood News Site', 'rss', 'en', 'Chicago (EUA)'),
    -- via RSS do site: 55 entradas, última em 07/10/2026
    ('Mundo', 'Chicago Sun-Times', 'https://chicago.suntimes.com/rss/index.xml', null, 'rss', 'en', 'Chicago (EUA)'),
    -- via Google Notícias: 97 entradas, última em 07/10/2026
    ('Mundo', 'Chicago Tribune', 'https://news.google.com/rss/search?q=site%3Achicagotribune.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Chicago (EUA)'),
    -- via RSS do site: 21 entradas, última em 07/10/2026
    ('Mundo', 'WBEZ', 'https://www.wbez.org/rss/index.xml', null, 'rss', 'en', 'Chicago (EUA)'),
    -- via sitemap de notícias: 16 entradas, última em 07/10/2026
    ('Mundo', 'Caixin Global', 'https://www.caixinglobal.com/sitemap_news.xml', null, 'sitemap', 'en', 'China'),
    -- via Google Notícias: 83 entradas, última em 07/10/2026
    ('Mundo', 'China Daily', 'https://news.google.com/rss/search?q=site%3Achinadaily.com.cn&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'China'),
    -- via Google Notícias: 100 entradas, última em 06/10/2026
    ('Mundo', 'ChinaFile', 'https://news.google.com/rss/search?q=site%3Achinafile.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'China'),
    -- via RSS do site: 51 entradas, última em sem data
    ('Mundo', 'Sixth Tone', 'https://api.sixthtone.com/cont/output/rssApi', 'Sixth Tone RSS', 'rss', 'en', 'China'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Mundo', 'South China Morning Post', 'https://www.scmp.com/rss/91/feed/', 'All the latest breaking news from Hong Kong, China and around the world', 'rss', 'en', 'China'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'Denverite', 'https://denverite.com/feed/', 'News for Denver know-it-alls, newcomers and everybody in between.', 'rss', 'en', 'Colorado (EUA)'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'The Colorado Sun', 'https://coloradosun.com/feed/', 'Telling stories that matter in a dynamic, evolving state.', 'rss', 'en', 'Colorado (EUA)'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Mundo', 'The Korea Herald', 'https://www.koreaherald.com/rss/newsAll', null, 'rss', 'en', 'Coreia do Sul'),
    -- via RSS do site: 15 entradas, última em 07/10/2026
    ('Mundo', 'The Korea Times', 'https://feed.koreatimes.co.kr/k/allnews.xml', 'Whole News', 'rss', 'en', 'Coreia do Sul'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Mundo', 'ABC News', 'https://abcnews.com/abcnews/topstories', null, 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Mundo', 'Associated Press', 'https://news.google.com/rss/search?q=site%3Aapnews.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Mundo', 'Atlantic Council', 'https://www.atlanticcouncil.org/feed/', 'Shaping the global future together', 'rss', 'en', 'EUA'),
    -- via RSS do site: 15 entradas, última em 07/10/2026
    ('Mundo', 'Breaking Defense', 'https://breakingdefense.com/feed/', 'Defense technology, policy and national security news', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 96 entradas, última em 06/10/2026
    ('Mundo', 'Carnegie Endowment', 'https://news.google.com/rss/search?q=site%3Acarnegieendowment.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Mundo', 'CBS News', 'https://www.cbsnews.com/latest/rss/main', 'Headlines From CBSNews.com', 'rss', 'en', 'EUA'),
    -- via RSS do site: 24 entradas, última em 07/10/2026
    ('Mundo', 'Council on Foreign Relations', 'https://www.cfr.org/feed', 'The latest content from the Council on Foreign Relations including articles, backgrounders, reports, books, and…', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 64 entradas, última em 07/10/2026
    ('Mundo', 'CSIS', 'https://news.google.com/rss/search?q=site%3Acsis.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 25 entradas, última em 07/10/2026
    ('Mundo', 'Defense News', 'https://www.defensenews.com/arc/outboundfeeds/sitemap-news/?outputType=xml', null, 'sitemap', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'Foreign Affairs', 'https://www.foreignaffairs.com/rss.xml', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Mundo', 'Foreign Policy', 'https://foreignpolicy.com/feed/', 'the Global Magazine of News and Ideas', 'rss', 'en', 'EUA'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Mundo', 'Fox News', 'https://moxie.foxnews.com/google-publisher/latest.xml', 'Discover the latest breaking news feed with Fox. Find out what the latest news is and read about the latest news…', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 04/10/2026
    ('Mundo', 'Institute for the Study of War', 'https://news.google.com/rss/search?q=site%3Aunderstandingwar.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'MSNBC', 'https://www.ms.now/feed', 'My source | News | Opinion | World', 'rss', 'en', 'EUA'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Mundo', 'NBC News', 'https://feeds.nbcnews.com/nbcnews/public/news', 'NBC News Top Stories', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'Newsweek', 'https://www.newsweek.com/rss', 'Latest News', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'NPR', 'https://feeds.npr.org/1001/rss.xml', 'NPR news, audio, and podcasts. Coverage of breaking stories, national and world news, politics, business, science,…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'PBS NewsHour', 'https://www.pbs.org/newshour/feeds/rss/headlines', 'The latest news, analysis and reporting from PBS News Hour.', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 99 entradas, última em 06/10/2026
    ('Mundo', 'RAND', 'https://news.google.com/rss/search?q=site%3Arand.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Mundo', 'Responsible Statecraft', 'https://responsiblestatecraft.org/feeds/feed.rss', 'Responsible Statecraft', 'rss', 'en', 'EUA'),
    -- via RSS do site: 259 entradas, última em 07/10/2026
    ('Mundo', 'Semafor', 'https://www.semafor.com/rss.xml', 'A global news platform for breaking stories, analysis and video.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Mundo', 'The Atlantic', 'https://www.theatlantic.com/feed/all/', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'The Christian Science Monitor', 'https://rss.csmonitor.com/feeds/all', 'The Christian Science Monitor is an international news organization that delivers thoughtful, global coverage via its…', 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'The Daily Beast', 'https://www.thedailybeast.com/arc/outboundfeeds/sitemap-news-index?outputType=xml', null, 'sitemap', 'en', 'EUA'),
    -- via RSS do site: 18 entradas, última em 07/10/2026
    ('Mundo', 'The New York Times', 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 56 entradas, última em 07/10/2026
    ('Mundo', 'The New York Times – World', 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 39 entradas, última em 07/10/2026
    ('Mundo', 'The War Zone', 'https://www.twz.com/feed', 'A strong offense for the world of defense.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 19 entradas, última em 07/10/2026
    ('Mundo', 'The Washington Post – National', 'https://feeds.washingtonpost.com/rss/national', 'The Washington Post''s national news coverage. Get the latest U.S. news, including science, health, climate and the…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 16 entradas, última em 07/10/2026
    ('Mundo', 'The Washington Post – World', 'https://feeds.washingtonpost.com/rss/world', 'The Washington Post World section provides information and analysis of breaking world news stories. In addition to our…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Mundo', 'TIME', 'https://time.com/feed/', 'Breaking news and analysis from TIME.com. Politics, world news, photos, video, tech reviews, health, science and…', 'rss', 'en', 'EUA'),
    -- via RSS do site: 24 entradas, última em 07/10/2026
    ('Mundo', 'UPI', 'https://rss.upi.com/news/top_news.rss', 'Top News - UPI.com', 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'USA Today', 'https://www.usatoday.com/news-sitemap.xml', null, 'sitemap', 'en', 'EUA'),
    -- via RSS do site: 17 entradas, última em 07/10/2026
    ('Mundo', 'Yahoo News', 'https://news.yahoo.com/rss/', 'yahoo.com/news Top Stories', 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'The National', 'https://www.thenationalnews.com/arc/outboundfeeds/news-sitemap/?outputType=xml', null, 'sitemap', 'en', 'Emirados Árabes'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Mundo', 'Euronews', 'https://www.euronews.com/rss', 'Latest news from Euronews', 'rss', 'en', 'Europa'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'Politico Europe', 'https://www.politico.eu/feed/', 'European Politics, Policy, Government News', 'rss', 'en', 'Europa'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'Radio Free Europe/Radio Liberty', 'https://www.rferl.org/api/', 'Radio Free Europe / Radio Liberty is an international news organization serving Central and Eastern Europe, the…', 'rss', 'en', 'Europa'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'The Philadelphia Inquirer', 'https://www.inquirer.com/sitemaps/48hour-news-sitemap-partner.xml', null, 'sitemap', 'en', 'Filadélfia (EUA)'),
    -- via Google Notícias: 86 entradas, última em 07/10/2026
    ('Mundo', 'Miami Herald', 'https://news.google.com/rss/search?q=site%3Amiamiherald.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Flórida (EUA)'),
    -- via Google Notícias: 95 entradas, última em 07/10/2026
    ('Mundo', 'Tampa Bay Times', 'https://news.google.com/rss/search?q=site%3Atampabay.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Flórida (EUA)'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'WLRN', 'https://www.wlrn.org/news-sitemap-content.xml', null, 'sitemap', 'en', 'Flórida (EUA)'),
    -- via RSS do site: 24 entradas, última em 07/10/2026
    ('Mundo', 'France 24', 'https://www.france24.com/en/rss', 'Breaking news and world news from France 24 on Business, Sports, Culture. Video news. News from the US, Europe, Asia…', 'rss', 'en', 'França'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Mundo', 'AFP', 'https://news.google.com/rss/search?q=site%3Aafp.com/en&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 10 entradas, última em sem data
    ('Mundo', 'Crisis Group', 'https://www.crisisgroup.org/rss', null, 'rss', 'en', 'Internacional'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'Reuters', 'https://www.reuters.com/arc/outboundfeeds/news-sitemap-index/?outputType=xml', null, 'sitemap', 'en', 'Internacional'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Mundo', 'Haaretz', 'https://news.google.com/rss/search?q=site%3Ahaaretz.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Israel'),
    -- via sitemap de notícias: 30 entradas, última em 08/10/2026
    ('Mundo', 'The Jerusalem Post', 'https://www.jpost.com/GoogleNewsSiteMap/GNSiteMap', null, 'sitemap', 'en', 'Israel'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'Nikkei Asia', 'https://asia.nikkei.com/sitemap_news.xml', null, 'sitemap', 'en', 'Japão'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Mundo', 'The Japan Times', 'https://www.japantimes.co.jp/feed/', 'News on Japan, Business News, Opinion, Sports, Entertainment and More', 'rss', 'en', 'Japão'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Mundo', 'LAist', 'https://laist.com/index.atom', 'Local and national news, NPR, things to do, food recommendations and guides to Los Angeles, Orange County and the…', 'rss', 'en', 'Los Angeles (EUA)'),
    -- via RSS do site: 136 entradas, última em 07/10/2026
    ('Mundo', 'Los Angeles Times', 'https://www.latimes.com/index.rss', 'The L.A. Times is a leading source of breaking news, entertainment, sports, politics, and more for Southern California…', 'rss', 'en', 'Los Angeles (EUA)'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'Detroit Free Press', 'https://www.freep.com/news-sitemap.xml', null, 'sitemap', 'en', 'Michigan (EUA)'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'MinnPost', 'https://www.minnpost.com/feed/', 'Nonprofit, independent journalism. Supported by readers.', 'rss', 'en', 'Minnesota (EUA)'),
    -- via Google Notícias: 98 entradas, última em 07/10/2026
    ('Mundo', 'Star Tribune', 'https://news.google.com/rss/search?q=site%3Astartribune.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Minnesota (EUA)'),
    -- via RSS do site: 15 entradas, última em 07/10/2026
    ('Mundo', 'Premium Times', 'https://www.premiumtimesng.com/feed', 'Premium Times - Nigeria''bs leading online newspaper, delivering breaking news and deep investigative reports from…', 'rss', 'en', 'Nigéria'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'amNY', 'https://www.amny.com/feed/', 'New York City News: Latest Headlines, Videos & Pictures', 'rss', 'en', 'Nova York (EUA)'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Mundo', 'Gothamist', 'https://news.google.com/rss/search?q=site%3Agothamist.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Nova York (EUA)'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Mundo', 'New York Daily News', 'https://news.google.com/rss/search?q=site%3Anydailynews.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Nova York (EUA)'),
    -- via RSS do site: 22 entradas, última em 07/10/2026
    ('Mundo', 'New York Post', 'https://nypost.com/feed/', 'Your source for breaking news, news about New York, sports, business, entertainment, opinion, real estate, culture,…', 'rss', 'en', 'Nova York (EUA)'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'The City', 'https://www.thecityreporter.nyc/feed/', 'Local News for New Yorkers', 'rss', 'en', 'Nova York (EUA)'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'Al-Monitor', 'https://www.al-monitor.com/rss', 'Al Monitor', 'rss', 'en', 'Oriente Médio'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'Middle East Eye', 'https://www.middleeasteye.net/rss', null, 'rss', 'en', 'Oriente Médio'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Mundo', 'Middle East Monitor', 'https://www.middleeastmonitor.com/feed/', 'Latest news from the Middle East and North Africa', 'rss', 'en', 'Oriente Médio'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Mundo', 'The New Arab', 'https://news.google.com/rss/search?q=site%3Anewarab.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Oriente Médio'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'Billy Penn', 'https://billypenn.com/feed/', 'Philadelphia local news: Neighborhoods, politics, food, and fun', 'rss', 'en', 'Pensilvânia (EUA)'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'Pittsburgh Post-Gazette', 'https://www.post-gazette.com/rss', 'This feed contains all stories', 'rss', 'en', 'Pensilvânia (EUA)'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Mundo', 'Spotlight PA', 'https://www.spotlightpa.org/feeds/full.xml', 'Independent, nonprofit, and free news covering statewide issues in Pennsylvania. High quality reporting focused on…', 'rss', 'en', 'Pensilvânia (EUA)'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'WHYY', 'https://whyy.org/feed/', 'WHYY serves the community by contributing to the quality of life through education, information, entertainment and…', 'rss', 'en', 'Pensilvânia (EUA)'),
    -- via RSS do site: 33 entradas, última em 07/10/2026
    ('Mundo', 'BBC News', 'https://feeds.bbci.co.uk/news/rss.xml', 'BBC News - News Front Page', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 22 entradas, última em 07/10/2026
    ('Mundo', 'BBC News – World', 'https://feeds.bbci.co.uk/news/world/rss.xml', 'BBC News - World', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 178 entradas, última em 07/10/2026
    ('Mundo', 'Daily Mail', 'https://www.dailymail.com/articles.rss', 'Daily Mail Online - get the latest breaking news, showbiz & celebrity photos, sport news & rumours, viral videos and…', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Mundo', 'Daily Mirror', 'https://www.mirror.co.uk/news/?service=rss', 'RSS feed from Mirror', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Mundo', 'Evening Standard', 'https://www.standard.co.uk/rss', 'Visit now for the latest news direct from The Standard and updated throughout the day', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'New Statesman', 'https://www.newstatesman.com/feed', 'New Times, New Ideas, New Statesman', 'rss', 'en', 'Reino Unido'),
    -- via Google Notícias: 98 entradas, última em 07/10/2026
    ('Mundo', 'Prospect', 'https://news.google.com/rss/search?q=site%3Aprospectmagazine.co.uk&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 9 entradas, última em 07/10/2026
    ('Mundo', 'Sky News', 'https://feeds.skynews.com/feeds/rss/home.xml', 'Sky news delivers breaking news, headlines and top stories from business, politics, entertainment and more in the UK…', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 300 entradas, última em 07/10/2026
    ('Mundo', 'The Economist', 'https://www.economist.com/latest/rss.xml', 'The most recent blogs and online articles from The Economist', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 112 entradas, última em 07/10/2026
    ('Mundo', 'The Guardian', 'https://www.theguardian.com/international/rss', 'Latest international news, sport and comment from the Guardian', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'The i Paper', 'https://inews.co.uk/feed', 'Impartial news & intelligent debate', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Mundo', 'The Independent', 'https://www.independent.co.uk/news/rss', 'Visit now for the latest news direct from The Independent News and updated throughout the day', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Mundo', 'The Sun', 'https://www.thesun.co.uk/feed/', 'The Best for News, Sport, Showbiz, Celebrities', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 120 entradas, última em 07/10/2026
    ('Mundo', 'The Telegraph', 'https://www.telegraph.co.uk/rss.xml', 'www.telegraph.co.uk for the latest news from the UK and around the world.', 'rss', 'en', 'Reino Unido'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'The Times', 'https://www.thetimes.com/sitemaps/news', null, 'sitemap', 'en', 'Reino Unido'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Mundo', 'UnHerd', 'https://unherd.com/feed/', 'think again', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Mundo', 'Meduza', 'https://meduza.io/rss/en/all', 'Every day we bring you the most important news and feature stories from hundreds of sources in Russia and across the…', 'rss', 'en', 'Rússia'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Mundo', 'The Moscow Times', 'https://www.themoscowtimes.com/rss/news', 'The Moscow Times offers everything you need to know about Russia: Breaking news, top stories, business, analysis,…', 'rss', 'en', 'Rússia'),
    -- via RSS do site: 35 entradas, última em 07/10/2026
    ('Mundo', 'The Seattle Times', 'https://www.seattletimes.com/feed/', 'Local news, sports, business, politics, entertainment, travel, restaurants and opinion for Seattle and the Pacific…', 'rss', 'en', 'Seattle (EUA)'),
    -- via sitemap de notícias: 30 entradas, última em 08/10/2026
    ('Mundo', 'CNA', 'https://www.channelnewsasia.com/api/v1/sitemap-news-feed?_format=xml', null, 'sitemap', 'en', 'Singapura'),
    -- via sitemap de notícias: 30 entradas, última em 08/10/2026
    ('Mundo', 'The Straits Times', 'https://www.straitstimes.com/googlenews.xml', null, 'sitemap', 'en', 'Singapura'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Mundo', 'KQED', 'https://ww2.kqed.org/news/feed/', 'KQED Public Media for Northern CA', 'rss', 'en', 'São Francisco (EUA)'),
    -- via RSS do site: 31 entradas, última em 07/10/2026
    ('Mundo', 'Mission Local', 'https://missionlocal.org/feed/', 'Local news for a global city', 'rss', 'en', 'São Francisco (EUA)'),
    -- via sitemap de notícias: 30 entradas, última em 30/09/2026
    ('Mundo', 'San Francisco Chronicle', 'https://www.sfchronicle.com/sitemap_news.xml', null, 'sitemap', 'en', 'São Francisco (EUA)'),
    -- via sitemap de notícias: 30 entradas, última em 30/09/2026
    ('Mundo', 'SFGATE', 'https://www.sfgate.com/sitemap_news.xml', null, 'sitemap', 'en', 'São Francisco (EUA)'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'The San Francisco Standard', 'https://sfstandard.com/feed/', 'The San Francisco Bay Area''s essential source for daily news, politics, business, food, tech, culture and more', 'rss', 'en', 'São Francisco (EUA)'),
    -- via sitemap de notícias: 30 entradas, última em 08/10/2026
    ('Mundo', 'Bangkok Post', 'https://www.bangkokpost.com/sitemap_news.xml', null, 'sitemap', 'en', 'Tailândia'),
    -- via sitemap de notícias: 30 entradas, última em 01/10/2026
    ('Mundo', 'Houston Chronicle', 'https://www.houstonchronicle.com/sitemap_news.xml', null, 'sitemap', 'en', 'Texas (EUA)'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Mundo', 'Houston Public Media', 'https://www.houstonpublicmedia.org/rsslatest.xml', 'Houston Public Media is a non-profit organization broadcasting through a multi-media platform to deliver content with…', 'rss', 'en', 'Texas (EUA)'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Mundo', 'Texas Monthly', 'https://www.texasmonthly.com/feed/', 'Covering Texas news, politics, food, history, crime, music, and everything in between for more than fifty years.', 'rss', 'en', 'Texas (EUA)'),
    -- via sitemap de notícias: 30 entradas, última em 01/10/2026
    ('Mundo', 'The Dallas Morning News', 'https://www.dallasnews.com/news-sitemap.xml', null, 'sitemap', 'en', 'Texas (EUA)'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Mundo', 'Anadolu Agency', 'https://www.aa.com.tr/tr/rss/default?cat=guncel', 'Türkiye''den ve Dünya''dan Güncel Haberler', 'rss', 'en', 'Turquia'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Mundo', 'Kyiv Post', 'https://www.kyivpost.com/feed', 'Kyiv Post Delivers Exclusive and In-Depth News and Opinions on Politics, Economics – Get Your Daily News Brief Direct…', 'rss', 'en', 'Ucrânia'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Mundo', 'VTDigger', 'https://vtdigger.org/feed/', 'News in pursuit of truth', 'rss', 'en', 'Vermont (EUA)'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'Washington City Paper', 'https://washingtoncitypaper.com/feed/?partner-feed=public', null, 'rss', 'en', 'Washington (EUA)'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'WTOP', 'https://wtop.com/feed/', 'News Happens Here', 'rss', 'en', 'Washington (EUA)'),
    -- via Google Notícias: 100 entradas, última em 01/10/2026
    ('Mundo', 'Africa Check', 'https://news.google.com/rss/search?q=site%3Aafricacheck.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'África'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'African Arguments', 'https://africanarguments.org/feed/', 'African Arguments', 'rss', 'en', 'África'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Mundo', 'The Africa Report', 'https://www.theafricareport.com/feed/', 'The Africa Report brings you expert analysis, opinion and breaking news on African politics, business, and society.', 'rss', 'en', 'África'),
    -- via RSS do site: 51 entradas, última em 08/10/2026
    ('Mundo', 'Daily Maverick', 'https://www.dailymaverick.co.za/dmrss/', 'Latest news and analysis from Daily Maverick', 'rss', 'en', 'África do Sul'),
    -- via Google Notícias: 99 entradas, última em 07/10/2026
    ('Mundo', 'News24', 'https://news.google.com/rss/search?q=site%3Anews24.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'África do Sul'),
    -- via RSS do site: 96 entradas, última em 07/10/2026
    ('Mundo', 'The Diplomat', 'https://thediplomat.com/feed/', 'The Diplomat is a current-affairs magazine for the Asia-Pacific, with news and analysis on politics, security,…', 'rss', 'en', 'Ásia'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Mundo', 'Firstpost', 'https://news.google.com/rss/search?q=site%3Afirstpost.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Índia'),
    -- via sitemap de notícias: 30 entradas, última em 08/10/2026
    ('Mundo', 'Hindustan Times', 'https://www.hindustantimes.com/sitemap/news.xml', null, 'sitemap', 'en', 'Índia'),
    -- via RSS do site: 132 entradas, última em 07/10/2026
    ('Mundo', 'India Today', 'https://www.indiatoday.in/rss/home', 'India Today', 'rss', 'en', 'Índia'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'NDTV', 'https://feeds.feedburner.com/ndtvnews-top-stories', 'NDTV.com provides the latest information from and in-depth coverage of India and the world. Find breaking news, India…', 'rss', 'en', 'Índia'),
    -- via RSS do site: 100 entradas, última em 07/10/2026
    ('Mundo', 'Scroll.in', 'https://feeds.feedburner.com/ScrollinArticles.rss', 'A digital daily of things that matter.', 'rss', 'en', 'Índia'),
    -- via RSS do site: 60 entradas, última em 07/10/2026
    ('Mundo', 'The Hindu', 'https://www.thehindu.com/news/feeder/default.rss', 'News Today: Get breaking news, top headlines, and live updates from India and around the world across politics,…', 'rss', 'en', 'Índia'),
    -- via RSS do site: 200 entradas, última em 07/10/2026
    ('Mundo', 'The Indian Express', 'https://indianexpress.com/feed/', 'Latest News Today, Breaking News, India News, Top Headlines', 'rss', 'en', 'Índia'),
    -- via sitemap de notícias: 30 entradas, última em 08/10/2026
    ('Mundo', 'The Wire', 'https://thewire.in/news-sitemap.xml', null, 'sitemap', 'en', 'Índia'),
    -- via RSS do site: 44 entradas, última em 07/10/2026
    ('Mundo', 'Times of India', 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms', 'The Times of India: Breaking news, views, reviews, cricket from across India', 'rss', 'en', 'Índia'),
    -- via Google Notícias: 96 entradas, última em 07/10/2026
    ('Outros', 'Ad Age', 'https://news.google.com/rss/search?q=site%3Aadage.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Outros', 'Adweek', 'https://www.adweek.com/feed/', 'Breaking News in Advertising, Media and Technology', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 06/10/2026
    ('Outros', 'Behavioral Scientist', 'https://behavioralscientist.org/feed/', 'Original, thought-provoking reports from the front lines of behavioral science.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Outros', 'Columbia Journalism Review', 'https://www.cjr.org/feed', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 15 entradas, última em 07/10/2026
    ('Outros', 'Digiday', 'https://digiday.com/feed/', 'Digital Content, Digital Advertising, Digital Marketing', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 01/10/2026
    ('Outros', 'Farnam Street', 'https://fs.blog/feed/', 'Mastering the best of what other people have already figured out', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Outros', 'HR Dive', 'https://www.hrdive.com/feeds/news/', 'Human Resources and Workforce Management News', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Outros', 'JSTOR Daily', 'https://daily.jstor.org/feed/', 'from JSTOR, nonprofit library for the intellectually curious', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Outros', 'Literary Hub', 'https://lithub.com/feed/', 'The best of the literary web', 'rss', 'en', 'EUA'),
    -- via RSS do site: 25 entradas, última em 07/10/2026
    ('Outros', 'Longreads', 'https://longreads.com/feed/', 'Longreads : The best longform stories on the web', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Outros', 'Mediaite', 'https://www.mediaite.com/feed/', 'Mediaite.com | News & Opinion', 'rss', 'en', 'EUA'),
    -- via RSS do site: 30 entradas, última em 07/10/2026
    ('Outros', 'Nieman Journalism Lab', 'https://www.niemanlab.org/feed/', null, 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Outros', 'Poynter', 'https://www.poynter.org/feed/', 'A global leader in journalism. Strengthening democracy.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 50 entradas, última em 07/10/2026
    ('Outros', 'The New Yorker', 'https://www.newyorker.com/feed/everything', 'Channel Description', 'rss', 'en', 'EUA'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Outros', 'The Paris Review', 'https://www.theparisreview.org/blog/feed/', 'The best prose, interviews, poetry, and art. Since 1953.', 'rss', 'en', 'EUA'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Outros', 'Aeon', 'https://aeon.co/feed.rss', 'Aeon is a magazine of ideas and culture. We publish in-depth essays from the world’s most incisive and ambitious…', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Outros', 'Psyche', 'https://psyche.co/feed.rss', 'Psyche is a magazine to help you understand your self and live well. Discover articles and videos on emotions, mental…', 'rss', 'en', 'Internacional'),
    -- via RSS do site: 10 entradas, última em 07/10/2026
    ('Outros', 'Press Gazette', 'https://pressgazette.co.uk/feed/', 'The Future of Media', 'rss', 'en', 'Reino Unido'),
    -- via RSS do site: 10 entradas, última em 07/09/2026
    ('Outros', 'Reuters Institute', 'https://reutersinstitute.politics.ox.ac.uk/rss.xml', null, 'rss', 'en', 'Reino Unido'),
    -- segunda passada (o plano B usava o caminho do feed na busca do Google Notícias; corrigido)
    -- via Google Notícias: 91 entradas, última em 29/09/2026
    ('Política', 'MuckRock', 'https://news.google.com/rss/search?q=site%3Amuckrock.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Política', 'Reveal', 'https://news.google.com/rss/search?q=site%3Arevealnews.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 75 entradas, última em 07/10/2026
    ('Finanças', 'Bureau of Labor Statistics', 'https://news.google.com/rss/search?q=site%3Abls.gov&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 73 entradas, última em 05/10/2026
    ('Finanças', 'Economic Policy Institute', 'https://news.google.com/rss/search?q=site%3Aepi.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 63 entradas, última em 07/10/2026
    ('Finanças', 'Nasdaq', 'https://news.google.com/rss/search?q=site%3Anasdaq.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 98 entradas, última em 07/10/2026
    ('Finanças', 'Seeking Alpha', 'https://news.google.com/rss/search?q=site%3Aseekingalpha.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 83 entradas, última em 07/10/2026
    ('Tecnologia', 'Cult of Mac', 'https://news.google.com/rss/search?q=site%3Acultofmac.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Tecnologia', 'DevOps.com', 'https://news.google.com/rss/search?q=site%3Adevops.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Tecnologia', 'Digital Trends', 'https://www.digitaltrends.com/sitemap-google-news-sitemap_1.xml', null, 'sitemap', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 01/10/2026
    ('Tecnologia', 'Microsoft AI Blog', 'https://news.google.com/rss/search?q=site%3Ablogs.microsoft.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 80 entradas, última em 07/10/2026
    ('Tecnologia', 'PCMag', 'https://news.google.com/rss/search?q=site%3Apcmag.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 95 entradas, última em 30/07/2024
    ('Tecnologia', 'StrictlyVC', 'https://news.google.com/rss/search?q=site%3Astrictlyvc.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 91 entradas, última em 07/10/2026
    ('Tecnologia', 'Tom''s Guide', 'https://news.google.com/rss/search?q=site%3Atomsguide.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Tecnologia', 'VentureBeat', 'https://news.google.com/rss/search?q=site%3Aventurebeat.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 27 entradas, última em 07/10/2026
    ('Tecnologia', 'Windows Central', 'https://www.windowscentral.com/sitemap-news.xml', null, 'sitemap', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 06/10/2026
    ('Tecnologia', 'AI News', 'https://news.google.com/rss/search?q=site%3Aartificialintelligence-news.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Reino Unido'),
    -- via Google Notícias: 99 entradas, última em 07/10/2026
    ('Tecnologia', 'GeekWire', 'https://news.google.com/rss/search?q=site%3Ageekwire.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Seattle (EUA)'),
    -- via Google Notícias: 24 entradas, última em 06/10/2026
    ('Ciência', 'NASA JPL', 'https://news.google.com/rss/search?q=site%3Ajpl.nasa.gov&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 98 entradas, última em 07/10/2026
    ('Ciência', 'Science', 'https://news.google.com/rss/search?q=site%3Ascience.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Ciência', 'Sky & Telescope', 'https://news.google.com/rss/search?q=site%3Askyandtelescope.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 28 entradas, última em 07/10/2026
    ('Ciência', 'Space.com', 'https://www.space.com/sitemap-news.xml', null, 'sitemap', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Ciência', 'Physics World', 'https://news.google.com/rss/search?q=site%3Aphysicsworld.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Reino Unido'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Meio ambiente', 'CleanTechnica', 'https://news.google.com/rss/search?q=site%3Acleantechnica.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Meio ambiente', 'Inside Climate News', 'https://news.google.com/rss/search?q=site%3Ainsideclimatenews.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 96 entradas, última em 02/10/2026
    ('Saúde', 'Harvard Health', 'https://news.google.com/rss/search?q=site%3Ahealth.harvard.edu&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 30/09/2026
    ('Saúde', 'Mayo Clinic News Network', 'https://news.google.com/rss/search?q=site%3Anewsnetwork.mayoclinic.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 79 entradas, última em 07/10/2026
    ('Saúde', 'Organização Mundial da Saúde', 'https://news.google.com/rss/search?q=site%3Awho.int&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Internacional'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Esportes', 'HoopsHype', 'https://www.hoopshype.com/news-sitemap.xml', null, 'sitemap', 'en', 'EUA'),
    -- via sitemap de notícias: 18 entradas, última em 07/10/2026
    ('Esportes', 'SB Nation', 'https://www.sbnation.com/sitemaps/google_news', null, 'sitemap', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Esportes', 'PlanetF1', 'https://news.google.com/rss/search?q=site%3Aplanetf1.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Reino Unido'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Entretenimento', 'RogerEbert.com', 'https://news.google.com/rss/search?q=site%3Arogerebert.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Entretenimento', 'Vulture', 'https://www.vulture.com/_news.xml', null, 'sitemap', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Automóveis', 'Autoblog', 'https://news.google.com/rss/search?q=site%3Aautoblog.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Automóveis', 'Electrek', 'https://electrek.co/news-sitemap.xml', null, 'sitemap', 'en', 'EUA'),
    -- via sitemap de notícias: 12 entradas, última em 07/10/2026
    ('Automóveis', 'MotorTrend', 'https://www.motortrend.com/sitemap_google_news.xml', null, 'sitemap', 'en', 'EUA'),
    -- via Google Notícias: 96 entradas, última em 07/10/2026
    ('Automóveis', 'Autocar', 'https://news.google.com/rss/search?q=site%3Aautocar.co.uk&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Reino Unido'),
    -- via Google Notícias: 100 entradas, última em 05/10/2026
    ('Mundo', 'Arizona Mirror', 'https://news.google.com/rss/search?q=site%3Aazmirror.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Arizona (EUA)'),
    -- via Google Notícias: 97 entradas, última em 07/10/2026
    ('Mundo', 'Orange County Register', 'https://news.google.com/rss/search?q=site%3Aocregister.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Califórnia (EUA)'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'The Mercury News', 'https://www.mercurynews.com/sitemap.xml', null, 'sitemap', 'en', 'Califórnia (EUA)'),
    -- via Google Notícias: 75 entradas, última em 07/10/2026
    ('Mundo', 'CBC News', 'https://news.google.com/rss/search?q=site%3Acbc.ca&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Canadá'),
    -- via Google Notícias: 98 entradas, última em 07/10/2026
    ('Mundo', 'Maclean''s', 'https://news.google.com/rss/search?q=site%3Amacleans.ca&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Canadá'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'Montreal Gazette', 'https://montrealgazette.com/news-sitemap.xml', null, 'sitemap', 'en', 'Canadá'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Mundo', 'The Denver Post', 'https://news.google.com/rss/search?q=site%3Adenverpost.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Colorado (EUA)'),
    -- via Google Notícias: 94 entradas, última em 06/10/2026
    ('Mundo', 'Brookings', 'https://news.google.com/rss/search?q=site%3Abrookings.edu&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'HuffPost', 'https://www.huffpost.com/static-assets/isolated/huffpostsitemapgeneratorjob-prod-public/us/sitemaps/sitemap-google-news.xml', null, 'sitemap', 'en', 'EUA'),
    -- via Google Notícias: 99 entradas, última em 07/10/2026
    ('Mundo', 'War on the Rocks', 'https://news.google.com/rss/search?q=site%3Awarontherocks.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Mundo', 'Florida Phoenix', 'https://news.google.com/rss/search?q=site%3Afloridaphoenix.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Flórida (EUA)'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Mundo', 'Florida Politics', 'https://news.google.com/rss/search?q=site%3Afloridapolitics.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Flórida (EUA)'),
    -- via sitemap de notícias: 30 entradas, última em 08/10/2026
    ('Mundo', 'The Times of Israel', 'https://www.timesofisrael.com/news-sitemap.xml', null, 'sitemap', 'en', 'Israel'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'Los Angeles Daily News', 'https://www.dailynews.com/sitemap.xml', null, 'sitemap', 'en', 'Los Angeles (EUA)'),
    -- via Google Notícias: 99 entradas, última em 07/10/2026
    ('Mundo', 'Mississippi Today', 'https://news.google.com/rss/search?q=site%3Amississippitoday.org&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Mississippi (EUA)'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'The Spectator', 'https://www.spectator.co.uk/news-sitemap.xml', null, 'sitemap', 'en', 'Reino Unido'),
    -- via RSS do site: 20 entradas, última em 07/10/2026
    ('Mundo', 'The Texas Tribune', 'https://feeds.texastribune.org/feeds/main/', 'Independent news. Trusted by Texans.', 'rss', 'en', 'Texas (EUA)'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'The Kyiv Independent', 'https://kyivindependent.com/news-sitemap.xml', null, 'sitemap', 'en', 'Ucrânia'),
    -- via Google Notícias: 100 entradas, última em 07/10/2026
    ('Mundo', 'The Washington Times', 'https://news.google.com/rss/search?q=site%3Awashingtontimes.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'Washington (EUA)'),
    -- via sitemap de notícias: 26 entradas, última em 07/10/2026
    ('Mundo', 'Mail & Guardian', 'https://mg.co.za/sitemap-news.xml', null, 'sitemap', 'en', 'África do Sul'),
    -- via sitemap de notícias: 30 entradas, última em 08/10/2026
    ('Mundo', 'ThePrint', 'https://theprint.in/googlenews.xml', null, 'sitemap', 'en', 'Índia'),
    -- via Google Notícias: 99 entradas, última em 01/10/2026
    ('Outros', 'The New York Review of Books', 'https://news.google.com/rss/search?q=site%3Anybooks.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA'),
    -- WSJ e Yahoo Finance pelo site (os feeds antigos pararam)
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Finanças', 'Yahoo Finance', 'https://finance.yahoo.com/news-sitemap.xml', null, 'sitemap', 'en', 'EUA'),
    -- via sitemap de notícias: 30 entradas, última em 07/10/2026
    ('Mundo', 'The Wall Street Journal', 'https://www.wsj.com/wsjsitemaps/wsj_google_news.xml', null, 'sitemap', 'en', 'EUA'),
    -- CNN pelo Google Notícias (o feed que o site anuncia está malformado): 86 entradas
    ('Mundo', 'CNN', 'https://news.google.com/rss/search?q=site%3Acnn.com&hl=en-US&gl=US&ceid=US:en', 'Via Google Notícias', 'rss', 'en', 'EUA')
on conflict (url) do nothing;
