"""
Taxonomia do Daily Paper, sem IA: para cada categoria, os termos que a
denunciam (português e inglês, já sem acento e em minúsculas, como
sinais.normalizar devolve). Peso 1 = indício; 2 = forte; 3 = quase certo.

As categorias são as mesmas de sempre (o hub, o e-mail e o Trending usam
essa lista). Os temas (Filmes, Fofoca, Inteligência artificial...)
ficam no catálogo de temas.py: uma notícia pode ter vários.

Pra melhorar a classificação, é aqui que se mexe: um termo novo, um peso
diferente. O classificar.py imprime as notícias que ficaram sem
categoria clara, pra ver o que falta.
"""

# Países e capitais (português e inglês, normalizados): sinal forte de
# "Mundo". Sem "ira" (vira o verbo "irá"); "roma" e "santiago" também são
# times e nomes, mas o peso de Esportes costuma ganhar quando é o caso.
def _lista_de_paises(texto):
    # nomes de uma ou mais palavras separados por espaço duplo seria frágil:
    # cada linha tem nomes de 1 palavra, e os compostos ficam juntos abaixo
    compostos = [
        "africa do sul", "arabia saudita", "buenos aires", "cabo verde", "coreia do sul", "coreia do norte",
        "costa rica", "emirados arabes", "estados unidos", "nova york", "hong kong", "nova delhi", "tel aviv",
        "nova zelandia", "reino unido", "republica dominicana", "sri lanka", "united kingdom", "saudi arabia",
        "new zealand", "south korea", "north korea", "south africa",
    ]
    restante = texto
    for c in compostos:
        restante = restante.replace(c, " ")
    return compostos + [p for p in restante.split() if p]


PAISES = _lista_de_paises("""
afeganistao cabul africa do sul alemanha berlim angola arabia saudita argelia argentina buenos aires armenia
australia austria azerbaijao bangladesh belgica bielorrussia bolivia bosnia bulgaria cabo verde camboja canada
catar chile santiago china pequim xangai colombia bogota coreia do sul coreia do norte seul costa rica croacia cuba
havana dinamarca egito cairo emirados arabes equador escocia eslovaquia espanha madri estados unidos washington
nova york estonia etiopia filipinas finlandia franca paris gana georgia grecia atenas guatemala haiti holanda
honduras hong kong hungria iemen india nova delhi indonesia inglaterra londres irlanda islandia israel jerusalem
tel aviv italia roma jamaica japao toquio jordania kosovo kuwait libano libia lituania marrocos mexico mocambique
moldavia mongolia myanmar nepal nicaragua nigeria noruega nova zelandia paquistao palestina panama paraguai
polonia portugal lisboa quenia reino unido republica dominicana romenia ruanda russia moscou senegal servia
singapura siria somalia sri lanka sudao suecia suica tailandia taiwan tanzania teera turquia ancara ucrania kiev
uganda uruguai montevideu venezuela caracas vietna vietnam zambia zimbabue
germany france spain italy japan canada mexico brazil united kingdom england london russia ukraine israel iran
iraq syria lebanon egypt saudi arabia turkey greece poland sweden norway denmark finland netherlands belgium
switzerland austria australia new zealand south korea north korea taiwan vietnam thailand indonesia philippines
india pakistan afghanistan nigeria kenya south africa argentina chile colombia venezuela cuba
""")

