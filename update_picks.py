import requests
import anthropic
import json
import os

# ── PICKS CONFIG ──────────────────────────────────────────────────────────────
# This is the source of truth for all picks.
# Update this list as the tournament progresses.

PICKS = [
    {"id": "W1", "home": "Lehigh",         "away": "Prairie View A&M", "pick": "Prairie View A&M", "spread": "+3.5", "status": "won",  "final": "67–55", "rlm": "na"},
    {"id": "W2", "home": "SMU",            "away": "Miami (OH)",        "pick": "Miami (OH)",        "spread": "+6.5", "status": "won",  "final": "89–79", "rlm": "na"},
    {"id": "01", "home": "Ohio State",     "away": "TCU",               "pick": "TCU",               "spread": "+2.5", "status": "pending", "final": "", "rlm": "ok"},
    {"id": "02", "home": "Nebraska",       "away": "Troy",              "pick": "Troy",              "spread": "+13.5","status": "pending", "final": "", "rlm": "bad"},
    {"id": "03", "home": "Louisville",     "away": "South Florida",     "pick": "USF",               "spread": "+4.5", "status": "pending", "final": "", "rlm": "bad", "note": "Conditional on Brown"},
    {"id": "04", "home": "Wisconsin",      "away": "High Point",        "pick": "PASS",              "spread": "",     "status": "pass",    "final": "", "rlm": "ok"},
    {"id": "05", "home": "Duke",           "away": "Siena",             "pick": "Siena",             "spread": "+28.5","status": "pending", "final": "", "rlm": "ok"},
    {"id": "06", "home": "Vanderbilt",     "away": "McNeese",           "pick": "Vanderbilt",        "spread": "-11.5","status": "pending", "final": "", "rlm": "no"},
    {"id": "07", "home": "Michigan State", "away": "North Dakota St",   "pick": "Michigan State",    "spread": "-16.5","status": "pending", "final": "", "rlm": "no"},
    {"id": "08", "home": "Arkansas",       "away": "Hawai'i",           "pick": "Hawai'i",           "spread": "+15.5","status": "pending", "final": "", "rlm": "ok"},
    {"id": "09", "home": "UNC",            "away": "VCU",               "pick": "VCU",               "spread": "+2.5", "status": "pending", "final": "", "rlm": "ok"},
    {"id": "10", "home": "Michigan",       "away": "Howard",            "pick": "Howard",            "spread": "+31.5","status": "pending", "final": "", "rlm": "no"},
    {"id": "11", "home": "BYU",            "away": "Texas",             "pick": "Texas",             "spread": "+2.5", "status": "pending", "final": "", "rlm": "no"},
    {"id": "12", "home": "Saint Mary's",   "away": "Texas A&M",         "pick": "PASS",              "spread": "",     "status": "pass",    "final": "", "rlm": "no"},
    {"id": "13", "home": "Illinois",       "away": "Penn",              "pick": "Illinois",          "spread": "-24.5","status": "pending", "final": "", "rlm": "no"},
    {"id": "14", "home": "Georgia",        "away": "Saint Louis",       "pick": "Saint Louis",       "spread": "+2.5", "status": "pending", "final": "", "rlm": "no"},
    {"id": "15", "home": "Gonzaga",        "away": "Kennesaw State",    "pick": "PASS",              "spread": "",     "status": "pass",    "final": "", "rlm": "no"},
    {"id": "16", "home": "Houston",        "away": "Idaho",             "pick": "Houston",           "spread": "-23.5","status": "pending", "final": "", "rlm": "no"},
]

# ── FETCH SCORES ──────────────────────────────────────────────────────────────

def fetch_scores():
    """Fetch live NCAAMB scores from the SportRadar-style endpoint Claude uses."""
    try:
        # Using the same scores source as the conversation
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        games = {}
        for event in data.get("events", []):
            competitors = event["competitions"][0]["competitors"]
            home = next(c for c in competitors if c["homeAway"] == "home")
            away = next(c for c in competitors if c["homeAway"] == "away")
            status = event["status"]["type"]["name"]  # STATUS_FINAL, STATUS_IN_PROGRESS etc
            home_name = home["team"]["displayName"]
            away_name = away["team"]["displayName"]
            home_score = home.get("score", "")
            away_score = away.get("score", "")
            key = f"{away_name} vs {home_name}"
            games[key] = {
                "home": home_name,
                "away": away_name,
                "home_score": home_score,
                "away_score": away_score,
                "status": status,
                "final": f"{away_score}–{home_score}" if home_score else ""
            }
        return games
    except Exception as e:
        print(f"Score fetch error: {e}")
        return {}

