import requests
import json
import os
from datetime import datetime

# ── PICKS CONFIG ──────────────────────────────────────────────────────────────

PICKS = [
    # WEDNESDAY - FIRST FOUR
    {"id": "W1", "home": "Lehigh",         "away": "Prairie View A&M", "pick": "Prairie View A&M", "spread": "+3.5",  "status": "won",     "final": "67-55", "rlm": "na",  "day": "Wed Mar 18"},
    {"id": "W2", "home": "SMU",            "away": "Miami (OH)",        "pick": "Miami (OH)",        "spread": "+6.5",  "status": "won",     "final": "89-79", "rlm": "na",  "day": "Wed Mar 18"},

    # THURSDAY
    {"id": "01", "home": "Ohio State",     "away": "TCU",               "pick": "TCU",               "spread": "+2.5",  "status": "won",     "final": "66-64", "rlm": "ok",  "day": "Thu Mar 19"},
    {"id": "02", "home": "Nebraska",       "away": "Troy",              "pick": "Troy",              "spread": "+13.5", "status": "lost",    "final": "47-76", "rlm": "bad", "day": "Thu Mar 19"},
    {"id": "03", "home": "Louisville",     "away": "South Florida",     "pick": "South Florida",     "spread": "+4.5",  "status": "won",     "final": "79-83", "rlm": "bad", "day": "Thu Mar 19"},
    {"id": "04", "home": "Wisconsin",      "away": "High Point",        "pick": "PASS",              "spread": "",      "status": "pass",    "final": "",      "rlm": "ok",  "day": "Thu Mar 19"},
    {"id": "05", "home": "Duke",           "away": "Siena",             "pick": "Siena",             "spread": "+28.5", "status": "won",     "final": "65-71", "rlm": "ok",  "day": "Thu Mar 19"},
    {"id": "06", "home": "Vanderbilt",     "away": "McNeese",           "pick": "Vanderbilt",        "spread": "-11.5", "status": "lost",    "final": "78-68", "rlm": "no",  "day": "Thu Mar 19"},
    {"id": "07", "home": "Michigan State", "away": "North Dakota St",   "pick": "Michigan State",    "spread": "-16.5", "status": "won",     "final": "92-67", "rlm": "no",  "day": "Thu Mar 19"},
    {"id": "08", "home": "Arkansas",       "away": "Hawai'i",           "pick": "Hawai'i",           "spread": "+15.5", "status": "lost",    "final": "78-97", "rlm": "ok",  "day": "Thu Mar 19"},
    {"id": "09", "home": "UNC",            "away": "VCU",               "pick": "VCU",               "spread": "+2.5",  "status": "won",     "final": "82-78", "rlm": "ok",  "day": "Thu Mar 19"},
    {"id": "10", "home": "Michigan",       "away": "Howard",            "pick": "Howard",            "spread": "+31.5", "status": "won",     "final": "80-101","rlm": "no",  "day": "Thu Mar 19"},
    {"id": "11", "home": "BYU",            "away": "Texas",             "pick": "Texas",             "spread": "+2.5",  "status": "won",     "final": "79-71", "rlm": "no",  "day": "Thu Mar 19"},
    {"id": "12", "home": "Saint Mary's",   "away": "Texas A&M",         "pick": "PASS",              "spread": "",      "status": "pass",    "final": "",      "rlm": "no",  "day": "Thu Mar 19"},
    {"id": "13", "home": "Illinois",       "away": "Penn",              "pick": "Illinois",          "spread": "-24.5", "status": "won",     "final": "105-70","rlm": "no",  "day": "Thu Mar 19"},
    {"id": "14", "home": "Georgia",        "away": "Saint Louis",       "pick": "Saint Louis",       "spread": "+2.5",  "status": "won",     "final": "102-77","rlm": "no",  "day": "Thu Mar 19"},
    {"id": "15", "home": "Gonzaga",        "away": "Kennesaw State",    "pick": "PASS",              "spread": "",      "status": "pass",    "final": "",      "rlm": "no",  "day": "Thu Mar 19"},
    {"id": "16", "home": "Houston",        "away": "Idaho",             "pick": "Houston",           "spread": "-23.5", "status": "pending", "final": "",      "rlm": "no",  "day": "Thu Mar 19"},

    # FRIDAY
    {"id": "F1",  "home": "Kentucky",      "away": "Santa Clara",       "pick": "Santa Clara",       "spread": "+3.5",  "status": "pending", "final": "",      "rlm": "bad", "day": "Fri Mar 20"},
    {"id": "F2",  "home": "Texas Tech",    "away": "Akron",             "pick": "Akron",             "spread": "+7.5",  "status": "pending", "final": "",      "rlm": "ok",  "day": "Fri Mar 20"},
    {"id": "F3",  "home": "Arizona",       "away": "LIU",               "pick": "LIU",               "spread": "+29.5", "status": "pending", "final": "",      "rlm": "ok",  "day": "Fri Mar 20"},
    {"id": "F4",  "home": "Virginia",      "away": "Wright State",      "pick": "PASS",              "spread": "",      "status": "pass",    "final": "",      "rlm": "no",  "day": "Fri Mar 20"},
    {"id": "F5",  "home": "Iowa State",    "away": "Tennessee State",   "pick": "PASS",              "spread": "",      "status": "pass",    "final": "",      "rlm": "no",  "day": "Fri Mar 20"},
    {"id": "F6",  "home": "Alabama",       "away": "Hofstra",           "pick": "Hofstra",           "spread": "+12.5", "status": "pending", "final": "",      "rlm": "no",  "day": "Fri Mar 20"},
    {"id": "F7",  "home": "Villanova",     "away": "Utah State",        "pick": "PASS",              "spread": "",      "status": "pass",    "final": "",      "rlm": "no",  "day": "Fri Mar 20"},
    {"id": "F8",  "home": "Tennessee",     "away": "Miami (OH)",        "pick": "Miami (OH)",        "spread": "+6.5",  "status": "pending", "final": "",      "rlm": "no",  "day": "Fri Mar 20"},
    {"id": "F9",  "home": "Clemson",       "away": "Iowa",              "pick": "Iowa",              "spread": "-2.5",  "status": "pending", "final": "",      "rlm": "ok",  "day": "Fri Mar 20"},
    {"id": "F10", "home": "St. John's",    "away": "Northern Iowa",     "pick": "Northern Iowa",     "spread": "+10.5", "status": "pending", "final": "",      "rlm": "ok",  "day": "Fri Mar 20"},
    {"id": "F11", "home": "UCLA",          "away": "UCF",               "pick": "PASS",              "spread": "",      "status": "pass",    "final": "",      "rlm": "no",  "day": "Fri Mar 20"},
    {"id": "F12", "home": "Purdue",        "away": "Queens",            "pick": "Purdue",            "spread": "-23.5", "status": "pending", "final": "",      "rlm": "ok",  "day": "Fri Mar 20"},
    {"id": "F13", "home": "Florida",       "away": "Prairie View A&M",  "pick": "PASS",              "spread": "",      "status": "pass",    "final": "",      "rlm": "na",  "day": "Fri Mar 20"},
    {"id": "F14", "home": "Kansas",        "away": "Cal Baptist",       "pick": "PASS",              "spread": "",      "status": "pass",    "final": "",      "rlm": "no",  "day": "Fri Mar 20"},
]

