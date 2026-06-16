# Euro Scouts Directory

🔗 **No ar:** https://euro-scouts-directory.netlify.app

Pipeline que monta um **diretório de scouts** (olheiros / recrutamento) dos clubes
do **Big 5 europeu + MLS**, achando o **LinkedIn** de cada um, e gera um **site
estático** com busca e filtros. (1º build: 525 scouts, 86 clubes, 6 ligas.)

## Como funciona

```
1_fetch_teams.py   →  resolve domínio de cada clube (TheSportsDB)      →  data/teams.json
2_scrape_scouts.py →  Apify leads-finder por domínio + cargo "scout"   →  data/scouts.json
3_build_site.py    →  gera o diretório estático                        →  site/index.html
```

- **Times:** rosters Big 5 2025/26 hardcoded em `config.py` (`LEAGUES`). O domínio
  oficial de cada clube é puxado da API do TheSportsDB (nunca inventado).
- **Scouts — duas fontes (mescladas por LinkedIn):**
  1. **Apify** [`microworlds/leads-finder`](https://apify.com/microworlds/leads-finder)
     (`2_scrape_scouts.py`, US$ 1/1k) — boa pra ligas anglófonas.
  2. **Apollo logado** (`2_scrape_apollo.py`) — a API por key mascara nome/LinkedIn,
     então usamos a **API interna do site** (`app.apollo.io`) com **cookie de sessão**
     (`apollo_cookies.json`, gitignored), que devolve nome+LinkedIn+foto sem máscara.
     Cobre muito melhor FR/ES/IT/PT. Free plan limita a 5 páginas → raspa **por clube**.
  Em ambas filtramos o ruído mantendo só cargos de scouting (`config.SCOUT_KEEP`,
  multilíngue EN/ES/IT/DE/FR). Ex.: Ligue 1 saiu de 4 → 100 scouts ao usar o Apollo.
- **Site:** HTML estático puro (sem framework), dados embutidos inline — abre
  direto no navegador ou publica no Netlify.

## Setup (segredos)

Os tokens **não** ficam no repo. Copie o exemplo e preencha:

```bash
cp local_config.example.py local_config.py   # depois edite com seus tokens
```

`local_config.py` está no `.gitignore`. Alternativa: definir as env vars
`APIFY_TOKEN` e `APOLLO_API_KEY`.

## Rodar

```bash
cd E:\sites\euro-scouts
python run_all.py                  # Big 5 completo
python run_all.py --only PL LALIGA # só algumas ligas  (PL, LALIGA, SERIEA, BUNDESLIGA, LIGUE1, MLS)
python run_all.py --max 200        # teto de leads por liga (controla custo)

# adicionar/atualizar uma liga sem re-raspar o resto:
python 1_fetch_teams.py  --only MLS
python 2_scrape_scouts.py --only MLS --append --max 450
python 3_build_site.py
```

Deploy é automático: `git push` → Netlify rebuilda (publish dir = `site/`).

Ou passo a passo: `python 1_fetch_teams.py` → `python 2_scrape_scouts.py` → `python 3_build_site.py`.

## Custo (Apify)

- Token usado: projeto `gourmet_voltage` (FREE tier, ~US$ 5/mês de crédito).
- `$1 / 1.000 leads`. O Big 5 completo gira em torno de **US$ 1–2**.
- `MAX_LEADS` em `config.py` limita o teto por run.

## Privacidade

- `data/scouts_raw.json` guarda **email** e fica no `.gitignore` (não vai pro git).
- `data/scouts.json` (e o site) trazem só **nome, cargo, clube, LinkedIn, foto,
  cidade** — informação profissional pública.

## Atualizar a cada temporada

Editar as listas em `config.py → LEAGUES` (entram os promovidos, saem os
rebaixados). Se algum clube não resolver domínio, ele é logado — preencha
`config.DOMAIN_OVERRIDES` e rode de novo.