# ── RESOLVE PICK STATUS ───────────────────────────────────────────────────────

def resolve_status(pick, games):
    """Check if a pick has a result and update its status."""
    if pick["status"] in ["won", "lost", "pass"]:
        return pick  # already settled

    home = pick["home"]
    away = pick["away"]

    # Try to find the game in fetched scores
    matched = None
    for key, game in games.items():
        if (home.lower() in game["home"].lower() or game["home"].lower() in home.lower()) and \
           (away.lower() in game["away"].lower() or game["away"].lower() in away.lower()):
            matched = game
            break

    if not matched or matched["status"] != "STATUS_FINAL":
        return pick  # game not found or not finished

    # Parse scores
    try:
        home_score = int(matched["home_score"])
        away_score = int(matched["away_score"])
    except:
        return pick

    pick_team = pick["pick"]
    spread = pick["spread"]

    try:
        spread_val = float(spread.replace("+", ""))
    except:
        return pick

    # Determine if pick team is home or away
    if pick_team.lower() in matched["home"].lower() or matched["home"].lower() in pick_team.lower():
        pick_score = home_score
        opp_score = away_score
    else:
        pick_score = away_score
        opp_score = home_score

    # Cover check
    covered = (pick_score + spread_val) > opp_score
    pick["status"] = "won" if covered else "lost"
    pick["final"] = f"{away_score}–{home_score}"
    return pick

# ── BUILD HTML ────────────────────────────────────────────────────────────────

