from __future__ import annotations
import datetime as dt, json, os, urllib.request
from pathlib import Path
from xml.sax.saxutils import escape
from PIL import Image, ImageOps, ImageEnhance
ROOT=Path(__file__).resolve().parents[1]; ASSETS=ROOT/'assets'; FONT="'Fira Code','JetBrains Mono',Consolas,monospace"
def data():
 q='query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){contributionsCollection(from:$from,to:$to){contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'; body=json.dumps({'query':q,'variables':{'login':'ToshitSai','from':'2026-01-01T00:00:00Z','to':'2026-12-31T23:59:59Z'}}).encode(); req=urllib.request.Request('https://api.github.com/graphql',data=body,headers={'Content-Type':'application/json','Authorization':f'bearer {os.environ.get("GITHUB_TOKEN","")}'})
 with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)['data']['user']['contributionsCollection']
def contribution(d):
 first=dt.date(2026,1,1); first-=dt.timedelta(days=(first.weekday()+1)%7); ds={dt.date.fromisoformat(x['date']):int(x['contributionCount']) for w in d.get('weeks',[]) for x in w['contributionDays']}; cs=['#161b22','#0e4429','#006d32','#26a641','#39d353']; cells=[]
 for c in range(53):
  for r in range(7):
   day=first+dt.timedelta(days=c*7+r); n=ds.get(day,0) if day.year==2026 and day<=dt.date.today() else 0; x,y=64+c*14,42+r*14; delay=c*.055; cells.append(f'<rect x="{x}" y="{y}" width="11" height="11" rx="2" fill="{cs[min(4,1+n//4) if n else 0]}" opacity="{.28 if day>dt.date.today() else .9}"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.12;.82;1" dur="8s" begin="{delay:.3f}s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="scale" values=".82 .82;1 1;1 1;.82 .82" keyTimes="0;.12;.82;1" dur="8s" begin="{delay:.3f}s" repeatCount="indefinite"/></rect>')
 labels=''.join(f'<text x="{64+((dt.date(2026,m,1)-first).days//7)*14}" y="25" fill="#8b949e" font-family="{FONT}" font-size="11">{dt.date(2026,m,1):%b}</text>' for m in range(1,13)); total=int(d.get('totalContributions',sum(ds.values())))
 return f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 830 190"><rect x="1" y="1" width="828" height="188" rx="18" fill="#0d1117" stroke="#30363d"/>{labels}<text x="14" y="63" fill="#8b949e" font-family="{FONT}" font-size="10">Mon</text><text x="14" y="105" fill="#8b949e" font-family="{FONT}" font-size="10">Wed</text><text x="14" y="147" fill="#8b949e" font-family="{FONT}" font-size="10">Fri</text>{"".join(cells)}<text x="64" y="178" fill="#39d353" font-family="{FONT}" font-size="10">{total} contributions in 2026</text></svg>'
def terminal():
 im=Image.open(ASSETS/'avatar.jpg').convert('L'); s=min(im.size); im=im.crop(((im.width-s)//2,(im.height-s)//2,(im.width+s)//2,(im.height+s)//2)); im=ImageEnhance.Contrast(ImageOps.autocontrast(im)).enhance(1.25).resize((64,36)); ramp=' .:-=+*#%@'; rows=[''.join(ramp[min(9,im.getpixel((x,y))*10//256)] for x in range(64)) for y in range(36)]; ts=''.join(f'<text x="18" y="{58+i*6.1:.1f}" fill="#39d353" opacity="0" font-family="{FONT}" font-size="5.8" xml:space="preserve">{escape(row)}<animate attributeName="opacity" from="0" to="1" dur="0.18s" begin="{i*.06:.2f}s" fill="freeze"/></text>' for i,row in enumerate(rows)); return f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 830 350"><rect x="1" y="1" width="828" height="348" rx="16" fill="#111827" stroke="#374151"/><circle cx="22" cy="22" r="6" fill="#ff5f56"/><circle cx="42" cy="22" r="6" fill="#ffbd2e"/><circle cx="62" cy="22" r="6" fill="#27c93f"/><text x="82" y="26" fill="#9ca3af" font-family="{FONT}" font-size="11">toshitsai@github:~$ ./portrait</text>{ts}<text x="18" y="337" fill="#60a5fa" font-family="{FONT}" font-size="12">toshitsai@github:~$ neofetch<tspan fill="#39d353"> ▮</tspan><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></text></svg>'
def info():
 rows=[('ToshitSai','@ github','u'),('','────────────────────────','d'),('Role','AI Product Developer','k'),('Focus','AI products & Prompt Engineering','k'),('College','NIAT','k'),('— Stack —','','s'),('Frontend','React','k'),('Backend','Node.js','k'),('Language','JavaScript · TypeScript · Python','k'),('AI','Prompt Engineering','k'),('— Highlights —','','s'),('●','CourseForge AI','b'),('●','Greetly','b'),('●','Job Gem Grader','b'),('●','Portfolio on Vercel','b')]; h=40+len(rows)*20+24; out=[]
 for i,(k,v,t) in enumerate(rows):
  y=58+i*20; a=f'<animate attributeName="opacity" from="0" to="1" dur="0.25s" begin="{i*.12:.2f}s" fill="freeze"/>'
  if t=='u':out.append(f'<text x="24" y="{y}" fill="#39D0D8" font-family="{FONT}" font-size="13" opacity="0">{k}<tspan fill="#3FB950"> {v}</tspan>{a}</text>')
  elif t=='d':out.append(f'<text x="24" y="{y}" fill="#484f58" font-family="{FONT}" font-size="11" opacity="0">{v}{a}</text>')
  elif t=='s':out.append(f'<text x="24" y="{y}" fill="#58A6FF" font-family="{FONT}" font-size="12" opacity="0">{k}{a}</text>')
  elif t=='k':out.append(f'<text x="24" y="{y}" fill="#E8833A" font-family="{FONT}" font-size="11" opacity="0">{k}</text><text x="130" y="{y}" fill="#C9D1D9" font-family="{FONT}" font-size="11" opacity="0">{v}{a}</text>')
  else:out.append(f'<text x="24" y="{y}" fill="#39D353" font-family="{FONT}" font-size="11" opacity="0">{k}</text><text x="42" y="{y}" fill="#C9D1D9" font-family="{FONT}" font-size="11" opacity="0">{v}{a}</text>')
 return f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 830 {h}"><rect x="1" y="1" width="828" height="{h-2}" rx="16" fill="#111827" stroke="#374151"/><text x="24" y="28" fill="#f9fafb" font-family="{FONT}" font-size="13">ToshitSai@github:~$ neofetch</text>{"".join(out)}</svg>'
try:d=data()
except Exception:d={'totalContributions':0,'weeks':[]}
(ASSETS/'github-contribution-animation.svg').write_text(contribution(d),encoding='utf-8'); (ASSETS/'terminal-card.svg').write_text(terminal(),encoding='utf-8'); (ASSETS/'info-card.svg').write_text(info(),encoding='utf-8')
