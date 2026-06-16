# -*- coding: utf-8 -*-
"""
Passo 1 — Resolve a lista de clubes do Big 5 em (liga, nome, domínio, escudo).

Fonte: TheSportsDB `searchteams.php?t={nome}` (devolve o site oficial e o badge).
Nomes vêm de config.LEAGUES; o domínio é derivado do strWebsite (nunca inventado).
Clubes não resolvidos são logados — preencha config.DOMAIN_OVERRIDES e rode de novo.

Saída: data/teams.json
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import config

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUT = os.path.join(DATA_DIR, "teams.json")
BASE = f"https://www.thesportsdb.com/api/v1/json/{config.THESPORTSDB_KEY}/searchteams.php?t="


def domain_from_url(url: str) -> str:
    """www.fcbarcelona.com / https://fcbayern.com/en  ->  fcbarcelona.com / fcbayern.com"""
    if not url:
        return ""
    u = url.strip().lower()
    u = u.split("://", 1)[-1]          # tira protocolo
    u = u.split("/", 1)[0]             # tira path
    if u.startswith("www."):
        u = u[4:]
    return u.strip()


def fetch_team(name: str, retries: int = 4):
    url = BASE + urllib.parse.quote(name)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                data = json.loads(r.read())
            teams = data.get("teams") or []
            return teams[0] if teams else None
        except urllib.error.HTTPError as e:
            if e.code == 429:                       # rate limit do free key
                wait = 5 * (attempt + 1)
                print(f"   … 429 em '{name}', aguardando {wait}s")
                time.sleep(wait)
                continue
            print(f"   ! HTTP {e.code} em '{name}'")
            return None
        except Exception as e:
            print(f"   ! erro de rede em '{name}': {e}")
            time.sleep(3)
    return None


def _load(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []


def main(only_leagues=None):
    os.makedirs(DATA_DIR, exist_ok=True)
    leagues = config.LEAGUES
    if only_leagues:
        leagues = {k: v for k, v in leagues.items() if k in only_leagues}

    # merge: preserva as ligas que NÃO estão sendo (re)resolvidas agora
    out = [t for t in _load(OUT) if t["league"] not in leagues]
    if out:
        print(f"[merge] preservados {len(out)} clubes de outras ligas")
    unresolved = []
    for league, names in leagues.items():
        print(f"\n== {league} ({len(names)} clubes) ==")
        for name in names:
            override = config.DOMAIN_OVERRIDES.get(name)
            badge = ""
            resolved_name = name
            if override:
                domain = override
            else:
                t = fetch_team(name)
                time.sleep(1.2)  # gentileza com o free key (rate limit agressivo)
                domain = domain_from_url((t or {}).get("strWebsite", "")) if t else ""
                badge = (t or {}).get("strBadge", "") or (t or {}).get("strTeamBadge", "") if t else ""
                resolved_name = (t or {}).get("strTeam", name) if t else name
            if not domain:
                unresolved.append(name)
                print(f"   ?? {name:32s} -> SEM DOMINIO (resolver manualmente)")
                continue
            out.append({
                "league": league,
                "name": name,
                "resolved_name": resolved_name,
                "domain": domain,
                "badge": badge,
            })
            print(f"   ok {name:32s} -> {domain}")

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n[teams] {len(out)} clubes resolvidos -> {OUT}")
    if unresolved:
        print(f"[teams] {len(unresolved)} sem domínio: {unresolved}")
        print("        -> adicione em config.DOMAIN_OVERRIDES e rode de novo.")
    return out


if __name__ == "__main__":
    only = None
    if "--only" in sys.argv:
        i = sys.argv.index("--only")
        feds = [a for a in sys.argv[i + 1:] if not a.startswith("--")]
        only = []
        for f in feds:
            only.append(config.FED_ALIASES.get(f.upper(), f))
    main(only)