# ── FETCH SCORES ──────────────────────────────────────────────────────────────

def fetch_scores():
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        games = {}
        for event in data.get("events", []):
            competitors = event["competitions"][0]["competitors"]
            home = next(c for c in competitors if c["homeAway"] == "home")
            away = next(c for c in competitors if c["homeAway"] == "away")
            status = event["status"]["type"]["name"]
            home_name = home["team"]["displayName"]
            away_name = away["team"]["displayName"]
            home_score = home.get("score", "")
            away_score = away.get("score", "")
            games[f"{away_name} vs {home_name}"] = {
                "home": home_name, "away": away_name,
                "home_score": home_score, "away_score": away_score,
                "status": status,
            }
        return games
    except Exception as e:
        print(f"Score fetch error: {e}")
        return {}

# ── RESOLVE PICK STATUS ───────────────────────────────────────────────────────

def resolve_status(pick, games):
    if pick["status"] in ["won", "lost", "pass"]:
        return pick
    for key, game in games.items():
        home_match = pick["home"].lower() in game["home"].lower() or game["home"].lower() in pick["home"].lower()
        away_match = pick["away"].lower() in game["away"].lower() or game["away"].lower() in pick["away"].lower()
        if home_match and away_match and game["status"] == "STATUS_FINAL":
            try:
                home_score = int(game["home_score"])
                away_score = int(game["away_score"])
            except:
                return pick
            pick_team = pick["pick"]
            try:
                spread_val = float(pick["spread"].replace("+", ""))
            except:
                return pick
            if pick_team.lower() in game["home"].lower() or game["home"].lower() in pick_team.lower():
                covered = (home_score + spread_val) > away_score
            else:
                covered = (away_score + spread_val) > home_score
            pick["status"] = "won" if covered else "lost"
            pick["final"] = f"{away_score}-{home_score}"
            return pick
    return pick

