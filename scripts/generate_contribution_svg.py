"""Generate dark animated profile assets from GitHub contribution data."""
from __future__ import annotations

import json, os, urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
USER = "ToshitSai"

def graphql_calendar() -> list[dict]:
    query = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""
    body = json.dumps({"query": query, "variables": {"login": USER}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={"Content-Type":"application/json", "Authorization":f"bearer {os.environ.get('GITHUB_TOKEN','')}"})
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.load(response)
    return [day for week in data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"] for day in week["contributionDays"]]

def fallback_calendar() -> list[dict]:
    # Keeps local generation useful before the workflow supplies GITHUB_TOKEN.
    return [{"date":"", "contributionCount":0} for _ in range(371)]

def contribution_svg(days: list[dict]) -> str:
    counts = [int(d.get("contributionCount", 0)) for d in days][-371:]
    counts = [0] * (371-len(counts)) + counts
    months = "Jan   Feb   Mar   Apr   May   Jun   Jul   Aug   Sep   Oct   Nov   Dec"
    cells = []
    for i, count in enumerate(counts):
        col, row = i // 7, i % 7
        level = 0 if count == 0 else min(4, 1 + count // 4)
        color = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"][level]
        delay = (col * 0.045) + (row * 0.012)
        cells.append(f'<rect x="{72+col*14}" y="{42+row*14}" width="10" height="10" rx="2" fill="{color}" opacity=".9"><animate attributeName="opacity" values=".45;1;.45" dur="2.8s" begin="-{delay:.2f}s" repeatCount="indefinite"/></rect>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="178" viewBox="0 0 760 178"><rect width="760" height="178" rx="18" fill="#0d1117" stroke="#30363d"/><text x="72" y="24" fill="#8b949e" font-family="ui-monospace,monospace" font-size="11">{months}</text><text x="18" y="63" fill="#8b949e" font-family="ui-monospace,monospace" font-size="10">Mon</text><text x="18" y="105" fill="#8b949e" font-family="ui-monospace,monospace" font-size="10">Wed</text><text x="18" y="147" fill="#8b949e" font-family="ui-monospace,monospace" font-size="10">Fri</text>{''.join(cells)}<text x="72" y="170" fill="#39d353" font-family="ui-monospace,monospace" font-size="10">CONTRIBUTION ANIMATION // LIVE DATA</text></svg>'''

def terminal_card() -> str:
    avatar = ROOT / "assets" / "avatar.jpg"
    try:
        img = Image.open(avatar).convert("L").resize((42, 18))
        chars = " .:-=+*#%@"
        lines = ["".join(chars[img.getpixel((x, y))*len(chars)//256] for x in range(img.width)) for y in range(img.height)]
    except Exception:
        lines = ["ASCII PORTRAIT TODO", "Avatar download unavailable"]
    text = "\n".join(lines)
    esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="370" height="300"><rect width="370" height="300" rx="16" fill="#111827" stroke="#374151"/><circle cx="22" cy="22" r="6" fill="#ff5f56"/><circle cx="42" cy="22" r="6" fill="#ffbd2e"/><circle cx="62" cy="22" r="6" fill="#27c93f"/><text x="22" y="52" fill="#9ca3af" font-family="monospace" font-size="12">toshitsai@github:~$ whoami</text><text x="22" y="75" fill="#39d353" font-family="monospace" font-size="9">{esc.replace(chr(10), '</text><text x="22" y="'+str(75+10)+'" fill="#39d353" font-family="monospace" font-size="9">')}</text><text x="22" y="270" fill="#60a5fa" font-family="monospace" font-size="12">toshitsai@github:~$ <tspan fill="#f9fafb">neofetch</tspan><tspan fill="#39d353"> ▮</tspan></text></svg>'''

def info_card() -> str:
    lines = ["ToshitSai @ github", "────────────────────────", "Role       AI Product Developer", "Focus      Prompt Engineering", "College    NIAT Student", "", "— Stack —", "Frontend   React", "Backend    Node.js", "Language   JavaScript / TypeScript / Python", "AI         Prompt Engineering / AI products", "", "— Highlights —", "● CourseForge AI", "● Greetly", "● Cinematic Avengers experience"]
    spans = []
    for i, line in enumerate(lines):
        color = "#60a5fa" if line.startswith("—") else "#fb923c" if any(line.startswith(k) for k in ("Role", "Focus", "College")) else "#39d353" if line.startswith("●") else "#d1d5db"
        spans.append(f'<tspan x="20" dy="{20 if i else 0}" fill="{color}">{line}</tspan>')
    tspans = "".join(spans)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="370" height="300"><rect width="370" height="300" rx="16" fill="#111827" stroke="#374151"/><text x="20" y="28" fill="#f9fafb" font-family="monospace" font-size="12">ToshitSai@github:~$ neofetch</text><text x="20" y="54" font-family="monospace" font-size="11">{tspans}</text></svg>'''

def main() -> None:
    try: days = graphql_calendar()
    except Exception: days = fallback_calendar()
    (ASSETS / "github-contribution-animation.svg").write_text(contribution_svg(days), encoding="utf-8")
    (ASSETS / "terminal-card.svg").write_text(terminal_card(), encoding="utf-8")
    (ASSETS / "info-card.svg").write_text(info_card(), encoding="utf-8")

if __name__ == "__main__": main()
