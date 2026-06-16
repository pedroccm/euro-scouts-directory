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
}

# Federações válidas pro --only (alias = nome da liga)
FED_ALIASES = {
    "PL": "Premier League", "EPL": "Premier League",
    "LALIGA": "La Liga", "LIGA": "La Liga",
    "SERIEA": "Serie A", "SERIE": "Serie A",
    "BUNDESLIGA": "Bundesliga", "BL": "Bundesliga",
    "LIGUE1": "Ligue 1", "L1": "Ligue 1",
    "MLS": "MLS", "USA": "MLS",
}
