"""
Catálogo de temas do Daily Paper: o que dá pra seguir e buscar além das
fontes. Três níveis convivem numa notícia (ela pode ter vários temas):
  - tema amplo: a própria categoria ("Games", "Cinema", "Política"), que
    vem da classificação (classificar.py);
  - tema específico: "Filmes", "Séries", "Fofoca", "Quadrinhos",
    "Inteligência artificial"... reconhecido pelos termos abaixo;
  - nomes (pessoas, times, franquias, empresas): não ficam aqui, vêm do
    spaCy (entidades.py) e também dá pra seguir.

Cada tema tem:
  - grupo: o assunto maior, pra organizar a lista no hub (Seguir > Temas);
  - sinonimos: o que as pessoas digitam pra achar o tema na busca ("hq",
    "comics" -> Quadrinhos; "famosos" -> Fofoca). O singular e o plural
    já valem sozinhos (sinais.radical);
  - termos: o que denuncia o tema numa notícia, com peso de 1 (indício) a
    3 (quase certo). Escritos no singular e sem acento: o plural casa
    pelo radical. No título valem 3x; no começo do texto, 1,5x. Precisa
    somar MINIMO pra notícia ganhar o tema. A frase mais longa ganha
    ("star wars" não conta como "war"); peso 0 é frase que só serve pra
    tirar um falso positivo ("escola de samba" não é Educação).

Pra crescer: um tema novo é uma linha aqui; um sinônimo novo, uma palavra
na lista. As buscas sem resultado (Relatórios) dizem o que está faltando.
O classificar.py copia o catálogo pro banco (tabela catalogo_temas,
sql/047) a cada rodada, pro hub usar na busca.
"""
import re
from collections import Counter

from sinais import normalizar, radical

MINIMO = 4
# Tema de assunto que não combina com a categoria da notícia vale metade:
# só entra com sinal forte e explícito ("filme" no título de uma notícia
# de games entra; "temporada" numa de Fórmula 1, não)
PESO_FORA_DO_ASSUNTO = 0.5
PESO_TITULO = 3
PESO_TEXTO = 1.5
CARACTERES_DO_TEXTO = 800
MAX_TEMAS = 4

GRUPOS = [
    "Entretenimento", "Cinema e séries", "Cultura geek", "Games", "Tecnologia", "Economia e negócios",
    "Esportes", "Política", "Mundo", "Saúde", "Ciência e meio ambiente", "Estilo de vida",
]

# Categorias de notícia em que os temas de cada grupo fazem sentido (sem
# entrada: qualquer uma). "Desabafa após polêmica" é Fofoca numa notícia
# de Entretenimento, não numa de Esportes.
CATEGORIAS_DO_GRUPO = {
    "Entretenimento": {"Entretenimento", "Cinema", "Humor", "Outros"},
    "Cinema e séries": {"Cinema", "Entretenimento", "Humor", "Outros"},
    "Cultura geek": {"Cinema", "Entretenimento", "Games", "Tecnologia", "Humor", "Outros"},
    "Games": {"Games", "Tecnologia", "Entretenimento", "Outros"},
    "Esportes": {"Esportes", "Outros"},
    "Estilo de vida": {"Entretenimento", "Outros", "Saúde", "Finanças", "Mundo", "Tecnologia", "Ciência", "Humor"},
}

# Categoria da notícia (classificar.py) -> tema amplo
DA_CATEGORIA = {
    "Política": "Política", "Mundo": "Mundo", "Finanças": "Finanças", "Tecnologia": "Tecnologia",
    "Games": "Games", "Cinema": "Cinema", "Entretenimento": "Entretenimento", "Esportes": "Esportes",
    "Saúde": "Saúde", "Ciência": "Ciência", "Humor": "Humor",
}


def _tema(nome, grupo, sinonimos="", termos="", categorias=None):
    pesos = {}
    for item in termos.split(","):
        item = item.strip()
        if not item:
            continue
        termo, _, peso = item.partition(":")
        pesos[normalizar(termo)] = int(peso or 2)
    return {
        "nome": nome,
        "grupo": grupo,
        "sinonimos": [s.strip() for s in sinonimos.split(",") if s.strip()],
        "termos": pesos,
        # só nessas categorias de notícia, e nunca fora delas (sem: as do
        # grupo, onde fora vale metade)
        "categorias": set(categorias) if categorias else None,
    }


