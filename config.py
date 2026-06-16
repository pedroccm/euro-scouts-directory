# -*- coding: utf-8 -*-
"""
Configuração central do pipeline Euro Scouts Directory.

Pipeline (3 passos):
  1_fetch_teams.py   -> resolve os domínios dos clubes (TheSportsDB)  -> data/teams.json
  2_scrape_scouts.py -> Apify leads-finder por domínio + cargo "scout" -> data/scouts.json
  3_build_site.py    -> gera o diretório estático                      -> site/index.html
"""

import os

# ---------------------------------------------------------------------------
# Segredos — NÃO ficam aqui (repo é público). Vêm de local_config.py
# (gitignored) ou de variáveis de ambiente. Veja local_config.example.py.
# ---------------------------------------------------------------------------
try:
    from local_config import APIFY_TOKEN, APOLLO_API_KEY
except ImportError:
    APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
    APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY", "")

# Actor microworlds/leads-finder (público — id não é segredo)
APIFY_ACTOR = "heLL6fUofdPgRXZie"

# TheSportsDB (free test key)
THESPORTSDB_KEY = "3"

# Teto de leads por run do Apify (controla custo: 1500 leads ~= US$ 1,50)
MAX_LEADS = 1500

# ---------------------------------------------------------------------------
# Cargos que mandamos pro Apify (matching fuzzy por "contém")
# ---------------------------------------------------------------------------
SCOUT_TITLES = [
    # inglês
    "scout", "scouting", "recruitment", "recruiter",
    "talent identification", "chief scout", "head of recruitment",
    "technical scout",
    # francês
    "recruteur", "recrutement", "cellule de recrutement",
    # espanhol
    "ojeador", "captador", "secretaria tecnica",
    # italiano
    "osservatore", "responsabile scouting",
    # alemão
    "kaderplanung",
    # português-BR
    "olheiro", "captação", "recrutamento", "observador", "analista de scout",
]

# Pós-filtro: só mantemos o lead se o cargo contiver uma destas substrings
# (ascii-safe, multilíngue: EN/ES/IT/DE/FR). Tira ruído tipo "Football Coach".
SCOUT_KEEP = [
    "scout", "scouting", "recruit", "recrut",
    "talent id", "talent identification", "talent acquisition",
    "ojead",          # ojeador (ES)
    "osservat",       # osservatore (IT)
    "reclut",         # reclutamiento (ES) / reclutamento (IT)
    "captac",         # captación (ES)
    "captad",         # captador (ES)
    "captaç",         # captação (PT-BR)
    "olheiro",        # olheiro (PT-BR)
    "observador",     # observador técnico (PT-BR)
    "kaderplan",      # Kaderplanung (DE)
]

