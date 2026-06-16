# -*- coding: utf-8 -*-
"""
Roda o pipeline inteiro: teams -> scouts -> site.

  python run_all.py                  # Big 5 completo
  python run_all.py --only PL LALIGA # só algumas ligas
  python run_all.py --max 200        # teto de leads por liga
"""
import importlib
import sys

import config

fetch_teams = importlib.import_module("1_fetch_teams")
scrape_scouts = importlib.import_module("2_scrape_scouts")
build_site = importlib.import_module("3_build_site")


def parse():
    argv = sys.argv[1:]
    only = None
    max_pl = None
    if "--only" in argv:
        i = argv.index("--only")
        feds = [a for a in argv[i + 1:] if not a.startswith("--")]
        only = [config.FED_ALIASES.get(f.upper(), f) for f in feds]
    if "--max" in argv:
        max_pl = int(argv[argv.index("--max") + 1])
    return only, max_pl


if __name__ == "__main__":
    only, max_pl = parse()
    print("==== 1/3 fetch teams ====")
    fetch_teams.main(only)
    print("\n==== 2/3 scrape scouts (Apify) ====")
    scrape_scouts.main(only, max_pl)
    print("\n==== 3/3 build site ====")
    build_site.main()
    print("\nPronto. Abra site/index.html")
