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
- **Scouts:** a API do Apollo encontra os scouts mas **mascara nome e LinkedIn**;
  por isso o scrape de verdade é feito pelo actor Apify
  [`microworlds/leads-finder`](https://apify.com/microworlds/leads-finder)
  (base B2B própria, US$ 1 / 1.000 leads), filtrando por `company_domains` +
  `contact_job_titles`. Depois filtramos o ruído mantendo só cargos de scouting
  (`config.SCOUT_KEEP`, multilíngue EN/ES/IT/DE/FR).
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