# ---------------------------------------------------------------------------
# Big 5 — rosters 2025/26 (96 clubes). Só nomes; o domínio é resolvido via API.
# Para atualizar a cada temporada, basta editar estas listas.
# ---------------------------------------------------------------------------
LEAGUES = {
    "Premier League": [
        "Arsenal", "Aston Villa", "Bournemouth", "Brentford",
        "Brighton & Hove Albion", "Burnley", "Chelsea", "Crystal Palace",
        "Everton", "Fulham", "Leeds United", "Liverpool",
        "Manchester City", "Manchester United", "Newcastle United",
        "Nottingham Forest", "Sunderland", "Tottenham Hotspur",
        "West Ham United", "Wolverhampton Wanderers",
    ],
    "La Liga": [
        "Deportivo Alaves", "Athletic Bilbao", "Atletico Madrid", "Barcelona",
        "Celta Vigo", "Elche", "Espanyol", "Getafe", "Girona", "Levante",
        "Mallorca", "Osasuna", "Rayo Vallecano", "Real Betis", "Real Madrid",
        "Real Oviedo", "Real Sociedad", "Sevilla", "Valencia", "Villarreal",
    ],
    "Serie A": [
        "Atalanta", "Bologna", "Cagliari", "Como", "Cremonese", "Fiorentina",
        "Genoa", "Hellas Verona", "Inter", "Juventus", "Lazio", "Lecce",
        "AC Milan", "Napoli", "Parma", "Pisa", "Roma", "Sassuolo",
        "Torino", "Udinese",
    ],
    "Bundesliga": [
        "Augsburg", "Bayer Leverkusen", "Bayern Munich", "Borussia Dortmund",
        "Borussia Monchengladbach", "Eintracht Frankfurt", "1. FC Heidenheim",
        "Hamburger SV", "Hoffenheim", "1. FC Koln", "Mainz 05", "RB Leipzig",
        "SC Freiburg", "FC St. Pauli", "VfB Stuttgart", "Union Berlin",
        "Werder Bremen", "VfL Wolfsburg",
    ],
    "Ligue 1": [
        "Angers", "Auxerre", "Brest", "Le Havre", "Lens", "Lille", "Lorient",
        "Lyon", "Marseille", "Metz", "Monaco", "Nantes", "Nice", "Paris FC",
        "Paris Saint-Germain", "Rennes", "Strasbourg", "Toulouse",
    ],
    # MLS 2025 (30 clubes) — base anglófona cobre bem
    "MLS": [
        "Atlanta United", "Austin FC", "Charlotte FC", "Chicago Fire",
        "FC Cincinnati", "Colorado Rapids", "Columbus Crew", "FC Dallas",
        "D.C. United", "Houston Dynamo", "Inter Miami", "LA Galaxy",
        "Los Angeles FC", "Minnesota United", "CF Montreal", "Nashville SC",
        "New England Revolution", "New York City FC", "New York Red Bulls",
        "Orlando City", "Philadelphia Union", "Portland Timbers",
        "Real Salt Lake", "San Diego FC", "San Jose Earthquakes",
        "Seattle Sounders", "Sporting Kansas City", "St. Louis City SC",
        "Toronto FC", "Vancouver Whitecaps",
    ],
    # Eredivisie 2025/26 (18 clubes)
    "Eredivisie": [
        "Ajax", "AZ Alkmaar", "Excelsior Rotterdam", "Feyenoord",
        "Fortuna Sittard", "Go Ahead Eagles", "FC Groningen",
        "Heracles Almelo", "NAC Breda", "NEC Nijmegen", "PEC Zwolle",
        "PSV Eindhoven", "Sparta Rotterdam", "SC Telstar", "FC Twente",
        "FC Utrecht", "FC Volendam", "sc Heerenveen",
    ],
    # Liga Portugal Betclic — Primeira Liga 2025/26 (18). Rosters via Wikipédia.
    "Liga Portugal": [
        "Sporting CP", "Benfica", "FC Porto", "Braga", "Vitoria Guimaraes",
        "Famalicao", "Moreirense", "Rio Ave", "Gil Vicente", "Estoril",
        "Casa Pia", "Santa Clara", "Arouca", "Estrela Amadora", "Nacional",
        "AVS", "Tondela", "Alverca",
    ],
    # Liga Portugal 2 — Segunda Liga 2025/26 (times B excluídos: domínio = clube-mãe)
    "Liga Portugal 2": [
        "Academico de Viseu", "Chaves", "Farense", "Feirense", "Felgueiras",
        "Leixoes", "Lusitania Lourosa", "Maritimo", "Oliveirense",
        "Pacos de Ferreira", "Penafiel", "Portimonense", "Torreense",
        "Uniao de Leiria", "Vizela",
    ],
    # EFL Championship 2025/26 (24) — Inglaterra 2ª divisão
    "Championship": [
        "Birmingham City", "Blackburn Rovers", "Bristol City",
        "Charlton Athletic", "Coventry City", "Derby County", "Hull City",
        "Ipswich Town", "Leicester City", "Middlesbrough", "Millwall",
        "Norwich City", "Oxford United", "Portsmouth", "Preston North End",
        "Queens Park Rangers", "Sheffield United", "Sheffield Wednesday",
        "Southampton", "Stoke City", "Swansea City", "Watford",
        "West Bromwich Albion", "Wrexham",
    ],
    # EFL League One 2025/26 (24) — Inglaterra 3ª divisão
    "League One": [
        "AFC Wimbledon", "Barnsley", "Blackpool", "Bolton Wanderers",
        "Bradford City", "Burton Albion", "Cardiff City", "Doncaster Rovers",
        "Exeter City", "Huddersfield Town", "Leyton Orient", "Lincoln City",
        "Luton Town", "Mansfield Town", "Northampton Town",
        "Peterborough United", "Plymouth Argyle", "Port Vale", "Reading",
        "Rotherham United", "Stevenage", "Stockport County", "Wigan Athletic",
        "Wycombe Wanderers",
    ],
    # 2. Bundesliga 2025/26 (18) — Alemanha 2ª divisão
    "2. Bundesliga": [
        "Hertha BSC", "Arminia Bielefeld", "Eintracht Braunschweig",
        "VfL Bochum", "Darmstadt 98", "Dynamo Dresden", "Fortuna Dusseldorf",
        "SV Elversberg", "Greuther Furth", "Hannover 96",
        "1. FC Kaiserslautern", "Karlsruher SC", "Holstein Kiel",
        "1. FC Magdeburg", "Preussen Munster", "1. FC Nurnberg",
        "SC Paderborn", "FC Schalke 04",
    ],
    # ===== BRASIL 2026 (Wikipédia) — nome "Brasileirão" p/ não colidir com Serie A (IT) =====
    "Brasileirão Série A": [
        "Athletico Paranaense", "Atlético Mineiro", "Bahia", "Botafogo",
        "Chapecoense", "Corinthians", "Coritiba", "Cruzeiro", "Flamengo",
        "Fluminense", "Grêmio", "Internacional", "Mirassol", "Palmeiras",
        "Red Bull Bragantino", "Remo", "Santos", "São Paulo", "Vasco da Gama",
        "Vitória",
    ],
    "Brasileirão Série B": [
        "América Mineiro", "Athletic Club", "Atlético Goianiense", "Avaí",
        "Botafogo-SP", "Ceará", "CRB", "Criciúma", "Cuiabá", "Fortaleza",
        "Goiás", "Juventude", "Londrina", "Náutico", "Novorizontino",
        "Operário Ferroviário", "Ponte Preta", "São Bernardo", "Sport",
        "Vila Nova",
    ],
    "Brasileirão Série C": [
        "Amazonas", "Anápolis", "Barra", "Botafogo-PB", "Brusque", "Caxias",
        "Confiança", "Ferroviária", "Figueirense", "Floresta", "Guarani",
        "Inter de Limeira", "Itabaiana", "Ituano", "Maranhão", "Maringá",
        "Paysandu", "Santa Cruz", "Volta Redonda", "Ypiranga",
    ],
    "Brasileirão Série D": [
        "ABC", "Água Santa", "Águia de Marabá", "Altos", "América-RN",
        "Aparecidense", "Araguaína", "ASA", "Atlético de Alagoinhas",
        "Atlético Cearense", "Azuriz", "Betim", "Brasil de Pelotas",
        "Capital", "Ceilândia", "Central", "Cianorte", "CRAC", "CSA", "CSE",
        "FC Cascavel", "Ferroviário", "Gama", "Guarany de Bagé", "Humaitá",
        "Iguatu", "Imperatriz", "Jacuipense", "Joinville", "Juazeirense",
        "Lagarto", "Luverdense", "Madureira", "Manaus", "Maracanã",
        "Marcílio Dias", "Mixto", "Moto Club", "Nova Iguaçu", "Parnahyba",
        "Pouso Alegre", "Primavera", "Real Noroeste", "Retrô", "Rio Branco",
        "Sampaio Corrêa", "São José-RS", "São Luiz", "São Raimundo", "Sergipe",
        "Sousa", "Tocantinópolis", "Tombense", "Treze", "Tuna Luso",
        "Uberlândia", "Velo Clube", "XV de Piracicaba",
    ],
    # Ucrânia — Premier League 2025/26 (16)
    "Ukrainian Premier League": [
        "Dynamo Kyiv", "Epitsentr Kamianets-Podilskyi", "Karpaty Lviv",
        "Kolos Kovalivka", "Kryvbas Kryvyi Rih", "Kudrivka", "LNZ Cherkasy",
        "Metalist 1925 Kharkiv", "Obolon Kyiv", "Oleksandriya",
        "Polissya Zhytomyr", "Poltava", "Rukh Lviv", "Shakhtar Donetsk",
        "Veres Rivne", "Zorya Luhansk",
    ],
    # Bélgica — Pro League 2025/26 (16)
    "Belgian Pro League": [
        "Anderlecht", "Antwerp", "Cercle Brugge", "Charleroi", "Club Brugge",
        "Dender EH", "Genk", "Gent", "La Louvière", "Mechelen", "OH Leuven",
        "Sint-Truiden", "Standard Liège", "Union SG", "Westerlo",
        "Zulte Waregem",
    ],
    # Chipre — First Division 2025/26 (14)
    "Cypriot First Division": [
        "AEK Larnaca", "AEL Limassol", "Akritas Chlorakas",
        "Anorthosis Famagusta", "APOEL", "Apollon Limassol", "Aris Limassol",
        "Enosis Neon Paralimni", "Ethnikos Achna", "Krasava",
        "Olympiakos Nicosia", "Omonia Nicosia", "Omonia Aradippou", "Pafos",
    ],
    # Escócia — Premiership 2025/26 (12)
    "Scottish Premiership": [
        "Aberdeen", "Celtic", "Dundee", "Dundee United", "Falkirk",
        "Heart of Midlothian", "Hibernian", "Kilmarnock", "Livingston",
        "Motherwell", "Rangers", "St Mirren",
    ],
    # Grécia — Super League 2025/26 (14)
    "Super League Greece": [
        "AEK Athens", "AE Kifisia", "AEL Larissa", "Aris Thessaloniki",
        "Asteras Tripolis", "Atromitos", "Levadiakos", "OFI Crete",
        "Olympiacos", "Panathinaikos", "Panetolikos", "Panserraikos",
        "PAOK", "Volos",
    ],
    # Turquia — Süper Lig 2025/26 (18)
    "Süper Lig": [
        "Alanyaspor", "Antalyaspor", "Beşiktaş", "Eyüpspor",
        "Fatih Karagümrük", "Fenerbahçe", "Galatasaray", "Gaziantep",
        "Gençlerbirliği", "Göztepe", "İstanbul Başakşehir", "Kasımpaşa",
        "Kayserispor", "Kocaelispor", "Konyaspor", "Rizespor", "Samsunspor",
        "Trabzonspor",
    ],
    # Arábia Saudita — Pro League 2025/26 (18)
    "Saudi Pro League": [
        "Al-Ahli", "Al-Ettifaq", "Al-Fateh", "Al-Fayha", "Al-Hazem",
        "Al-Hilal", "Al-Ittihad", "Al-Khaleej", "Al-Kholood", "Al-Najma",
        "Al-Nassr", "Al-Okhdood", "Al-Qadsiah", "Al-Riyadh", "Al-Shabab",
        "Al-Taawoun", "Damac", "Neom SC",
    ],
    # Argentina — Liga Profesional 2025 (30)
    "Liga Profesional Argentina": [
        "Aldosivi", "Argentinos Juniors", "Atlético Tucumán", "Banfield",
        "Barracas Central", "Belgrano", "Boca Juniors", "Central Córdoba",
        "Defensa y Justicia", "Deportivo Riestra", "Estudiantes de La Plata",
        "Gimnasia y Esgrima La Plata", "Godoy Cruz", "Huracán", "Independiente",
        "Independiente Rivadavia", "Instituto", "Lanús", "Newell's Old Boys",
        "Platense", "Racing Club", "River Plate", "Rosario Central",
        "San Lorenzo", "San Martín de San Juan", "Sarmiento", "Talleres",
        "Tigre", "Unión", "Vélez Sarsfield",
    ],
    # Suíça — Super League 2025/26 (12)
    "Swiss Super League": [
        "Basel", "Grasshopper", "Lausanne-Sport", "Lugano", "Luzern",
        "Servette", "Sion", "St. Gallen", "Thun", "Winterthur", "Young Boys",
        "Zürich",
    ],
    # Áustria — Bundesliga 2025/26 (12)  [nome distinto da alemã]
    "Austrian Bundesliga": [
        "Austria Wien", "Blau-Weiß Linz", "Grazer AK", "LASK",
        "SK Rapid Wien", "Red Bull Salzburg", "SC Rheindorf Altach", "SV Ried",
        "SK Sturm Graz", "TSV Hartberg", "WSG Tirol", "Wolfsberger AC",
    ],
    # Dinamarca — Superliga 2025/26 (12)
    "Danish Superliga": [
        "AGF", "Brøndby", "Copenhagen", "Fredericia", "Midtjylland",
        "Nordsjælland", "OB", "Randers", "Silkeborg", "Sønderjyske", "Vejle",
        "Viborg",
    ],
    # Polônia — Ekstraklasa 2025/26 (18)
    "Ekstraklasa": [
        "Arka Gdynia", "Termalica Nieciecza", "Cracovia", "GKS Katowice",
        "Górnik Zabrze", "Jagiellonia Białystok", "Korona Kielce",
        "Lech Poznań", "Lechia Gdańsk", "Legia Warsaw", "Motor Lublin",
        "Piast Gliwice", "Pogoń Szczecin", "Radomiak Radom",
        "Raków Częstochowa", "Widzew Łódź", "Wisła Płock", "Zagłębie Lubin",
    ],
    # México — Liga MX 2025/26 (18)
    "Liga MX": [
        "América", "Atlas", "Atlético San Luis", "Cruz Azul", "Guadalajara",
        "Juárez", "León", "Mazatlán", "Monterrey", "Necaxa", "Pachuca",
        "Puebla", "Querétaro", "Santos Laguna", "Tijuana", "Toluca", "Tigres",
        "Pumas UNAM",
    ],
    # Suécia — Allsvenskan 2026 (16)
    "Allsvenskan": [
        "AIK", "BK Häcken", "Degerfors IF", "Djurgårdens IF", "GAIS",
        "Halmstads BK", "Hammarby IF", "IF Brommapojkarna", "IF Elfsborg",
        "IFK Göteborg", "IK Sirius", "Kalmar FF", "Malmö FF", "Mjällby AIF",
        "Västerås SK", "Örgryte IS",
    ],
    # Noruega — Eliteserien 2026 (16)
    "Eliteserien": [
        "Aalesund", "Bodø/Glimt", "Brann", "Fredrikstad", "HamKam",
        "KFUM Oslo", "Kristiansund", "Lillestrøm", "Molde", "Rosenborg",
        "Sandefjord", "Sarpsborg 08", "Start", "Tromsø", "Vålerenga", "Viking",
    ],
}