def build_html(picks):
    wins    = sum(1 for p in picks if p["status"] == "won")
    losses  = sum(1 for p in picks if p["status"] == "lost")
    pending = sum(1 for p in picks if p["status"] == "pending")
    passes  = sum(1 for p in picks if p["status"] == "pass")
    rlm_confirmed = sum(1 for p in picks if p.get("rlm") == "ok" and p["status"] != "pass")

    def rlm_badge(rlm, status):
        if status == "pass": return '<div class="rlm no">—</div>'
        if rlm == "na":  return '<div class="rlm na">—</div>'
        if rlm == "ok":  return '<div class="rlm ok">RLM ✓</div>'
        if rlm == "bad": return '<div class="rlm bad">Public ✗</div>'
        return '<div class="rlm no">—</div>'

    def status_badge(p):
        s = p["status"]
        note = p.get("note", "")
        if s == "won":     return '<div class="status won">Won ✓</div>'
        if s == "lost":    return '<div class="status lost">Lost ✗</div>'
        if s == "pass":    return '<div class="status pass">Pass</div>'
        if note:           return '<div class="status cond">Conditional</div>'
        return '<div class="status pending">Pending</div>'

    def pick_col(p):
        if p["pick"] == "PASS":
            return '<div class="pick-col"><span class="pt">—</span></div>'
        return f'<div class="pick-col"><span class="pt">{p["pick"].upper()}</span><span class="ps">{p["spread"]}</span></div>'

    def row_class(p):
        s = p["status"]
        if s == "won":  return "pick won"
        if s == "lost": return "pick lost"
        if s == "pass": return "pick pass"
        return "pick pending"

    def meta(p):
        if p["final"]:
            return f'Final {p["final"]}'
        return ""

    def rows(ids):
        html = ""
        for p in picks:
            if p["id"] not in ids: continue
            m = meta(p)
            html += f"""
  <div class="{row_class(p)}">
    <div class="game-num">{p["id"]}</div>
    <div class="matchup-col">
      <div class="teams">{p["away"]} vs {p["home"]}</div>
      <div class="meta">{m}</div>
    </div>
    {pick_col(p)}
    {rlm_badge(p.get("rlm","no"), p["status"])}
    {status_badge(p)}
  </div>"""
        return html

    from datetime import datetime
    timestamp = datetime.utcnow().strftime("%a %b %-d · %-I:%M %p UTC")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Patrick's March Picks</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg:#080808;--surface:#101010;--surface2:#181818;--border:#1e1e1e;--border2:#282828;
    --green:#00e676;--green-dim:rgba(0,230,118,0.08);--green-border:rgba(0,230,118,0.25);
    --red:#ff4444;--red-dim:rgba(255,68,68,0.08);--red-border:rgba(255,68,68,0.25);
    --yellow:#ffca28;--yellow-dim:rgba(255,202,40,0.07);--yellow-border:rgba(255,202,40,0.2);
    --blue:#40c4ff;--blue-dim:rgba(64,196,255,0.07);--blue-border:rgba(64,196,255,0.2);
    --orange:#ff9800;--muted:#444;--text:#ececec;--text2:#666;--text3:#999;
  }}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;min-height:100vh;padding:40px 28px 60px;max-width:1100px;margin:0 auto}}
  .header{{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:36px;padding-bottom:28px;border-bottom:1px solid var(--border);gap:20px;flex-wrap:wrap}}
  .title-block h1{{font-family:'Bebas Neue',sans-serif;font-size:clamp(52px,9vw,104px);letter-spacing:3px;line-height:0.88}}
  .title-block h1 em{{color:var(--green);font-style:normal}}
  .title-block .subtitle{{font-family:'DM Mono',monospace;font-size:10px;color:var(--text2);letter-spacing:4px;text-transform:uppercase;margin-top:10px}}
  .record-block{{text-align:right;flex-shrink:0}}
  .record-block .record-num{{font-family:'Bebas Neue',sans-serif;font-size:clamp(40px,6vw,72px);letter-spacing:3px;color:var(--green);line-height:1}}
  .record-block .record-sub{{font-family:'DM Mono',monospace;font-size:10px;color:var(--text2);letter-spacing:3px;text-transform:uppercase;margin-top:4px}}
  .stat-strip{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:44px}}
  .stat{{background:var(--surface);border:1px solid var(--border);padding:18px 16px;position:relative;overflow:hidden}}
  .stat::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:2px}}
  .stat.s-green::after{{background:var(--green)}}.stat.s-red::after{{background:var(--red)}}
  .stat.s-yellow::after{{background:var(--yellow)}}.stat.s-blue::after{{background:var(--blue)}}
  .stat.s-orange::after{{background:var(--orange)}}
  .stat .v{{font-family:'Bebas Neue',sans-serif;font-size:38px;line-height:1;letter-spacing:1px}}
  .stat.s-green .v{{color:var(--green)}}.stat.s-red .v{{color:var(--red)}}
  .stat.s-yellow .v{{color:var(--yellow)}}.stat.s-blue .v{{color:var(--blue)}}
  .stat.s-orange .v{{color:var(--orange)}}
  .stat .l{{font-family:'DM Mono',monospace;font-size:9px;color:var(--text2);letter-spacing:2px;text-transform:uppercase;margin-top:5px}}
  .section-label{{display:flex;align-items:center;gap:14px;margin-bottom:12px;margin-top:32px}}
  .section-label span{{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:4px;text-transform:uppercase;color:var(--text2);white-space:nowrap}}
  .section-label::after{{content:'';flex:1;height:1px;background:var(--border)}}
  .picks{{display:flex;flex-direction:column;gap:6px;margin-bottom:8px}}
  .pick{{display:grid;grid-template-columns:40px 1fr 170px 72px 90px;align-items:center;gap:14px;background:var(--surface);border:1px solid var(--border);border-left:3px solid transparent;padding:13px 18px;transition:background 0.12s}}
  .pick:hover{{background:var(--surface2)}}
  .pick.won{{border-left-color:var(--green)}}.pick.lost{{border-left-color:var(--red)}}
  .pick.pending{{border-left-color:var(--border2)}}.pick.pass{{border-left-color:var(--muted);opacity:0.4}}
  .game-num{{font-family:'DM Mono',monospace;font-size:11px;color:var(--muted);text-align:center}}
  .matchup-col .teams{{font-size:13px;font-weight:500;color:var(--text)}}
  .matchup-col .meta{{font-family:'DM Mono',monospace;font-size:10px;color:var(--text2);margin-top:2px}}
  .pick-col{{display:flex;align-items:center;gap:8px;overflow:hidden}}
  .pick-col .pt{{font-family:'DM Mono',monospace;font-size:11px;font-weight:500;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
  .pick-col .ps{{font-family:'DM Mono',monospace;font-size:11px;color:var(--text3);background:var(--surface2);border:1px solid var(--border2);padding:1px 7px;white-space:nowrap;flex-shrink:0}}
  .rlm{{font-family:'DM Mono',monospace;font-size:10px;text-align:center;padding:4px 6px;border:1px solid transparent;white-space:nowrap}}
  .rlm.ok{{color:var(--green);background:var(--green-dim);border-color:var(--green-border)}}
  .rlm.no{{color:var(--muted);background:transparent;border-color:var(--border)}}
  .rlm.bad{{color:var(--red);background:var(--red-dim);border-color:var(--red-border)}}
  .rlm.na{{color:var(--muted);border-color:transparent;font-size:9px}}
  .status{{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1px;text-transform:uppercase;padding:4px 8px;text-align:center;white-space:nowrap}}
  .status.won{{background:var(--green-dim);color:var(--green);border:1px solid var(--green-border)}}
  .status.lost{{background:var(--red-dim);color:var(--red);border:1px solid var(--red-border)}}
  .status.pending{{background:var(--yellow-dim);color:var(--yellow);border:1px solid var(--yellow-border)}}
  .status.pass{{background:transparent;color:var(--muted);border:1px solid var(--border)}}
  .status.cond{{background:var(--blue-dim);color:var(--blue);border:1px solid var(--blue-border);font-size:8px}}
  .legend{{display:flex;align-items:center;gap:20px;margin-top:32px;padding-top:20px;border-top:1px solid var(--border);flex-wrap:wrap}}
  .legend-title{{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:var(--muted)}}
  .legend-item{{display:flex;align-items:center;gap:7px}}
  .legend-dot{{width:28px;height:18px;font-family:'DM Mono',monospace;font-size:10px;display:flex;align-items:center;justify-content:center;border:1px solid}}
  .legend-dot.ok{{background:var(--green-dim);color:var(--green);border-color:var(--green-border)}}
  .legend-dot.no{{background:transparent;color:var(--muted);border-color:var(--border)}}
  .legend-dot.bad{{background:var(--red-dim);color:var(--red);border-color:var(--red-border)}}
  .legend-text{{font-family:'DM Mono',monospace;font-size:9px;color:var(--text2)}}
  .footer{{margin-top:24px;font-family:'DM Mono',monospace;font-size:9px;color:var(--muted);text-align:center;letter-spacing:3px;text-transform:uppercase}}
  .timestamp{{margin-top:8px;font-size:9px;color:#333;letter-spacing:2px}}
</style>
</head>
<body>

<div class="header">
  <div class="title-block">
    <h1>PATRICK'S<br><em>MARCH</em><br>PICKS</h1>
    <div class="subtitle">NCAA Tournament 2026 · First Round Tracker</div>
  </div>
  <div class="record-block">
    <div class="record-num">{wins}—{losses}</div>
    <div class="record-sub">Overall ATS</div>
  </div>
</div>

<div class="stat-strip">
  <div class="stat s-green"><div class="v">{wins}</div><div class="l">Wins</div></div>
  <div class="stat s-red"><div class="v">{losses}</div><div class="l">Losses</div></div>
  <div class="stat s-yellow"><div class="v">{pending}</div><div class="l">Pending</div></div>
  <div class="stat s-blue"><div class="v">{passes}</div><div class="l">Passes</div></div>
  <div class="stat s-orange"><div class="v">{rlm_confirmed}</div><div class="l">RLM ✓</div></div>
</div>

<div class="section-label"><span>Wednesday · First Four</span></div>
<div class="picks">{rows(["W1","W2"])}</div>

<div class="section-label"><span>Thursday · Morning</span></div>
<div class="picks">{rows(["01","02","03","04","05","06","07","08"])}</div>

<div class="section-label"><span>Thursday · Evening</span></div>
<div class="picks">{rows(["09","10","11","12","13","14","15","16"])}</div>

<div class="legend">
  <div class="legend-title">RLM Key</div>
  <div class="legend-item"><div class="legend-dot ok">✓</div><div class="legend-text">Sharp money confirms pick</div></div>
  <div class="legend-item"><div class="legend-dot no">—</div><div class="legend-text">No clear signal</div></div>
  <div class="legend-item"><div class="legend-dot bad">✗</div><div class="legend-text">Public on our side (no RLM edge)</div></div>
</div>

<div class="footer">
  Patrick's March Picks · NCAA 2026 · For Entertainment Purposes Only
  <div class="timestamp">LAST UPDATED · {timestamp}</div>
</div>

</body>
</html>"""

# ── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Fetching scores...")
    games = fetch_scores()

    print("Resolving pick statuses...")
    updated_picks = [resolve_status(p, games) for p in PICKS]

    print("Building HTML...")
    html = build_html(updated_picks)

    with open("index.html", "w") as f:
        f.write(html)

    print("Done — index.html updated.")
