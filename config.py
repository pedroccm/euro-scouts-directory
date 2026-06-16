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
}