# Overrides manuais de domínio (caso o TheSportsDB não resolva ou traga errado).
# Preenchido conforme necessário depois do 1º run do fetch_teams.
DOMAIN_OVERRIDES = {
    # clubes que o TheSportsDB não resolveu (429) ou trouxe time errado
    "Arsenal": "arsenal.com",
    "Nottingham Forest": "nottinghamforest.co.uk",
    "Real Madrid": "realmadrid.com",
    "Inter": "inter.it",
    "Hamburger SV": "hsv.de",
    "RB Leipzig": "rbleipzig.com",
    "SC Freiburg": "scfreiburg.com",
    "FC St. Pauli": "fcstpauli.de",
    "Paris Saint-Germain": "psg.fr",
    # MLS: TheSportsDB casou time errado / domínio não-canônico
    "St. Louis City SC": "stlcitysc.com",   # vinha loucity.com (= Louisville City, outro clube)
    "Chicago Fire": "chicagofirefc.com",     # vinha chicago-fire.com
    # Eredivisie
    "Excelsior Rotterdam": "sbvexcelsior.nl",  # não resolveu
    "FC Groningen": "fcgroningen.nl",          # vinha donar.nl (= Donar, clube de basquete)
    # Portugal / Championship / League One / 2.Bundesliga — 429 ou nome variante
    "Nacional": "cdnacional.pt",
    "Leicester City": "lcfc.com",
    "Ipswich Town": "itfc.co.uk",
    "Wigan Athletic": "wiganlatics.co.uk",
    "Wycombe Wanderers": "wwfc.com",
    "FC Schalke 04": "schalke04.de",
    "Alverca": "fcalverca.pt",
    "Tondela": "cdtondela.pt",
    "Chaves": "gdchaves.pt",
    "AVS": "afsfut.pt",
    # ainda sem domínio confiável (clubes pequenos da 2ª PT, scout improvável):
    # Felgueiras, Lusitania Lourosa, Torreense
    # Brasil — notáveis da B/C que o TheSportsDB não resolveu (verificados por HTTP)
    "Vila Nova": "vilanovafc.com.br",
    "São Bernardo": "saobernardofc.com.br",
    "Amazonas": "amazonasfc.com.br",
    "Sport": "sportrecife.com.br",
    # Bélgica / Chipre — notáveis que o TheSportsDB não resolveu (verificados por HTTP)
    "Union SG": "rusg.brussels",
    "Sint-Truiden": "stvv.com",
    "La Louvière": "raal.be",
    "OH Leuven": "ohleuven.be",
    "APOEL": "apoelfc.com.cy",
}

