# -*- coding: utf-8 -*-
"""
Passo 3 — Gera o diretório estático (HTML puro, sem framework).

Lê data/scouts.json e escreve site/index.html com os dados embutidos inline
(funciona abrindo o arquivo direto OU publicado no Netlify). Busca + filtro por
liga e por clube são client-side. Sem email (respeita a escolha nome+cargo+LI).

Saída: site/index.html  (+ site/data.json para referência)
"""
import datetime
import json
import os

import config

ROOT = os.path.dirname(__file__)
PUB = os.path.join(ROOT, "data", "scouts.json")
SITE_DIR = os.path.join(ROOT, "site")

PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Euro Scouts Directory</title>
<style>
:root{
  --bg:#0b0f17; --panel:#121826; --panel2:#1a2233; --line:#243049;
  --txt:#e8edf6; --muted:#8a97ad; --accent:#37d399; --li:#0a66c2;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:inherit;text-decoration:none}
header{padding:34px 20px 18px;text-align:center;border-bottom:1px solid var(--line);
  background:radial-gradient(1200px 300px at 50% -120px,#16324a 0%,transparent 70%)}
h1{margin:0;font-size:30px;letter-spacing:.3px}
h1 span{color:var(--accent)}
.sub{color:var(--muted);margin-top:6px;font-size:14px}
.wrap{max-width:1180px;margin:0 auto;padding:20px}
.controls{position:sticky;top:0;z-index:5;background:var(--bg);
  padding:16px 0;border-bottom:1px solid var(--line);margin-bottom:18px}
.searchbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
input[type=search],select{
  background:var(--panel);border:1px solid var(--line);color:var(--txt);
  padding:11px 13px;border-radius:10px;font-size:14px;outline:none}
input[type=search]{flex:1;min-width:240px}
input[type=search]:focus,select:focus{border-color:var(--accent)}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.chip{padding:7px 13px;border:1px solid var(--line);border-radius:999px;
  background:var(--panel);color:var(--muted);font-size:13px;cursor:pointer;user-select:none}
.chip.active{background:var(--accent);color:#06281c;border-color:var(--accent);font-weight:600}
.count{color:var(--muted);font-size:13px;margin:6px 2px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;
  padding:16px;display:flex;flex-direction:column;gap:10px;transition:.15s}
.card:hover{border-color:var(--accent);transform:translateY(-2px)}
.top{display:flex;gap:12px;align-items:center}
.avatar{width:52px;height:52px;border-radius:50%;object-fit:cover;background:var(--panel2);
  border:1px solid var(--line);flex:none}
.who{min-width:0}
.name{font-weight:600;font-size:15px;line-height:1.2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.title{color:var(--muted);font-size:12.5px;margin-top:3px}
.club{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--txt);
  border-top:1px solid var(--line);padding-top:10px}
.club img{width:20px;height:20px;object-fit:contain;flex:none}
.league-tag{font-size:11px;color:var(--muted)}
.loc{font-size:12px;color:var(--muted)}
.li-btn{margin-top:auto;display:inline-flex;align-items:center;justify-content:center;gap:8px;
  background:var(--li);color:#fff;padding:9px;border-radius:9px;font-size:13px;font-weight:600}
.li-btn:hover{filter:brightness(1.1)}
.li-btn.off{background:var(--panel2);color:var(--muted);pointer-events:none}
.empty{text-align:center;color:var(--muted);padding:60px 0}
footer{color:var(--muted);font-size:12px;text-align:center;padding:30px 20px;border-top:1px solid var(--line)}
</style>
</head>
<body>
<header>
  <h1>Euro <span>Scouts</span> Directory</h1>
  <div class="sub">Scouts & recruitment staff across the Big 5 leagues — __TOTAL__ profiles · __CLUBS__ clubs</div>
</header>
<div class="wrap">
  <div class="controls">
    <div class="searchbar">
      <input id="q" type="search" placeholder="Search name, club or role…" autocomplete="off">
      <select id="club"><option value="">All clubs</option></select>
    </div>
    <div class="chips" id="leagues"></div>
    <div class="count" id="count"></div>
  </div>
  <div class="grid" id="grid"></div>
  <div class="empty" id="empty" style="display:none">No scouts match your filters.</div>
</div>
<footer>
  Generated __DATE__ · Data via Apify leads-finder + TheSportsDB · Public professional info only (name, role, club, LinkedIn).
</footer>

<script>
const DATA = __DATA__;
const LEAGUES = __LEAGUES__;

let fLeague = "", fClub = "", fQ = "";
const grid = document.getElementById("grid");
const empty = document.getElementById("empty");
const countEl = document.getElementById("count");

// chips de liga
const chipsEl = document.getElementById("leagues");
["All", ...LEAGUES].forEach(l => {
  const c = document.createElement("div");
  c.className = "chip" + (l === "All" ? " active" : "");
  c.textContent = l;
  c.onclick = () => {
    fLeague = l === "All" ? "" : l;
    [...chipsEl.children].forEach(x => x.classList.toggle("active", x.textContent === l));
    fillClubs(); render();
  };
  chipsEl.appendChild(c);
});

const clubSel = document.getElementById("club");
function fillClubs(){
  const pool = DATA.filter(d => !fLeague || d.league === fLeague);
  const clubs = [...new Set(pool.map(d => d.club).filter(Boolean))].sort();
  clubSel.innerHTML = '<option value="">All clubs</option>' +
    clubs.map(c => `<option value="${c.replace(/"/g,'&quot;')}">${c}</option>`).join("");
  fClub = "";
}

document.getElementById("q").addEventListener("input", e => { fQ = e.target.value.toLowerCase().trim(); render(); });
clubSel.addEventListener("change", e => { fClub = e.target.value; render(); });

function esc(s){ return (s||"").replace(/[&<>"]/g, m => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[m])); }

function card(d){
  const init = (d.name||"?").trim().charAt(0).toUpperCase();
  const avatar = d.image
    ? `<img class="avatar" src="${esc(d.image)}" loading="lazy" onerror="this.replaceWith(Object.assign(document.createElement('div'),{className:'avatar',style:'display:flex;align-items:center;justify-content:center;font-weight:700',textContent:'${init}'}))">`
    : `<div class="avatar" style="display:flex;align-items:center;justify-content:center;font-weight:700">${init}</div>`;
  const badge = d.badge ? `<img src="${esc(d.badge)}" loading="lazy">` : "";
  const loc = [d.city, d.country].filter(Boolean).join(", ");
  const li = d.linkedin
    ? `<a class="li-btn" href="${esc(d.linkedin)}" target="_blank" rel="noopener">in · View LinkedIn</a>`
    : `<span class="li-btn off">No LinkedIn</span>`;
  return `<div class="card">
    <div class="top">${avatar}
      <div class="who">
        <div class="name">${esc(d.name)}</div>
        <div class="title">${esc(d.title)}</div>
      </div>
    </div>
    <div class="club">${badge}<div><div>${esc(d.club)}</div>
      <div class="league-tag">${esc(d.league)}</div></div></div>
    ${loc ? `<div class="loc">📍 ${esc(loc)}</div>` : ""}
    ${li}
  </div>`;
}

function render(){
  const list = DATA.filter(d => {
    if (fLeague && d.league !== fLeague) return false;
    if (fClub && d.club !== fClub) return false;
    if (fQ){
      const hay = (d.name+" "+d.club+" "+d.title+" "+d.league).toLowerCase();
      if (!hay.includes(fQ)) return false;
    }
    return true;
  });
  countEl.textContent = `${list.length} of ${DATA.length} profiles`;
  empty.style.display = list.length ? "none" : "block";
  grid.innerHTML = list.map(card).join("");
}

fillClubs();
render();
</script>
</body>
</html>
"""


def _norm_domain(d):
    if not d:
        return ""
    d = str(d).strip().lower().split("://", 1)[-1].split("/", 1)[0]
    return d[4:] if d.startswith("www.") else d


def normalize_clubs(scouts):
    """Unifica nome/ liga/ badge do clube pelo domínio (fontes Apify+Apollo usam
    nomes diferentes pro mesmo time). Auto-corrige a cada build."""
    teams_path = os.path.join(ROOT, "data", "teams.json")
    if not os.path.exists(teams_path):
        return scouts
    with open(teams_path, encoding="utf-8") as f:
        teams = json.load(f)
    dom2 = {_norm_domain(t["domain"]): t for t in teams}
    for r in scouts:
        t = dom2.get(_norm_domain(r.get("club_domain")))
        if t:
            r["club"] = t["name"]
            r["league"] = t["league"]
            if not r.get("badge"):
                r["badge"] = t.get("badge", "")
    return scouts


def main():
    with open(PUB, encoding="utf-8") as f:
        scouts = json.load(f)
    scouts = normalize_clubs(scouts)
    clubs = len({s["club"] for s in scouts if s.get("club")})
    leagues = [l for l in config.LEAGUES if any(s["league"] == l for s in scouts)]

    html = (PAGE
            .replace("__DATA__", json.dumps(scouts, ensure_ascii=False))
            .replace("__LEAGUES__", json.dumps(leagues, ensure_ascii=False))
            .replace("__TOTAL__", str(len(scouts)))
            .replace("__CLUBS__", str(clubs))
            .replace("__DATE__", datetime.date.today().isoformat()))

    os.makedirs(SITE_DIR, exist_ok=True)
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(SITE_DIR, "data.json"), "w", encoding="utf-8") as f:
        json.dump(scouts, f, ensure_ascii=False, indent=2)

    print(f"[site] {len(scouts)} scouts, {clubs} clubes -> {os.path.join(SITE_DIR, 'index.html')}")


if __name__ == "__main__":
    main()
