# -*- coding: utf-8 -*-
"""
Passo 2 (alternativo/complementar) — Raspa scouts via API LOGADA do Apollo.

Por que existe: a base do Apify (microworlds) sub-indexa futebol não-anglófono
(Ligue 1, La Liga, Serie A, Portugal...). O Apollo tem MUITO mais scouts desses
clubes — mas a API por key mascara nome/LinkedIn. Aqui usamos a API interna do
site (app.apollo.io) com o COOKIE de sessão logado, que devolve tudo sem máscara.

Pré-requisito: `apollo_cookies.json` (gitignored) com os cookies do app.apollo.io
logado (incluindo `_leadgenie_session` e `X-CSRF-TOKEN`). Quando expirar, recapture.

Mescla ADITIVAMENTE em data/scouts.json (dedup por LinkedIn) — não remove nada do
que o Apify já trouxe; só acrescenta o que faltava.

Uso:
  python 2_scrape_apollo.py                      # todas as ligas
  python 2_scrape_apollo.py --only LIGUE1 LALIGA
  python 2_scrape_apollo.py --pages 12           # teto de páginas por liga
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

import config

ROOT = os.path.dirname(__file__)
DATA = os.path.join(ROOT, "data")
TEAMS = os.path.join(DATA, "teams.json")
RAW = os.path.join(DATA, "scouts_raw.json")
PUB = os.path.join(DATA, "scouts.json")
COOKIES = os.path.join(ROOT, "apollo_cookies.json")

ENDPOINT = "https://app.apollo.io/api/v1/mixed_people/search"
PER_PAGE = 25
PAGE_CAP = 10           # teto de páginas por liga (25*10 = 250 scouts/liga)
SLEEP = 1.3             # gentileza entre requisições


def _load(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []


def headers():
    cookies = _load(COOKIES)
    if not cookies:
        sys.exit(f"[apollo] {COOKIES} não encontrado — exporte o cookie do app.apollo.io logado.")
    cookie_hdr = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
    csrf = next((c["value"] for c in cookies if c["name"] == "X-CSRF-TOKEN"), "")
    return {
        "Content-Type": "application/json",
        "X-CSRF-TOKEN": csrf,
        "Cookie": cookie_hdr,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Origin": "https://app.apollo.io",
        "Referer": "https://app.apollo.io/",
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "XMLHttpRequest",
    }


def search(hdrs, domains, page):
    body = {
        "q_organization_domains_list": domains,
        "person_titles": config.SCOUT_TITLES,
        "page": page,
        "per_page": PER_PAGE,
    }
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(),
                                 method="POST", headers=hdrs)
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())


def norm_li(u):
    if not u:
        return ""
    u = str(u).strip().lower().split("://", 1)[-1].rstrip("/")
    return u[4:] if u.startswith("www.") else u


def clean_club(name):
    n = (name or "").strip()
    for suf in (" Groupe", " Football SAD", " SAD", " S.A.D.", " e.V.", " - SAF"):
        if n.endswith(suf):
            n = n[: -len(suf)].strip()
    return n


def is_scout(title):
    t = (title or "").lower()
    return any(k in t for k in config.SCOUT_KEEP)


def main(only_leagues=None, page_cap=PAGE_CAP):
    teams = _load(TEAMS)
    selected = [t for t in teams if not only_leagues or t["league"] in only_leagues]

    hdrs = headers()

    # carrega o que já existe (Apify + runs anteriores) e mescla ADITIVO
    pub = _load(PUB)
    raw = _load(RAW)
    seen = {norm_li(r.get("linkedin")) for r in pub if r.get("linkedin")}
    seen.discard("")

    added_by_league = {}
    stop = False
    for t in selected:
        if stop:
            break
        league, club, dom, badge = t["league"], t["name"], t["domain"], t.get("badge", "")
        added = 0
        page = 1
        while page <= page_cap:
            try:
                d = search(hdrs, [dom], page)
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    print(f"[apollo] HTTP {e.code} em {club} — cookie expirado. PARANDO (recapture o cookie).")
                    stop = True
                else:
                    print(f"   ! {club} p{page}: HTTP {e.code}")
                break
            except Exception as e:
                print(f"   ! {club} p{page}: {e}")
                break
            ppl = d.get("people") or []
            total_pages = (d.get("pagination") or {}).get("total_pages") or 1
            for p in ppl:
                if not is_scout(p.get("title")):
                    continue
                li = norm_li(p.get("linkedin_url"))
                if not li or li in seen:
                    continue
                seen.add(li)
                added += 1
                rec = {
                    "name": p.get("name") or (f"{p.get('first_name','')} {p.get('last_name','')}").strip() or "—",
                    "title": p.get("title") or p.get("headline") or "",
                    "league": league,
                    "club": club,                       # nome canônico do teams.json
                    "club_domain": dom,
                    "badge": badge,                     # badge do TheSportsDB
                    "linkedin": p.get("linkedin_url") or "",
                    "image": p.get("photo_url") or "",
                    "city": p.get("city") or "",
                    "country": p.get("country") or "",
                }
                pub.append(rec)
                raw.append({**rec, "email": p.get("email"), "_source": "apollo"})
            time.sleep(SLEEP)
            if page >= total_pages:
                break
            page += 1
        added_by_league[league] = added_by_league.get(league, 0) + added
        if added:
            print(f"   {league:16s} {club:26s} +{added}")

    pub.sort(key=lambda r: (r["league"], r.get("club") or "", r["name"]))
    with open(PUB, "w", encoding="utf-8") as f:
        json.dump(pub, f, ensure_ascii=False, indent=2)
    with open(RAW, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)

    tot_new = sum(added_by_league.values())
    print(f"\n[apollo] +{tot_new} scouts novos | total agora {len(pub)}")
    for lg, n in added_by_league.items():
        print(f"   {lg}: +{n}")


if __name__ == "__main__":
    argv = sys.argv[1:]
    only = None
    cap = PAGE_CAP
    if "--only" in argv:
        i = argv.index("--only")
        feds = [a for a in argv[i + 1:] if not a.startswith("--")]
        only = [config.FED_ALIASES.get(f.upper(), f) for f in feds]
    if "--pages" in argv:
        cap = int(argv[argv.index("--pages") + 1])
    main(only, cap)