# Federações válidas pro --only (alias = nome da liga)
FED_ALIASES = {
    "PL": "Premier League", "EPL": "Premier League",
    "LALIGA": "La Liga", "LIGA": "La Liga",
    "SERIEA": "Serie A", "SERIE": "Serie A",
    "BUNDESLIGA": "Bundesliga", "BL": "Bundesliga",
    "LIGUE1": "Ligue 1", "L1": "Ligue 1",
    "MLS": "MLS", "USA": "MLS",
    "EREDIVISIE": "Eredivisie", "NL": "Eredivisie", "HOLANDA": "Eredivisie", "NED": "Eredivisie",
    "PORTUGAL": "Liga Portugal", "LIGAPORTUGAL": "Liga Portugal", "PT1": "Liga Portugal", "PRIMEIRA": "Liga Portugal",
    "LIGAPORTUGAL2": "Liga Portugal 2", "PT2": "Liga Portugal 2", "SEGUNDA": "Liga Portugal 2",
    "CHAMPIONSHIP": "Championship", "EFL": "Championship", "CHAMP": "Championship",
    "LEAGUEONE": "League One", "EFL1": "League One", "L1ENG": "League One",
    "BUNDESLIGA2": "2. Bundesliga", "BL2": "2. Bundesliga", "2BL": "2. Bundesliga", "ZWEITE": "2. Bundesliga",
    "BRA": "Brasileirão Série A", "BRASILEIRAO": "Brasileirão Série A", "BRASILEIRAOA": "Brasileirão Série A",
    "BRB": "Brasileirão Série B", "BRASILEIRAOB": "Brasileirão Série B",
    "BRC": "Brasileirão Série C", "BRASILEIRAOC": "Brasileirão Série C",
    "BRD": "Brasileirão Série D", "BRASILEIRAOD": "Brasileirão Série D",
    "UKR": "Ukrainian Premier League", "UKRAINE": "Ukrainian Premier League", "UPL": "Ukrainian Premier League",
    "BEL": "Belgian Pro League", "BELGIUM": "Belgian Pro League", "BELGICA": "Belgian Pro League", "JUPILER": "Belgian Pro League",
    "CYP": "Cypriot First Division", "CYPRUS": "Cypriot First Division", "CHIPRE": "Cypriot First Division",
    "SCO": "Scottish Premiership", "SCOTLAND": "Scottish Premiership", "ESCOCIA": "Scottish Premiership",
    "GRE": "Super League Greece", "GREECE": "Super League Greece", "GRECIA": "Super League Greece",
    "TUR": "Süper Lig", "TURKEY": "Süper Lig", "TURQUIA": "Süper Lig", "SUPERLIG": "Süper Lig",
    "SAU": "Saudi Pro League", "SAUDI": "Saudi Pro League", "ARABIA": "Saudi Pro League", "KSA": "Saudi Pro League",
    "ARG": "Liga Profesional Argentina", "ARGENTINA": "Liga Profesional Argentina",
    "SUI": "Swiss Super League", "SWISS": "Swiss Super League", "SUICA": "Swiss Super League", "SWITZERLAND": "Swiss Super League",
    "AUT": "Austrian Bundesliga", "AUSTRIA": "Austrian Bundesliga",
    "DEN": "Danish Superliga", "DENMARK": "Danish Superliga", "DINAMARCA": "Danish Superliga",
    "POL": "Ekstraklasa", "POLAND": "Ekstraklasa", "POLONIA": "Ekstraklasa", "EKSTRAKLASA": "Ekstraklasa",
    "MEX": "Liga MX", "MEXICO": "Liga MX", "LIGAMX": "Liga MX",
    "SWE": "Allsvenskan", "SWEDEN": "Allsvenskan", "SUECIA": "Allsvenskan", "ALLSVENSKAN": "Allsvenskan",
    "NOR": "Eliteserien", "NORWAY": "Eliteserien", "NORUEGA": "Eliteserien", "ELITESERIEN": "Eliteserien",
}