# ── BUILD HTML ────────────────────────────────────────────────────────────────

def build_html(picks):
    wins    = sum(1 for p in picks if p["status"] == "won")
    losses  = sum(1 for p in picks if p["status"] == "lost")
    pending = sum(1 for p in picks if p["status"] == "pending")
    passes  = sum(1 for p in picks if p["status"] == "pass")
    rlm_ct  = sum(1 for p in picks if p.get("rlm") == "ok" and p["status"] != "pass")
    timestamp = datetime.utcnow().strftime("%a %b %-d · %-I:%M %p UTC")

    # Group picks by day
    days_order = ["Wed Mar 18", "Thu Mar 19", "Fri Mar 20"]
    days_label = {
        "Wed Mar 18": "Wednesday · First Four",
        "Thu Mar 19": "Thursday · Round 1",
        "Fri Mar 20": "Friday · Round 1",
    }
    today = datetime.utcnow().strftime("%a %b %-d")
    # Map today to our day keys
    active_day = "Fri Mar 20"  # default to Friday since that's current
    for d in days_order:
        if d == today:
            active_day = d
            break

    def rlm_badge(rlm, status):
        if status == "pass": return '<div class="rlm no">—</div>'
        if rlm == "na":  return '<div class="rlm na">—</div>'
        if rlm == "ok":  return '<div class="rlm ok">RLM ✓</div>'
        if rlm == "bad": return '<div class="rlm bad">Public ✗</div>'
        return '<div class="rlm no">—</div>'

    def status_badge(p):
        s = p["status"]
        if s == "won":  return '<div class="status won">Won ✓</div>'
        if s == "lost": return '<div class="status lost">Lost ✗</div>'
        if s == "pass": return '<div class="status pass">Pass</div>'
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

    def day_record(day_picks):
        w = sum(1 for p in day_picks if p["status"] == "won")
        l = sum(1 for p in day_picks if p["status"] == "lost")
        return f"{w}–{l}"

    def tab_content(day):
        day_picks = [p for p in picks if p["day"] == day]
        rows = ""
        for p in day_picks:
            final_text = f"Final {p['final']}" if p.get("final") else ""
            rows += f"""
        <div class="{row_class(p)}">
          <div class="game-num">{p["id"]}</div>
          <div class="matchup-col">
            <div class="teams">{p["away"]} vs {p["home"]}</div>
            <div class="meta">{final_text}</div>
          </div>
          {pick_col(p)}
          {rlm_badge(p.get("rlm","no"), p["status"])}
          {status_badge(p)}
        </div>"""
        return rows

    # Build tabs
    tabs_nav = ""
    tabs_content = ""
    for i, day in enumerate(days_order):
        day_picks = [p for p in picks if p["day"] == day]
        rec = day_record(day_picks)
        is_active = day == active_day
        active_class = "active" if is_active else ""
        has_pending = any(p["status"] == "pending" for p in day_picks)
        dot = '<span class="live-dot"></span>' if has_pending else ""
        tabs_nav += f'<button class="tab-btn {active_class}" onclick="switchTab(\'{day}\')" id="btn-{day.replace(" ","-")}">{dot}{days_label[day]}<span class="tab-rec">{rec}</span></button>'
        display = "block" if is_active else "none"
        tabs_content += f'<div class="tab-panel" id="panel-{day.replace(" ","-")}" style="display:{display}">{tab_content(day)}</div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Patrick's March Picks</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root{{--bg:#080808;--surface:#101010;--surface2:#181818;--border:#1e1e1e;--border2:#282828;--green:#00e676;--green-dim:rgba(0,230,118,0.08);--green-border:rgba(0,230,118,0.25);--red:#ff4444;--red-dim:rgba(255,68,68,0.08);--red-border:rgba(255,68,68,0.25);--yellow:#ffca28;--yellow-dim:rgba(255,202,40,0.07);--yellow-border:rgba(255,202,40,0.2);--blue:#40c4ff;--blue-dim:rgba(64,196,255,0.07);--blue-border:rgba(64,196,255,0.2);--orange:#ff9800;--muted:#444;--text:#ececec;--text2:#666;--text3:#999;}}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;min-height:100vh;padding:40px 28px 60px;max-width:1100px;margin:0 auto}}
  .header{{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:36px;padding-bottom:28px;border-bottom:1px solid var(--border);gap:20px;flex-wrap:wrap}}
  .title-block h1{{font-family:'Bebas Neue',sans-serif;font-size:clamp(52px,9vw,104px);letter-spacing:3px;line-height:0.88}}
  .title-block h1 em{{color:var(--green);font-style:normal}}
  .title-block .subtitle{{font-family:'DM Mono',monospace;font-size:10px;color:var(--text2);letter-spacing:4px;text-transform:uppercase;margin-top:10px}}
  .record-block{{text-align:right;flex-shrink:0}}
  .record-block .record-num{{font-family:'Bebas Neue',sans-serif;font-size:clamp(40px,6vw,72px);letter-spacing:3px;color:var(--green);line-height:1}}
  .record-block .record-sub{{font-family:'DM Mono',monospace;font-size:10px;color:var(--text2);letter-spacing:3px;text-transform:uppercase;margin-top:4px}}
  .stat-strip{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:32px}}
  .stat{{background:var(--surface);border:1px solid var(--border);padding:18px 16px;position:relative;overflow:hidden}}
  .stat::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:2px}}
  .stat.s-green::after{{background:var(--green)}}.stat.s-red::after{{background:var(--red)}}.stat.s-yellow::after{{background:var(--yellow)}}.stat.s-blue::after{{background:var(--blue)}}.stat.s-orange::after{{background:var(--orange)}}
  .stat .v{{font-family:'Bebas Neue',sans-serif;font-size:38px;line-height:1;letter-spacing:1px}}
  .stat.s-green .v{{color:var(--green)}}.stat.s-red .v{{color:var(--red)}}.stat.s-yellow .v{{color:var(--yellow)}}.stat.s-blue .v{{color:var(--blue)}}.stat.s-orange .v{{color:var(--orange)}}
  .stat .l{{font-family:'DM Mono',monospace;font-size:9px;color:var(--text2);letter-spacing:2px;text-transform:uppercase;margin-top:5px}}

  /* TABS */
  .tabs-nav{{display:flex;gap:4px;margin-bottom:0;border-bottom:1px solid var(--border);overflow-x:auto}}
  .tab-btn{{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--text2);background:transparent;border:none;border-bottom:2px solid transparent;padding:12px 20px;cursor:pointer;white-space:nowrap;display:flex;align-items:center;gap:8px;transition:color 0.15s,border-color 0.15s;margin-bottom:-1px}}
  .tab-btn:hover{{color:var(--text)}}
  .tab-btn.active{{color:var(--green);border-bottom-color:var(--green)}}
  .tab-rec{{font-family:'DM Mono',monospace;font-size:9px;color:var(--muted);margin-left:6px}}
  .tab-btn.active .tab-rec{{color:var(--green);opacity:0.7}}

  /* LIVE DOT */
  .live-dot{{width:6px;height:6px;border-radius:50%;background:var(--yellow);animation:pulse 1.5s infinite}}
  @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}

  /* PICKS */
  .tab-panel{{padding-top:20px}}
  .picks{{display:flex;flex-direction:column;gap:6px;margin-bottom:8px}}
  .pick{{display:grid;grid-template-columns:40px 1fr 170px 72px 90px;align-items:center;gap:14px;background:var(--surface);border:1px solid var(--border);border-left:3px solid transparent;padding:13px 18px;transition:background 0.12s}}
  .pick:hover{{background:var(--surface2)}}
  .pick.won{{border-left-color:var(--green)}}.pick.lost{{border-left-color:var(--red)}}.pick.pending{{border-left-color:var(--border2)}}.pick.pass{{border-left-color:var(--muted);opacity:0.4}}
  .game-num{{font-family:'DM Mono',monospace;font-size:11px;color:var(--muted);text-align:center}}
  .matchup-col .teams{{font-size:13px;font-weight:500;color:var(--text)}}
  .matchup-col .meta{{font-family:'DM Mono',monospace;font-size:10px;color:var(--text2);margin-top:2px}}
  .pick-col{{display:flex;align-items:center;gap:8px;overflow:hidden}}
  .pick-col .pt{{font-family:'DM Mono',monospace;font-size:11px;font-weight:500;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
  .pick-col .ps{{font-family:'DM Mono',monospace;font-size:11px;color:var(--text3);background:var(--surface2);border:1px solid var(--border2);padding:1px 7px;white-space:nowrap;flex-shrink:0}}
  .rlm{{font-family:'DM Mono',monospace;font-size:10px;text-align:center;padding:4px 6px;border:1px solid transparent;white-space:nowrap}}
  .rlm.ok{{color:var(--green);background:var(--green-dim);border-color:var(--green-border)}}.rlm.no{{color:var(--muted);background:transparent;border-color:var(--border)}}.rlm.bad{{color:var(--red);background:var(--red-dim);border-color:var(--red-border)}}.rlm.na{{color:var(--muted);border-color:transparent;font-size:9px}}
  .status{{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1px;text-transform:uppercase;padding:4px 8px;text-align:center;white-space:nowrap}}
  .status.won{{background:var(--green-dim);color:var(--green);border:1px solid var(--green-border)}}.status.lost{{background:var(--red-dim);color:var(--red);border:1px solid var(--red-border)}}.status.pending{{background:var(--yellow-dim);color:var(--yellow);border:1px solid var(--yellow-border)}}.status.pass{{background:transparent;color:var(--muted);border:1px solid var(--border)}}
  .legend{{display:flex;align-items:center;gap:20px;margin-top:32px;padding-top:20px;border-top:1px solid var(--border);flex-wrap:wrap}}
  .legend-title{{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:var(--muted)}}
  .legend-item{{display:flex;align-items:center;gap:7px}}
  .legend-dot{{width:28px;height:18px;font-family:'DM Mono',monospace;font-size:10px;display:flex;align-items:center;justify-content:center;border:1px solid}}
  .legend-dot.ok{{background:var(--green-dim);color:var(--green);border-color:var(--green-border)}}.legend-dot.no{{background:transparent;color:var(--muted);border-color:var(--border)}}.legend-dot.bad{{background:var(--red-dim);color:var(--red);border-color:var(--red-border)}}
  .legend-text{{font-family:'DM Mono',monospace;font-size:9px;color:var(--text2)}}
  .footer{{margin-top:24px;font-family:'DM Mono',monospace;font-size:9px;color:var(--muted);text-align:center;letter-spacing:3px;text-transform:uppercase}}
  .timestamp{{margin-top:8px;font-size:9px;color:#333;letter-spacing:2px}}
  @media(max-width:680px){{.stat-strip{{grid-template-columns:repeat(3,1fr)}}.pick{{grid-template-columns:1fr 90px;grid-template-rows:auto auto;gap:8px 10px;padding:12px 14px}}.game-num{{display:none}}.matchup-col{{grid-column:1;grid-row:1}}.pick-col{{grid-column:1;grid-row:2;display:flex}}.rlm{{display:none}}.status{{grid-column:2;grid-row:1 / 3;align-self:center;font-size:8px;padding:6px}}.matchup-col .teams{{font-size:12px}}}}
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
  <div class="stat s-orange"><div class="v">{rlm_ct}</div><div class="l">RLM ✓</div></div>
</div>

<div class="tabs-nav">{tabs_nav}</div>
<div class="picks">{tabs_content}</div>

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
<script>
function switchTab(day) {{
  document.querySelectorAll('.tab-panel').forEach(p => p.style.display = 'none');
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('panel-' + day.replace(/ /g,'-')).style.display = 'block';
  document.getElementById('btn-' + day.replace(/ /g,'-')).classList.add('active');
}}
</script>
</body>
</html>"""

# ── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Fetching scores...")
    games = fetch_scores()
    print(f"Found {len(games)} games")
    print("Resolving picks...")
    updated = [resolve_status(p, games) for p in PICKS]
    print("Building HTML...")
    html = build_html(updated)
    with open("index.html", "w") as f:
        f.write(html)
    print("Done.")