TEMAS = [
    # ---------------------------------------------------------------- Entretenimento
    _tema("Entretenimento", "Entretenimento", "entretenimento, famosos, cultura pop"),
    _tema("Celebridades", "Entretenimento", "celebridade, famosos, famosas, artistas, celebs",
          "celebridade:3, celebrity:3, famoso:2, famosa:2, influenciador:2, influenciadora:2, influencer:2, "
          "socialite:3, paparazzi:3, kardashian:3, ex bbb:2, herdeira:1, apresentadora:1, apresentador:1"),
    _tema("Fofoca", "Entretenimento", "fofocas, gossip, babado, polêmicas de famosos, vida de famosos, famosos",
          "fofoca:3, gossip:3, affair:3, climao:3, barraco:3, traicao:2, traiu:2, separacao:2, divorcio:2, "
          "termina namoro:3, terminam namoro:3, reata:3, reatam:3, flagra:2, flagrado:2, flagrada:2, indireta:3, "
          "alfineta:3, alfinetada:3, treta:3, shade:2, rompimento:2, ex marido:1, ex mulher:1, ex namorado:1, "
          "ex namorada:1, namorado:1, namorada:1, beijo:1, polemica:1, detona:1, desabafa:1, crush:2",
          categorias={"Entretenimento", "Humor"}),
    _tema("Música", "Entretenimento", "musica, músicas, cantores, shows, discos, álbuns, music",
          "cantor:2, cantora:2, musica:2, album:2, turne:2, banda:2, clipe:2, single:1, spotify:2, sertanejo:3, "
          "funk:2, pagode:3, samba:2, axe:2, rock:2, rapper:2, rap:2, mpb:3, lollapalooza:3, rock in rio:3, "
          "the town:2, concert:2, singer:2, billboard:3, hot 100:3, dj:2, show:1, festival de musica:3, "
          "parada musical:3, musical:1"),
    _tema("TV e novelas", "Entretenimento", "tv, televisão, novela, novelas, programas de tv",
          "novela:3, telenovela:3, capitulo:2, resumo da novela:3, tv globo:2, globo:1, sbt:2, record:1, "
          "audiencia:2, ibope:3, programa:1, domingao:3, fantastico:2, mais voce:3, faustao:3, luciano huck:2, "
          "ana maria braga:2, horario nobre:3, emissora:2"),
    _tema("Reality shows", "Entretenimento", "reality, realities, bbb, big brother, a fazenda",
          "reality:3, reality show:3, bbb:3, big brother:3, a fazenda:3, masterchef:3, the voice:3, "
          "casamento as cegas:3, love is blind:3, survivor:2, paredao:3, eliminacao:2, eliminado:1, peao:2, "
          "peoa:3, prova de fogo:2, de ferias com o ex:3, ilha da tentacao:3, power couple:3, estrela da casa:3"),
    _tema("K-pop", "Entretenimento", "kpop, k pop, música coreana, idols",
          "kpop:3, k pop:3, bts:3, blackpink:3, stray kids:3, newjeans:3, seventeen:2, twice:1, hybe:3, "
          "idol:2, comeback:1, coreano:1"),
    _tema("Livros", "Entretenimento", "livro, literatura, leitura, escritores, books",
          "livro:2, escritor:2, escritora:2, autor:1, autora:1, literatura:3, editora:1, best seller:3, "
          "bestseller:3, bienal do livro:3, flip:1, jabuti:2, booktok:3, kindle:2, romance policial:3, "
          "lancamento do livro:3, saga:1, novel:1, poesia:2, poeta:2"),
    _tema("Humor", "Entretenimento", "humor, comédia, memes, piadas, stand up",
          "humor:2, comedia:2, comediante:3, stand up:3, meme:2, piada:2, humorista:3, esquete:2"),

    # ---------------------------------------------------------------- Cinema e séries
    _tema("Cinema", "Cinema e séries", "cinema, audiovisual, cinema e séries"),
    _tema("Filmes", "Cinema e séries", "filme, cinema, movies, longas, longa-metragem",
          "filme:3, longa metragem:3, bilheteria:3, box office:3, movie:2, film:1, sequel:2, prequel:2, "
          "nos cinemas:3, estreia nos cinemas:3, in theaters:3, filmagem:2, hollywood:2, diretor:1, diretora:1, "
          "roteiro:1, remake:1, sequencia:1, longa:1, cinebiografia:3, biopic:3, elenco:1, trailer:1"),
    _tema("Séries", "Cinema e séries", "série, seriado, seriados, séries de tv, tv shows, doramas",
          "serie:2, serie de:0, serie de tv:3, uma serie:0, seriado:3, temporada:1, episodio:1, episode:2, season:1, showrunner:3, spin off:2, "
          "minisserie:3, sitcom:3, renovada para:3, renovada:1, cancelada:1, dorama:3, k drama:3, kdrama:3, "
          "final de temporada:3, nova temporada:3, tv show:3"),
    _tema("Streaming", "Cinema e séries", "streamings, plataformas de streaming, netflix, prime video",
          "streaming:3, netflix:3, hbo max:3, prime video:3, disney:2, apple tv:3, globoplay:3, paramount:2, "
          "crunchyroll:2, max:1, catalogo:1, assinantes:2, assinatura:1"),
    _tema("Premiações", "Cinema e séries", "premiação, prêmios, oscar, emmy, globo de ouro, awards",
          "oscar:3, emmy:3, globo de ouro:3, golden globe:3, grammy:3, festival de cannes:3, cannes:2, bafta:3, "
          "sag award:3, indicado:1, indicacao:1, premiacao:3, tapete vermelho:2, red carpet:2, vencedor:1, "
          "the game awards:2, premio:1"),
    _tema("Animação", "Cinema e séries", "animações, desenho animado, desenhos, animated",
          "animacao:3, animado:1, animated:2, pixar:3, dreamworks:3, cartoon:2, desenho animado:3, "
          "stop motion:3, ghibli:2, disney animation:3"),
    _tema("Super-heróis", "Cinema e séries", "super-herói, super herois, heróis, marvel, dc, mcu",
          "super heroi:3, superheroi:3, superhero:3, marvel:3, mcu:3, dcu:3, dc studio:3, dc comics:3, vingadores:3, "
          "avengers:3, homem aranha:3, spider man:3, batman:3, superman:3, mulher maravilha:3, wonder woman:3, "
          "x men:3, deadpool:3, wolverine:2, capitao america:3, quarteto fantastico:3, fantastic four:3, "
          "liga da justica:3, coringa:2, thor:2, hulk:2, homem de ferro:3, iron man:3, pantera negra:3"),
    _tema("Terror", "Cinema e séries", "horror, filmes de terror, suspense, terror e suspense",
          "terror:1, filme de terror:3, serie de terror:3, horror:2, slasher:3, assombracao:3, possessao:2, invocacao do mal:3, stephen king:2, "
          "jogos mortais:3, evil dead:3, zumbi:2, zombie:2, sobrenatural:2, blumhouse:3, a24:2, sexta feira 13:3, "
          "exorcista:3, halloween:1, suspense:1"),
    _tema("Documentários", "Cinema e séries", "documentário, docs, true crime, docuseries",
          "documentario:3, documentary:3, docuserie:3, true crime:3, serie documental:3"),

    # ---------------------------------------------------------------- Cultura geek
    _tema("Cultura geek", "Cultura geek", "geek, nerd, cultura nerd, cultura pop, nerdices",
          "nerd:2, geek:3, ccxp:3, comic con:3, cosplay:3, cultura pop:2, star wars:3, star trek:3, "
          "senhor dos aneis:3, lord of the rings:3, harry potter:3, game of thrones:3, house of the dragon:3, "
          "jovem nerd:3, nerdcast:3, colecionavel:2, action figure:3, funko:3, lego:2, sci fi:2, "
          "ficcao cientifica:2, doctor who:3, warhammer:3, tolkien:3, fandom:2"),
    _tema("Quadrinhos", "Cultura geek", "hq, hqs, comics, gibi, gibis, graphic novel, histórias em quadrinhos",
          "quadrinho:3, hq:1, comics:2, gibi:3, graphic novel:3, turma da monica:3, mauricio de sousa:3, "
          "panini:2, cartunista:3, tirinha:2, webcomic:3, dc comics:3, marvel comics:3, image comics:3, "
          "editora de quadrinhos:3, desenhista:1"),
    _tema("Anime e mangá", "Cultura geek", "anime, animes, mangá, mangás, otaku, animação japonesa",
          "anime:3, manga:1, mangaka:3, otaku:3, crunchyroll:3, one piece:3, naruto:3, dragon ball:3, "
          "demon slayer:3, jujutsu kaisen:3, attack on titan:3, shingeki:3, studio ghibli:3, ghibli:3, "
          "my hero academia:3, chainsaw man:3, solo leveling:3, boruto:3, bleach:3, spy x family:3, "
          "dandadan:3, frieren:3, isekai:3, shonen:3, cosplay:1"),
    _tema("Jogos de tabuleiro", "Cultura geek", "board games, boardgames, rpg de mesa, card games, tcg",
          "jogo de tabuleiro:3, board game:3, boardgame:3, rpg de mesa:3, dungeons dragons:3, card game:2, "
          "magic the gathering:3, tcg:3, pokemon tcg:3, xadrez:1, chess:1"),

    # ---------------------------------------------------------------- Games
    _tema("Games", "Games", "games, jogos, videogame, videogames, gamer, video games"),
    _tema("Consoles", "Games", "console, videogames, playstation, xbox, nintendo",
          "playstation:3, ps5:3, ps4:2, ps6:3, xbox:3, nintendo:2, switch 2:3, nintendo switch:3, console:2, "
          "series x:3, steam deck:3, handheld:2, portatil:1, dualsense:3, rog ally:3"),
    _tema("Jogos de PC", "Games", "pc gamer, jogos para pc, steam",
          "steam:3, epic games store:3, jogos de pc:3, pc gamer:3, placa de video:3, gpu:2, rtx:3, dlss:3, "
          "requisitos minimos:3, mod:2, gog:2, pc:1"),
    _tema("Jogos mobile", "Games", "mobile, jogos de celular, games mobile",
          "jogo mobile:3, jogos mobile:3, mobile game:3, free fire:3, clash royale:3, pokemon go:3, gacha:3, "
          "genshin impact:2, candy crush:3, roblox:2, google play:1, app store:1, mobile:1"),
    _tema("E-sports", "Games", "esports, esportes eletrônicos, competitivo, campeonatos de games",
          "e sports:3, esports:3, cblol:3, league of legends:2, valorant:2, counter strike:2, cs2:2, "
          "mundial de lol:3, worlds:1, pain gaming:3, furia:1, major:1, campeonato de:1, free fire world series:3"),
    _tema("Lançamentos de jogos", "Games", "lançamentos, novos jogos, trailers de games, data de lançamento",
          "data de lancamento:2, release date:2, gameplay:2, state of play:3, nintendo direct:3, "
          "xbox showcase:3, summer game fest:3, the game awards:3, gamescom:3, tokyo game show:3, pre venda:2, "
          "pre order:2, dlc:2, remake:1, remaster:2, early access:3, acesso antecipado:3, demo:1, beta:1"),

    # ---------------------------------------------------------------- Tecnologia
    _tema("Tecnologia", "Tecnologia", "tecnologia, tech, tecnologias"),
    _tema("Inteligência artificial", "Tecnologia", "ia, ai, inteligência artificial, chatgpt, ia generativa",
          "inteligencia artificial:3, artificial intelligence:3, ia:1, ai:1, openai:3, chatgpt:3, gemini:2, "
          "anthropic:3, llm:3, modelo de linguagem:3, ia generativa:3, generative ai:3, copilot:2, deepseek:3, "
          "machine learning:3, aprendizado de maquina:3, chatbot:3, agente de ia:3, midjourney:3, sam altman:3, "
          "grok:2, claude:1"),
    _tema("Celulares", "Tecnologia", "celular, smartphone, smartphones, iphone, android",
          "iphone:3, android:2, smartphone:3, celular:3, galaxy:2, xiaomi:2, motorola:2, pixel:1, redmi:3, "
          "oneplus:3, dobravel:3, foldable:2, poco:1"),
    _tema("Computadores e hardware", "Tecnologia", "computador, pc, notebook, hardware, processadores",
          "notebook:3, laptop:3, computador:2, processador:3, cpu:2, gpu:2, placa de video:3, chip:2, "
          "semicondutor:3, intel:2, amd:2, nvidia:2, memoria ram:3, ssd:3, monitor:1, macbook:3, windows:1, "
          "qualcomm:2, snapdragon:3, tsmc:3, hardware:3"),
    _tema("Segurança digital", "Tecnologia", "cibersegurança, golpes, hackers, privacidade, vazamento",
          "hacker:3, ciberseguranca:3, cybersecurity:3, vazamento de dado:3, golpe digital:3, golpe:1, "
          "phishing:3, ransomware:3, malware:3, ataque hacker:3, ciberataque:3, cyberattack:3, dados pessoais:2, "
          "lgpd:3, privacidade:2, spyware:3, engenharia social:3, fraude:1"),
    _tema("Redes sociais", "Tecnologia", "rede social, instagram, tiktok, twitter, x, youtube",
          "redes sociais:2, rede social:2, nas redes sociais:0, em suas redes sociais:0, pelas redes sociais:0, "
          "nas redes:0, em suas redes:0, instagram:1, tiktok:1, twitter:1, facebook:1, threads:1, bluesky:3, "
          "youtube:1, kwai:1, meta:1, banimento:2, regulacao das redes:3, algoritmo:2, zuckerberg:2, moderacao de conteudo:3, viralizou:2, viraliza:2, viral:1, "
          "influenciador:1, big tech:1"),
    _tema("Apps e software", "Tecnologia", "aplicativos, apps, software, programas, atualizações",
          "aplicativo:2, app:1, software:2, atualizacao:1, update:1, ios:2, whatsapp:2, nova funcao:2, "
          "novo recurso:2, recurso:1, google chrome:3, chrome:2, navegador:2, browser:2, sistema operacional:3, "
          "linux:2, macos:3, windows 11:3"),
    _tema("Startups", "Tecnologia", "startup, empreendedorismo, unicórnios, venture capital",
          "startup:3, unicornio:3, venture capital:3, rodada de investimento:3, aporte:2, fintech:2, "
          "fundador:1, empreendedor:2, empreendedorismo:3, aceleradora:3"),

    # ---------------------------------------------------------------- Economia e negócios
    _tema("Finanças", "Economia e negócios", "economia, finanças, dinheiro, negócios, mercado"),
    _tema("Mercado financeiro", "Economia e negócios", "bolsa, ações, investimentos, ibovespa, dólar",
          "ibovespa:3, b3:3, acao:1, dolar:2, wall street:3, nasdaq:3, dow jones:3, dividendo:3, ipo:3, "
          "bolsa de valores:3, bolsa:1, investidor:2, fundo imobiliario:2, fii:2, renda variavel:3, renda fixa:3, "
          "cdb:2, tesouro direto:3, cotacao:2, mercado financeiro:3, preco alvo:3, investimento:1"),
    _tema("Juros e inflação", "Economia e negócios", "juros, inflação, selic, copom, preços",
          "selic:3, copom:3, juro:3, inflacao:3, ipca:3, fed:2, inflation:3, banco central:2, taxa de juro:3, "
          "interest rate:3, igp m:3, custo de vida:2"),
    _tema("Empresas", "Economia e negócios", "negócios, companhias, corporações, resultados",
          "lucro:2, balanco:2, trimestre:1, resultado do trimestre:3, faturamento:2, earnings:3, fusao:3, aquisicao:2, resultado trimestral:3, "
          "receita liquida:3, demissao:1, layoff:3, recuperacao judicial:3, falencia:3, ceo:1, valor de mercado:2, "
          "market cap:2"),
    _tema("Criptomoedas", "Economia e negócios", "cripto, criptomoeda, bitcoin, crypto, blockchain",
          "bitcoin:3, cripto:3, criptomoeda:3, crypto:3, ethereum:3, blockchain:3, stablecoin:3, solana:2, "
          "binance:3, nft:2, etf de bitcoin:3"),
    _tema("Imóveis", "Economia e negócios", "imóvel, mercado imobiliário, aluguel, casa própria",
          "imovel:3, mercado imobiliario:3, aluguel:2, minha casa minha vida:3, financiamento imobiliario:3, "
          "construtora:2, incorporadora:2, apartamento:1, real estate:3, metro quadrado:2"),
    _tema("Finanças pessoais", "Economia e negócios", "dinheiro, orçamento, dívidas, imposto de renda, aposentadoria",
          "financas pessoais:3, imposto de renda:3, declaracao do ir:3, restituicao:3, decimo terceiro:3, fgts:3, "
          "inss:2, aposentadoria:2, cartao de credito:2, endividamento:2, nome sujo:3, serasa:3, desenrola:3, "
          "poupanca:2, como economizar:3, orcamento familiar:3, salario minimo:2, bolsa familia:2, pix:1"),
    _tema("Empregos", "Economia e negócios", "emprego, vagas, mercado de trabalho, concursos, carreira",
          "emprego:2, desemprego:3, mercado de trabalho:3, vaga:2, concurso publico:3, concurso:2, salario:1, "
          "clt:3, home office:2, trabalho remoto:3, carteira assinada:3, seguro desemprego:3, caged:3, "
          "jovem aprendiz:3, escala 6x1:2, carreira:1"),
    _tema("Varejo e consumo", "Economia e negócios", "consumo, compras, promoções, ofertas, black friday",
          "varejo:3, consumidor:2, black friday:3, promocao:2, desconto:1, shopping:2, e commerce:3, ecommerce:3, "
          "mercado livre:2, shopee:2, amazon:1, shein:2, magalu:2, procon:3, direito do consumidor:3, cupom:2, "
          "supermercado:2, cesta basica:3, oferta:1"),
    _tema("Agronegócio", "Economia e negócios", "agro, agricultura, pecuária, safra",
          "agronegocio:3, agro:2, safra:3, soja:3, milho:2, pecuaria:3, embrapa:3, produtor rural:3, conab:3, "
          "seguro rural:3, colheita:2, plantio:2, agricultura:2, agricultor:2, boi gordo:3"),
    _tema("Impostos", "Economia e negócios", "imposto, tributos, reforma tributária, receita federal",
          "imposto:2, tributaria:3, reforma tributaria:3, receita federal:3, iof:3, icms:3, ipva:2, iptu:3, "
          "tributacao:3, taxacao:3, isencao:2"),

    # ---------------------------------------------------------------- Esportes
    _tema("Esportes", "Esportes", "esportes, esporte, sports"),
    _tema("Futebol", "Esportes", "futebol, futebol brasileiro, brasileirão, soccer",
          "futebol:3, brasileirao:3, seriea:3, serieb:3, seriec:2, libertadores:3, sul americana:3, "
          "copa do brasil:3, copa do mundo:2, champions league:3, premier league:3, la liga:3, gol:1, "
          "selecao brasileira:3, cbf:3, fifa:2, flamengo:2, palmeiras:2, corinthians:2, sao paulo fc:2, vasco:2, "
          "fluminense:2, botafogo:2, gremio:2, cruzeiro:2, atletico mg:2, santos:1, real madrid:2, barcelona:1, "
          "psg:2, manchester city:2, liverpool:1, atacante:2, zagueiro:2, goleiro:2, escalacao:2, artilheiro:3, "
          "rebaixamento:2, onde assistir:1, torcida:2, tecnico:1"),
    _tema("Automobilismo", "Esportes", "fórmula 1, f1, corridas, automobilismo, motogp",
          "f1:3, formula 1:3, grande premio:3, gp:2, stock car:3, formula e:3, nascar:3, indycar:3, motogp:3, "
          "piloto:2, pole position:3, pole:2, projeto piloto:0, verstappen:3, hamilton:2, leclerc:3, norris:2, bortoleto:3, "
          "red bull racing:3, mclaren:3, ferrari:1, autodromo:3, interlagos:3, safety car:3"),
    _tema("Basquete", "Esportes", "basquete, nba, basketball",
          "nba:3, basquete:3, basketball:3, nbb:3, lebron:3, curry:2, laker:3, celtic:3, warrior:3, knick:3, "
          "wembanyama:3, wnba:3, enterrada:2, cesta de tres:3"),
    _tema("Tênis", "Esportes", "tênis, atp, wta, grand slam",
          "tenis:2, tenis de corrida:0, atp:3, wta:3, grand slam:3, roland garros:3, wimbledon:3, us open:2, australian open:3, "
          "joao fonseca:3, djokovic:3, alcaraz:3, sinner:3, haddad maia:3, raquete:2"),
    _tema("Lutas", "Esportes", "mma, ufc, boxe, luta, artes marciais",
          "ufc:3, mma:3, boxe:3, boxing:3, box art:0, box office:0, luta:1, luta contra:0, luta pelo:0, lutador:3, lutadora:3, cinturao:3, nocaute:3, knockout:2, "
          "jiu jitsu:3, judo:2, octogono:3, poatan:3, alex pereira:3, peso pesado:2"),
    _tema("Vôlei", "Esportes", "vôlei, voleibol, volleyball, vôlei de praia",
          "volei:3, voleibol:3, volleyball:3, superliga:3, vnl:3, liga das nacoes:2, volei de praia:3, "
          "levantador:3, levantadora:3, ponteiro:2, ponteira:2, libero:3"),
    _tema("Olimpíadas", "Esportes", "olimpíadas, jogos olímpicos, olympics, paralimpíadas",
          "olimpiada:3, olimpico:2, olimpica:2, olympic:3, jogos olimpicos:3, cob:2, coi:2, paralimpiada:3, "
          "paralimpico:3, medalha de ouro:2, ginastica:2, rebeca andrade:3, atletismo:2, natacao:2, surfe:2, "
          "skate:1"),
    _tema("Futebol americano", "Esportes", "nfl, futebol americano, super bowl",
          "nfl:3, super bowl:3, futebol americano:3, quarterback:3, touchdown:3, chief:2, mahomes:3, "
          "tom brady:3"),

    # ---------------------------------------------------------------- Política
    _tema("Política", "Política", "política, políticos, brasília, governo"),
    _tema("Eleições", "Política", "eleição, eleições, pesquisas eleitorais, candidatos, voto",
          "eleicao:3, segundo turno:1, primeiro turno:1, pesquisa eleitoral:3, quaest:3, datafolha:3, "
          "atlasintel:3, candidato:2, candidata:2, urna:3, debate:1, horario eleitoral:3, propaganda eleitoral:3, "
          "tse:2, intencao de voto:3, voto valido:3, eleitor:2, campanha eleitoral:3, boca de urna:3, apuracao:2, "
          "reeleicao:3"),
    _tema("Legislativo", "Política", "congresso, câmara, senado, deputados, senadores, leis",
          "camara dos deputados:3, senado:2, pec:3, projeto de lei:3, ccj:3, plenario:2, votacao:1, deputado:2, "
          "deputada:2, senador:2, senadora:2, congresso nacional:3, congresso:1, medida provisoria:3, relator:2, "
          "bancada:2, cpmi:3, cpi:2, hugo motta:2, alcolumbre:2"),
    _tema("Judiciário", "Política", "justiça, stf, supremo, tribunais, julgamentos",
          "stf:3, supremo:2, moraes:2, alexandre de moraes:3, pgr:2, stj:3, tribunal:2, juiz:1, juiza:1, "
          "julgamento:2, habeas corpus:3, inquerito:2, condenado:2, condenacao:2, gilmar mendes:3, flavio dino:3, "
          "fachin:3, barroso:3, zanin:3, fux:3, carmen lucia:3, toffoli:3, nunes marques:2, kassio:2"),
    _tema("Governo federal", "Política", "governo, planalto, ministérios, governo lula",
          "governo federal:3, governo lula:3, planalto:2, ministerio:2, ministro:1, ministra:1, esplanada:2, "
          "decreto:2, casa civil:3, presidente lula:3, programa do governo:3"),
    _tema("Segurança pública", "Política", "crime, violência, polícia, segurança",
          "seguranca publica:3, policia:2, policial:2, policia civil:3, policia militar:3, policia federal:2, "
          "crime:2, criminoso:2, assassinato:3, homicidio:3, assalto:3, roubo:2, furto:2, trafico:3, "
          "traficante:3, faccao:3, pcc:3, comando vermelho:3, milicia:3, operacao policial:3, tiroteio:3, "
          "bala perdida:3, sequestro:3, feminicidio:3, violencia:2, preso:2, delegado:2, delegacia:3"),
    _tema("Educação", "Política", "educação, escolas, ensino, enem, universidades",
          "educacao:3, escola:2, escola de samba:0, ensino medio:3, ensino fundamental:3, enem:3, vestibular:3, universidade:2, "
          "faculdade:2, mec:3, aluno:2, professor:2, sisu:3, prouni:3, fies:3, ensino superior:3, "
          "alfabetizacao:3, pe de meia:3, creche:2"),
    _tema("Corrupção", "Política", "corrupção, escândalos, propina, lava jato",
          "corrupcao:3, propina:3, lavagem de dinheiro:3, desvio:2, fraude:2, lava jato:3, delacao:3, "
          "delacao premiada:3, improbidade:3, superfaturamento:3, orcamento secreto:3"),

    # ---------------------------------------------------------------- Mundo
    _tema("Mundo", "Mundo", "mundo, internacional, notícias internacionais, world"),
    _tema("Guerras e conflitos", "Mundo", "guerra, guerras, conflitos, ataques, war",
          "guerra:3, war:1, gaza:3, hamas:3, ucrania:2, ukraine:2, cessar fogo:3, ceasefire:3, bombardeio:3, "
          "missil:3, drone:1, forcas armadas:2, militar:1, exercito:2, hezbollah:3, houthi:3, invasao:2, "
          "conflito armado:3, refem:3, hostage:2"),
    _tema("Estados Unidos", "Mundo", "eua, usa, américa, trump, casa branca",
          "trump:3, casa branca:3, white house:3, estados unidos:2, eua:2, washington:1, donald trump:3, biden:2, "
          "partido republicano:3, partido democrata:3, republicano:2, democrata:2, congresso americano:3, "
          "pentagono:2, tarifaco:3, vance:2"),
    _tema("Oriente Médio", "Mundo", "oriente médio, israel, irã, palestina, middle east",
          "oriente medio:3, middle east:3, israel:2, iran:3, teera:3, tehran:3, netanyahu:3, gaza:2, "
          "cisjordania:3, libano:2, siria:2, arabia saudita:2, catar:2, qatar:2, iemen:2, iraque:2, palestina:2, "
          "palestino:2, jerusalem:2"),
    _tema("Europa", "Mundo", "europa, união europeia, europe",
          "europa:2, uniao europeia:3, european union:3, parlamento europeu:3, comissao europeia:3, franca:2, "
          "macron:3, alemanha:2, merz:3, reino unido:2, starmer:3, italia:2, meloni:3, espanha:2, portugal:2, "
          "polonia:2, bruxela:2, brexit:3, zona do euro:3"),
    _tema("América Latina", "Mundo", "américa latina, américa do sul, latam",
          "america latina:3, argentina:2, milei:3, venezuela:2, maduro:3, colombia:2, gustavo petro:3, chile:2, "
          "boric:3, mexico:2, sheinbaum:3, peru:2, bolivia:2, equador:2, paraguai:2, uruguai:2, cuba:2, "
          "buenos aires:2, mercosul:3, caracas:2"),
    _tema("Ásia", "Mundo", "ásia, china, japão, coreia, índia",
          "china:2, xi jinping:3, pequim:2, beijing:2, japao:2, japan:2, coreia do norte:3, kim jong un:3, "
          "coreia do sul:2, india:2, modi:2, taiwan:2, hong kong:2, toquio:2, filipina:2, vietna:2, indonesia:2, "
          "paquistao:2, asia:2"),
    _tema("Imigração", "Mundo", "imigrantes, migração, refugiados, deportação",
          "imigracao:3, imigrante:3, migrante:3, refugiado:3, deportacao:3, deportado:3, asilo:2, green card:3, "
          "xenofobia:3, crise migratoria:3, fronteira:1"),

    # ---------------------------------------------------------------- Saúde
    _tema("Saúde", "Saúde", "saúde, medicina, bem-estar, health"),
    _tema("Doenças", "Saúde", "doença, doenças, sintomas, tratamentos",
          "cancer:3, tumor:2, diabetes:3, dengue:3, covid:3, virus:2, surto:3, epidemia:3, pandemia:2, "
          "alzheimer:3, parkinson:3, avc:3, infarto:3, hipertensao:3, pressao alta:3, obesidade:2, gripe:2, "
          "influenza:3, sarampo:3, doenca:2, sintoma:2, diagnostico:2, linfoma:3, leucemia:3, chikungunya:3, "
          "zika:3, hiv:3, tuberculose:3, mpox:3, doenca rara:3"),
    _tema("Medicamentos", "Saúde", "remédios, remédio, medicamento, farmácia, canetas emagrecedoras",
          "medicamento:3, remedio:3, anvisa:3, ozempic:3, mounjaro:3, tirzepatida:3, semaglutida:3, "
          "caneta emagrecedora:3, wegovy:3, farmacia:2, farmaceutica:2, generico:2, bula:3, receita medica:3, "
          "antibiotico:3, fda:2, ensaio clinico:3, clinical trial:3"),
    _tema("Saúde mental", "Saúde", "ansiedade, depressão, psicologia, terapia, burnout",
          "saude mental:3, depressao:3, ansiedade:3, burnout:3, transtorno:2, terapia:2, psicologo:2, "
          "psicologa:2, psiquiatra:3, suicidio:3, setembro amarelo:3, tdah:3, estresse:2, crise de ansiedade:3"),
    _tema("Alimentação", "Saúde", "nutrição, dieta, alimentos, emagrecimento",
          "alimentacao:3, nutricao:3, nutricionista:3, dieta:2, alimento:2, ultraprocessado:3, proteina:2, "
          "vitamina:2, suplemento:2, jejum intermitente:3, emagrecimento:2, emagrecer:2"),
    _tema("Exercícios", "Saúde", "exercício, atividade física, academia, treino, fitness",
          "exercicio:2, atividade fisica:3, academia:2, musculacao:3, caminhada:2, treino:1, pilates:3, "
          "yoga:2, massa muscular:3, sedentarismo:3, longevidade:2, fitness:3"),
    _tema("Vacinas", "Saúde", "vacina, vacinação, imunização",
          "vacina:3, vacinacao:3, imunizacao:3, dose de reforco:3, campanha de vacinacao:3, vaccine:3, "
          "antivacina:3, calendario vacinal:3, butantan:2, fiocruz:2"),

    # ---------------------------------------------------------------- Ciência e meio ambiente
    _tema("Ciência", "Ciência e meio ambiente", "ciência, pesquisa científica, descobertas, science"),
    _tema("Espaço", "Ciência e meio ambiente", "astronomia, universo, nasa, planetas, space",
          "nasa:3, espaco:1, astronomia:3, astronauta:3, planeta:2, galaxia:3, telescopio:3, james webb:3, "
          "spacex:2, foguete:3, marte:3, mars:2, estacao espacial:3, orbita:2, asteroide:3, cometa:3, eclipse:3, "
          "buraco negro:3, black hole:3, exoplaneta:3, artemis:2, satelite:2, meteoro:3, superlua:3"),
    _tema("Meio ambiente", "Ciência e meio ambiente", "ambiente, natureza, sustentabilidade, ecologia",
          "meio ambiente:3, desmatamento:3, amazonia:2, queimada:3, incendio florestal:3, poluicao:3, "
          "reciclagem:3, plastico:2, cop 30:3, cop30:3, sustentabilidade:3, sustentavel:2, biodiversidade:3, ibama:3, "
          "carbono:2, emissao:2, pantanal:2, cerrado:2, saneamento:2, ambientalista:3"),
    _tema("Clima", "Ciência e meio ambiente", "tempo, previsão do tempo, chuva, calor, frio, mudanças climáticas",
          "clima:0, clima de:0, aquecimento global:3, mudanca climatica:3, climate change:3, previsao do tempo:3, chuva:2, chuva de:0, "
          "temporal:3, tempestade:3, onda de calor:3, frente fria:3, massa de ar:3, inmet:3, enchente:3, "
          "alagamento:3, seca:2, el nino:3, la nina:3, furacao:3, hurricane:3, tornado:3, granizo:3, ciclone:3, "
          "defesa civil:2, temperatura:2, meteorologia:3"),
    _tema("Animais", "Ciência e meio ambiente", "animal, bichos, vida selvagem, fauna, wildlife",
          "animal:2, especie:2, vida selvagem:3, wildlife:3, zoologico:3, em extincao:3, baleia:3, tubarao:3, "
          "onca:3, elefante:3, macaco:2, passaro:2, ave:1, golfinho:3, fauna:3"),
    _tema("Arqueologia e história", "Ciência e meio ambiente", "história, arqueologia, dinossauros, fósseis",
          "arqueologia:3, arqueologo:3, fossil:3, dinossauro:3, descoberta arqueologica:3, sitio arqueologico:3, "
          "egito antigo:3, piramide:2, piramide financeira:0, roma antiga:3, idade media:3, historiador:3, mumia:3, tumba:2, "
          "pre historia:3, neandertal:3, segunda guerra mundial:3"),
    _tema("Energia", "Ciência e meio ambiente", "energia, energia solar, petróleo, conta de luz",
          "energia:1, energia solar:3, energia eolica:3, eolica:3, energia renovavel:3, petroleo:2, "
          "hidrogenio verde:3, usina:2, nuclear:2, conta de luz:3, bandeira tarifaria:3, aneel:3, apagao:3, "
          "transicao energetica:3, combustivel fossil:3, biocombustivel:3, etanol:2"),

    # ---------------------------------------------------------------- Estilo de vida
    _tema("Viagens", "Estilo de vida", "viagem, turismo, férias, destinos, travel",
          "viagem:3, turismo:3, turista:2, ferias:2, destino:0, destino turistico:3, hotel:2, resort:3, passagem aerea:3, "
          "aeroporto:2, companhia aerea:3, voo:2, roteiro de viagem:3, mochilao:3, travel:2, passaporte:2, "
          "ponto turistico:3, airbnb:3"),
    _tema("Gastronomia", "Estilo de vida", "comida, culinária, receitas, restaurantes, food",
          "gastronomia:3, receita de bolo:3, receita facil:3, receita caseira:3, modo de preparo:3, ingrediente:2, restaurante:3, chef:3, culinaria:3, comida:2, vinho:3, cerveja:2, "
          "sobremesa:3, michelin:3, churrasco:3, pizza:2, hamburguer:2, prato:1"),
    _tema("Moda e beleza", "Estilo de vida", "moda, beleza, looks, maquiagem, skincare, fashion",
          "moda:3, semana de moda:3, fashion week:3, estilista:3, grife:3, look:2, roupa:2, vestido:2, "
          "maquiagem:3, beleza:2, skincare:3, cuidados com a pele:3, cabelo:2, perfume:2, cosmetico:3, "
          "desfile:2, met gala:3, louis vuitton:3, chanel:2, dior:2, gucci:2, prada:2"),
    _tema("Carros", "Estilo de vida", "carro, automóveis, veículos, motos, carros elétricos",
          "carro:2, carro chefe:0, automovel:3, montadora:3, suv:3, sedan:3, hatch:3, picape:3, concessionaria:3, fipe:3, "
          "carro eletrico:2, hibrido:2, volkswagen:2, fiat:2, chevrolet:2, toyota:2, hyundai:2, byd:2, "
          "renault:2, jeep:2, nissan:2, salao do automovel:3, motocicleta:2, moto:1, recall:2, cnh:2, detran:2, "
          "multa de transito:3"),
    _tema("Casa e decoração", "Estilo de vida", "casa, decoração, jardinagem, design de interiores",
          "decoracao:3, design de interiores:3, reforma da casa:3, jardim:2, jardinagem:3, movel:2, "
          "organizacao da casa:3, eletrodomestico:2, air fryer:3, airfryer:3, cozinha planejada:3"),
    _tema("Relacionamentos", "Estilo de vida", "relacionamento, amor, namoro, família, maternidade",
          "relacionamento:3, vida a dois:3, sexo:2, sexualidade:2, aplicativo de namoro:3, tinder:3, "
          "terapia de casal:3, ciume:2, paquera:3, maternidade:2, paternidade:2, gravidez:2, gestante:2, "
          "parentalidade:3"),
    _tema("Pets", "Estilo de vida", "pet, animais de estimação, cachorros, gatos",
          "pet:3, cachorro:3, cao:1, gato:2, animal de estimacao:3, veterinario:3, pet shop:3, petshop:3, "
          "racao:3, adocao de animal:3, maus trato:2, tutor:1"),
]

