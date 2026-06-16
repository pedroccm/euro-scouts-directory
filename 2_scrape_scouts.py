# -*- coding: utf-8 -*-
"""
Passo 2 — Raspa os scouts de cada clube via Apify (actor microworlds/leads-finder).

Para cada liga, roda o actor filtrando por:
  - company_domains  = domínios dos clubes daquela liga (de data/teams.json)
  - contact_job_titles = config.SCOUT_TITLES  (scout / scouting / recruitment ...)
Depois filtra o ruído (mantém só cargos em config.SCOUT_KEEP), atribui cada lead
ao seu clube pelo domínio, deduplica por LinkedIn e salva:

  data/scouts_raw.json  -> tudo, COM email   (privado, no .gitignore)
  data/scouts.json      -> público, SEM email (vira o site)

Uso:
  python 2_scrape_scouts.py                 # todas as ligas
  python 2_scrape_scouts.py --only PL LALIGA
  python 2_scrape_scouts.py --max 200       # teto de leads por liga
"""
import json
import os
import sys
import time
import urllib.request

import config

try:  # stdout UTF-8 (Windows cp1252 quebra em nomes turcos/gregos)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TEAMS = os.path.join(DATA_DIR, "teams.json")
RAW = os.path.join(DATA_DIR, "scouts_raw.json")
PUB = os.path.join(DATA_DIR, "scouts.json")

API = "https://api.apify.com/v2"


def _req(method, url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def run_actor(domains, titles, max_result):
    """Dispara o actor, faz polling até terminar e devolve os itens do dataset."""
    payload = {
        "max_result": max_result,
        "contact_job_titles": titles,
        "company_domains": domains,
    }
    run = _req("POST", f"{API}/acts/{config.APIFY_ACTOR}/runs?token={config.APIFY_TOKEN}", payload)
    rid = run["data"]["id"]
    dsid = run["data"]["defaultDatasetId"]
    print(f"      run {rid} iniciado…", end="", flush=True)
    while True:
        time.sleep(5)
        st = _req("GET", f"{API}/actor-runs/{rid}?token={config.APIFY_TOKEN}")["data"]["status"]
        print(".", end="", flush=True)
        if st in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            print(f" {st}")
            break
    if st != "SUCCEEDED":
        print(f"      ! run terminou em {st}")
        return []
    items = _req("GET", f"{API}/datasets/{dsid}/items?token={config.APIFY_TOKEN}&clean=true")
    return items if isinstance(items, list) else []


def norm_domain(d):
    if not d:
        return ""
    d = str(d).strip().lower().split("://", 1)[-1].split("/", 1)[0]
    return d[4:] if d.startswith("www.") else d


def is_scout(title):
    t = (title or "").lower()
    return any(k in t for k in config.SCOUT_KEEP)


def _load(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []


def main(only_leagues=None, max_per_league=None, append=False):
    with open(TEAMS, encoding="utf-8") as f:
        teams = json.load(f)

    # índice domínio -> clube
    by_domain = {norm_domain(t["domain"]): t for t in teams}

    # agrupa domínios por liga
    leagues = {}
    for t in teams:
        if only_leagues and t["league"] not in only_leagues:
            continue
        leagues.setdefault(t["league"], []).append(norm_domain(t["domain"]))

    n_leagues = max(1, len(leagues))
    cap = max_per_league or max(150, config.MAX_LEADS // n_leagues)

    raw_all = []
    for league, domains in leagues.items():
        print(f"\n== {league}: {len(domains)} clubes, teto {cap} leads ==")
        items = run_actor(domains, config.SCOUT_TITLES, cap)
        print(f"      {len(items)} leads brutos")
        for it in items:
            it["_league"] = league
            raw_all.append(it)

    # ---- dedup + filtro + atribuição ----
    seen = set()
    raw_records = []
    pub_records = []
    if append:
        # parte do que já existe; novas ligas re-raspadas substituem as antigas
        rescraped = set(leagues.keys())
        for r in _load(PUB):
            if r.get("league") in rescraped:
                continue
            pub_records.append(r)
            seen.add(r.get("linkedin") or (r.get("name", "").lower() + "|" + (r.get("club") or "").lower()))
        for r in _load(RAW):
            if r.get("_league") not in rescraped:
                raw_records.append(r)
        print(f"[merge] preservados {len(pub_records)} scouts de outras ligas")
    kept = dropped = 0
    for it in raw_all:
        title = it.get("title") or it.get("headline") or ""
        if not is_scout(title):
            dropped += 1
            continue
        li = (it.get("linkedin_url") or "").strip()
        fname = (it.get("first_name") or "").strip()
        lname = (it.get("last_name") or "").strip()
        full = (fname + " " + lname).strip()
        dom = norm_domain(it.get("organization_primary_domain") or "")
        club = by_domain.get(dom)
        # se o domínio do lead não casar, tenta pelo nome da organização
        club_name = it.get("organization_name") or (club["name"] if club else "")
        league = (club["league"] if club else it.get("_league", ""))
        badge = club["badge"] if club else ""

        key = li or (full.lower() + "|" + (club_name or "").lower())
        if not key or key in seen:
            continue
        seen.add(key)
        kept += 1

        raw_records.append({**it, "_full_name": full, "_club": club_name, "_league": league})
        pub_records.append({
            "name": full or it.get("headline") or "—",
            "title": title,
            "league": league,
            "club": club_name,
            "club_domain": dom,
            "badge": badge,
            "linkedin": li,
            "image": it.get("image") or "",
            "city": it.get("city") or "",
            "country": it.get("country") or "",
        })

    pub_records.sort(key=lambda r: (r["league"], r["club"], r["name"]))

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(RAW, "w", encoding="utf-8") as f:
        json.dump(raw_records, f, ensure_ascii=False, indent=2)
    with open(PUB, "w", encoding="utf-8") as f:
        json.dump(pub_records, f, ensure_ascii=False, indent=2)

    clubs_cov = len({r["club"] for r in pub_records if r["club"]})
    print(f"\n[scouts] mantidos {kept} | descartados (cargo fora de escopo) {dropped}")
    print(f"[scouts] clubes com ao menos 1 scout: {clubs_cov}")
    print(f"[scouts] -> {PUB}  (público, sem email)")
    print(f"[scouts] -> {RAW}  (privado, com email)")
    return pub_records


if __name__ == "__main__":
    only = None
    max_pl = None
    argv = sys.argv[1:]
    append = "--append" in argv
    if "--only" in argv:
        i = argv.index("--only")
        feds = [a for a in argv[i + 1:] if not a.startswith("--")]
        only = [config.FED_ALIASES.get(f.upper(), f) for f in feds]
    if "--max" in argv:
        i = argv.index("--max")
        max_pl = int(argv[i + 1])
    main(only, max_pl, append)