CATEGORIAS = {
    "Política": {
        "termos": {
            "lula": 2, "bolsonaro": 2, "flavio bolsonaro": 2, "alckmin": 2, "haddad": 1, "tarcisio": 2,
            "stf": 2, "supremo": 2, "moraes": 2, "camara dos deputados": 3, "senado": 2, "senador": 2,
            "deputado": 2, "deputada": 2, "vereador": 2, "prefeito": 1, "governador": 1, "ministro": 1,
            "ministerio": 1, "planalto": 2, "congresso": 2, "pec": 2, "projeto de lei": 2, "eleicao": 2,
            "eleicoes": 2, "eleitoral": 2, "tse": 2, "candidato": 2, "candidata": 2, "campanha": 1,
            "pesquisa eleitoral": 3, "quaest": 2, "datafolha": 2, "partido": 2, "pt": 1, "pl": 1, "psdb": 2,
            "mdb": 2, "psol": 2, "uniao brasil": 2, "centrao": 2, "impeachment": 2, "cpi": 2, "pgr": 2,
            "policia federal": 1, "governo federal": 2, "oposicao": 1, "base aliada": 2, "debate": 1,
            "segundo turno": 2, "primeiro turno": 2, "urna": 2, "votacao": 1, "plenario": 2, "ccj": 2,
        },
    },
    "Mundo": {
        "termos": {
            "trump": 2, "casa branca": 2, "white house": 2, "putin": 2, "russia": 2, "ucrania": 2, "ukraine": 2,
            "israel": 2, "gaza": 2, "hamas": 2, "ira": 1, "iran": 2, "china": 1, "xi jinping": 2, "pequim": 2,
            "beijing": 2, "onu": 2, "united nations": 2, "otan": 2, "nato": 2, "uniao europeia": 2,
            "european union": 2, "vaticano": 2, "papa": 2, "pope": 2, "guerra": 1, "war": 1, "cessar fogo": 2,
            "ceasefire": 2, "diplomacia": 2, "embaixada": 2, "estados unidos": 1, "eua": 1, "argentina": 1,
            "milei": 2, "venezuela": 2, "maduro": 2, "peru": 1, "mexico": 1, "franca": 1, "macron": 2,
            "alemanha": 1, "reino unido": 1, "londres": 1, "groenlandia": 2, "japao": 1, "coreia do norte": 2,
            "india": 1, "oriente medio": 2, "middle east": 2, "terrorismo": 1, "refugiados": 1,
            "internacional": 1, "presidente americano": 2, "premie": 2, "primeiro ministro": 2, "chanceler": 2,
            "prime minister": 2, "kremlin": 2, "parlamento europeu": 2, "taleba": 2, "taliban": 2,
            **{pais: 2 for pais in PAISES},
        },
    },
    "Finanças": {
        "termos": {
            "ibovespa": 3, "bolsa": 1, "b3": 2, "dolar": 2, "acoes": 2, "acao": 1, "investidor": 2,
            "investidores": 2, "investimento": 1, "juros": 2, "selic": 3, "copom": 3, "banco central": 2,
            "inflacao": 2, "ipca": 3, "pib": 2, "economia": 2, "economico": 1, "mercado financeiro": 3,
            "lucro": 2, "receita": 1, "faturamento": 2, "balanco": 2, "trimestre": 2, "dividendos": 3,
            "tesouro": 2, "fiscal": 2, "arrecadacao": 2, "imposto": 1, "impostos": 1, "tributaria": 2,
            "petrobras": 1, "vale": 1, "bitcoin": 2, "cripto": 2, "criptomoeda": 2, "startup": 1, "ipo": 3,
            "fusao": 2, "aquisicao": 1, "stock": 1, "stocks": 2, "earnings": 2, "inflation": 2, "fed": 2,
            "wall street": 2, "nasdaq": 2, "tarifa": 1, "tarifas": 1, "tariffs": 1, "desemprego": 2,
            "emprego": 1, "salario minimo": 2, "credito": 1, "banco": 1, "bancos": 1, "varejo": 1,
            "petroleo": 2, "barril": 2, "commodities": 3, "precos": 1, "preco": 1, "gasolina": 2,
            "combustivel": 2, "combustiveis": 2, "diesel": 2, "consumidor": 1, "vendas": 1, "mercado": 1,
            "empresa": 1, "empresas": 1, "investimentos": 2, "agronegocio": 2, "safra": 2, "exportacoes": 2,
            "importacoes": 2, "balanca comercial": 3, "orcamento": 1, "divida": 1, "falencia": 2,
            "recuperacao judicial": 3, "fintech": 2, "pix": 1, "cartao de credito": 2, "aposentadoria": 1, "inss": 2,
        },
    },
    "Tecnologia": {
        "termos": {
            "inteligencia artificial": 3, "artificial intelligence": 3, "ia": 1, "ai": 1, "openai": 3,
            "chatgpt": 3, "gemini": 2, "claude": 1, "anthropic": 3, "nvidia": 2, "google": 1, "apple": 1,
            "microsoft": 1, "meta": 1, "samsung": 1, "iphone": 3, "android": 3, "ios": 2, "smartphone": 3,
            "celular": 2, "app": 1, "aplicativo": 2, "software": 2, "hardware": 2, "chip": 2, "chips": 2,
            "processador": 2, "semicondutores": 2, "computador": 1, "notebook": 2, "tablet": 2, "whatsapp": 2,
            "instagram": 1, "tiktok": 1, "x antigo twitter": 2, "elon musk": 1, "tesla": 1, "spacex": 1,
            "hacker": 2, "hackers": 2, "ciberseguranca": 3, "cybersecurity": 3, "vazamento de dados": 3,
            "golpe digital": 2, "5g": 2, "internet": 1, "big tech": 2, "algoritmo": 1, "robo": 1, "robotica": 2,
            "carro eletrico": 2, "carros eletricos": 2, "tecnologia": 2, "tech": 1, "startup": 1, "galaxy": 2,
            "pixel": 1, "xiaomi": 2, "motorola": 2, "windows": 2, "linux": 2, "update": 1, "atualizacao": 1,
        },
    },
    "Games": {
        "termos": {
            "game": 2, "games": 2, "videogame": 3, "videogames": 3, "gamer": 2, "playstation": 3, "ps5": 3,
            "ps4": 3, "xbox": 3, "nintendo": 3, "switch 2": 3, "nintendo switch": 3, "steam": 2, "console": 2,
            "consoles": 2, "gameplay": 3, "dlc": 3, "rpg": 2, "fps": 2, "e sports": 3, "esports": 3,
            "pokemon": 2, "zelda": 3, "mario": 2, "gta": 3, "fortnite": 3, "minecraft": 3, "call of duty": 3,
            "ea sports": 2, "ubisoft": 3, "capcom": 3, "bethesda": 3, "remake": 1, "remaster": 2,
            "jogo de": 1, "lancamento do jogo": 3, "estudio": 1, "early access": 3, "battle royale": 3,
        },
    },
    "Cinema": {
        "termos": {
            "filme": 2, "filmes": 2, "film": 2, "movie": 2, "cinema": 2, "cinemas": 2, "serie": 2, "series": 1,
            "temporada": 1, "season": 1, "episodio": 2, "episode": 1, "trailer": 2, "teaser": 2, "estreia": 1,
            "bilheteria": 3, "box office": 3, "netflix": 2, "hbo": 2, "max": 1, "disney": 1, "prime video": 2,
            "apple tv": 2, "streaming": 2, "oscar": 2, "emmy": 2, "globo de ouro": 2, "diretor": 1, "diretora": 1,
            "elenco": 2, "cast": 1, "ator": 1, "atriz": 1, "marvel": 2, "dc": 1, "pixar": 2, "sequencia": 1,
            "remake": 1, "festival de cannes": 3, "hollywood": 2, "roteiro": 1, "anime": 2,
        },
    },
    "Entretenimento": {
        "termos": {
            "cantor": 2, "cantora": 2, "musica": 2, "album": 2, "show": 1, "turne": 2, "tour": 1, "banda": 2,
            "hit": 1, "clipe": 2, "spotify": 2, "grammy": 2, "rock in rio": 3, "lollapalooza": 3, "festival": 1,
            "novela": 3, "reality": 2, "bbb": 3, "big brother": 3, "a fazenda": 3, "famosos": 2, "celebridade": 2,
            "influenciador": 2, "influenciadora": 2, "apresentador": 2, "apresentadora": 2, "tv globo": 2,
            "globo": 1, "sbt": 2, "record": 1, "band": 1, "namoro": 2, "casamento": 1, "gravidez": 1,
            "aniversario": 1, "morre": 1, "morreu": 1, "livro": 1, "escritor": 1, "literatura": 2,
            "famosa": 2, "famoso": 2, "ex bbb": 3, "modelo": 1, "ator": 1, "atriz": 1, "fas": 1, "fa": 1,
            "rapper": 2, "pop": 1, "biografia": 1, "heranca": 1, "polemica": 1, "web": 1,
            "singer": 2, "album release": 2, "concert": 2, "celebrity": 2, "axe": 2, "sertanejo": 2, "funk": 1,
        },
    },
    "Esportes": {
        "termos": {
            "futebol": 3, "brasileirao": 3, "libertadores": 3, "sul americana": 3, "copa do brasil": 3,
            "copa do mundo": 2, "champions league": 3, "liga dos campeoes": 3, "premier league": 3,
            "selecao": 2, "gol": 2, "gols": 2, "placar": 2, "rodada": 2, "partida": 2, "jogo": 1, "jogos": 1,
            "tecnico": 2, "tecnico do": 2, "treinador": 2, "jogador": 2, "atacante": 3, "zagueiro": 3,
            "goleiro": 3, "meia": 1, "escalacao": 3, "escalacoes": 3, "onde assistir": 2, "campeonato": 2,
            "flamengo": 3, "palmeiras": 3, "corinthians": 3, "sao paulo fc": 3, "santos": 1, "vasco": 3,
            "fluminense": 3, "botafogo": 3, "gremio": 3, "internacional": 1, "cruzeiro": 3, "atletico mg": 3,
            "real madrid": 3, "barcelona": 2, "psg": 3, "manchester city": 3, "liverpool": 2, "nba": 3,
            "nfl": 3, "f1": 3, "formula 1": 3, "gp": 1, "tenis": 2, "volei": 3, "basquete": 3, "ufc": 3,
            "olimpiadas": 3, "olimpico": 2, "atleta": 2, "maratona": 2, "copa": 1, "torcida": 2, "estadio": 2,
            "maracana": 2, "cbf": 3, "fifa": 2, "transfer": 1, "contratacao": 2, "reforco": 2,
            "atp": 3, "wta": 3, "ranking": 1, "torneio": 2, "numero um do mundo": 2, "grand slam": 3,
            "roland garros": 3, "wimbledon": 3, "us open": 2, "medalha": 2, "campeao": 2, "campea": 2,
            "semifinal": 2, "quartas de final": 3, "final": 1, "clube": 2, "time": 1, "times": 1,
            "artilheiro": 3, "rebaixamento": 3, "classificacao": 1, "sub 20": 2, "feminino": 1,
        },
    },
    "Saúde": {
        "termos": {
            "saude": 2, "doenca": 2, "doencas": 2, "vacina": 3, "vacinacao": 3, "hospital": 1, "sus": 2,
            "medico": 1, "medicos": 1, "medicamento": 2, "remedio": 2, "anvisa": 3, "cancer": 2, "tumor": 2,
            "diabetes": 3, "obesidade": 2, "dengue": 3, "covid": 3, "virus": 2, "surto": 2, "epidemia": 3,
            "pandemia": 2, "oms": 3, "who": 1, "tratamento": 1, "cirurgia": 1, "saude mental": 3,
            "depressao": 2, "ansiedade": 2, "sono": 1, "dieta": 2, "nutricao": 2, "emagrecimento": 2,
            "canetas emagrecedoras": 3, "ozempic": 3, "tirzepatida": 3, "health": 2, "disease": 2, "vaccine": 3,
        },
    },
    "Ciência": {
        "termos": {
            "ciencia": 2, "cientistas": 3, "cientista": 2, "pesquisa": 1, "pesquisadores": 2, "estudo": 1,
            "universidade": 1, "nasa": 3, "espaco": 2, "astronomia": 3, "astronautas": 3, "planeta": 2,
            "galaxia": 3, "telescopio": 3, "fossil": 3, "dinossauro": 3, "arqueologia": 3, "arqueologos": 3,
            "clima": 1, "aquecimento global": 3, "mudancas climaticas": 3, "climate change": 3, "biologia": 2,
            "fisica": 2, "quimica": 2, "genetica": 2, "dna": 2, "especie": 2, "especies": 2, "oceano": 1,
            "meio ambiente": 2, "desmatamento": 2, "amazonia": 1, "science": 2, "scientists": 3, "study": 1,
            "researchers": 2, "space": 1,
        },
    },
    "Humor": {"termos": {}},
    "Outros": {"termos": {}},
}

# Categoria do catálogo (a do site) -> categoria das notícias. As que só
# existem no catálogo viram a mais próxima (ou nenhuma).
DA_FONTE = {
    "Notícias": None, "Meio ambiente": "Ciência", "Automóveis": None,
}

# Sites de um assunto só: a categoria do site pesa mais
FONTES_ESPECIALIZADAS = {"Games", "Cinema", "Esportes", "Tecnologia", "Finanças", "Saúde", "Ciência", "Entretenimento", "Humor"}