POR_NOME = {t["nome"]: t for t in TEMAS}
assert len(POR_NOME) == len(TEMAS), "tema repetido"
assert all(t["grupo"] in GRUPOS for t in TEMAS), "grupo fora da lista"
assert all(amplo in POR_NOME for amplo in DA_CATEGORIA.values()), "tema amplo sem entrada"

# "Série A" do futebol não é série de TV: vira uma palavra só ("seriea"),
# que conta pro Futebol. "Series A" (rodada de startup) fica de fora.
_SERIE_DO_FUTEBOL = re.compile(r"\bserie ([abcd])\b")


def _palavras(texto):
    return [radical(p) for p in _SERIE_DO_FUTEBOL.sub(r"serie\1", normalizar(texto)).split()]


# frase (radicais) -> [(tema, peso)]
INDICE = {}
for _t in TEMAS:
    for _termo, _peso in _t["termos"].items():
        INDICE.setdefault(tuple(_palavras(_termo)), []).append((_t["nome"], _peso))
MAIOR_TERMO = max(len(f) for f in INDICE)


def detectar(titulo, texto, categoria=None):
    """Os temas da notícia: o amplo (da categoria) primeiro, depois os
    específicos que somaram MINIMO, do mais forte pro mais fraco."""
    pontos = Counter()
    for palavras, peso_lugar in (
        (_palavras(titulo), PESO_TITULO),
        (_palavras((texto or "")[:CARACTERES_DO_TEXTO]), PESO_TEXTO),
    ):
        achados = Counter()
        i = 0
        while i < len(palavras):
            # a frase mais longa que começa aqui; as palavras dela não contam de novo
            for n in range(min(MAIOR_TERMO, len(palavras) - i), 0, -1):
                frase = tuple(palavras[i:i + n])
                if frase in INDICE:
                    achados[frase] += 1
                    i += n
                    break
            else:
                i += 1
        for frase, vezes in achados.items():
            for tema, peso in INDICE[frase]:
                pontos[tema] += peso * peso_lugar * min(vezes, 2)
    for tema in pontos:
        so_nessas = POR_NOME[tema]["categorias"]
        if so_nessas and categoria not in so_nessas:
            pontos[tema] = 0  # lista do próprio tema: fora dela, nunca
            continue
        combina = CATEGORIAS_DO_GRUPO.get(POR_NOME[tema]["grupo"])
        if combina and categoria and categoria not in combina:
            pontos[tema] *= PESO_FORA_DO_ASSUNTO
    amplo = DA_CATEGORIA.get(categoria)
    especificos = [t for t, p in pontos.most_common() if p >= MINIMO and t != amplo]
    return ([amplo] if amplo else []) + especificos[: MAX_TEMAS - (1 if amplo else 0)]


def linhas_do_catalogo():
    """(nome, grupo, sinonimos, ordem) pra tabela catalogo_temas."""
    ordem_do_grupo = {g: i for i, g in enumerate(GRUPOS)}
    return [
        (t["nome"], t["grupo"], t["sinonimos"], ordem_do_grupo[t["grupo"]] * 100 + i)
        for i, t in enumerate(TEMAS)
    ]
