from __future__ import annotations
import datetime as dt, json, os, re, sys, urllib.request
from pathlib import Path
from xml.sax.saxutils import escape
from PIL import Image, ImageOps, ImageEnhance

ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'assets'; FONT="ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', 'Courier New', monospace"

def get_json():
 q='query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){contributionsCollection(from:$from,to:$to){contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'
 body=json.dumps({'query':q,'variables':{'login':'ToshitSai','from':'2026-01-01T00:00:00Z','to':'2026-12-31T23:59:59Z'}}).encode(); tok=os.getenv('PROFILE_GITHUB_TOKEN') or os.getenv('GITHUB_TOKEN',''); req=urllib.request.Request('https://api.github.com/graphql',data=body,headers={'Content-Type':'application/json','Authorization':f'bearer {tok}'})
 with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)['data']['user']['contributionsCollection']

def public_data():
 u='https://github.com/users/ToshitSai/contributions?from=2026-01-01&to=2026-12-31'; html=urllib.request.urlopen(u,timeout=30).read().decode('utf-8','ignore'); ds={}; total=0
 for n in re.findall(r'(?:aria-label="|>)(\d+) contributions? (?:on|in)',html): total+=int(n)
 for date,level in re.findall(r'data-date="(2026-\d\d-\d\d)"[^>]*data-level="(\d)"',html): ds[dt.date.fromisoformat(date)]=int(level)
 if not ds: raise RuntimeError('public contribution page contained no 2026 day cells')
 return {'totalContributions':total or sum(1 for x in ds.values() if x), 'levels':ds}

def contribution_svg(d):
 first=dt.date(2026,1,1); first-=dt.timedelta(days=(first.weekday()+1)%7); levels=d.get('levels',{}); total=int(d['totalContributions']); colors=['#161b22','#0e4429','#006d32','#26a641','#39d353']; tints=['','#57ffb0','#8dffcc','#c8ffe8','#c8ffe8']; cells=[]
 for c in range(53):
  for r in range(7):
   day=first+dt.timedelta(days=c*7+r); n=levels.get(day,0) if day<=dt.date.today() and day.year==2026 else 0; x,y=34+14*c,28+14*r; level=min(4,n); t=max(0.0001,c*.0115+r*.0069); glow=' filter="url(#cellglow)"' if level>=3 else ''
   opacity=f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{t:.4f};{t+.012:.4f};1" dur="7s" repeatCount="indefinite"/>'
   if level:
    anim=opacity+f'<animate attributeName="fill" values="{colors[level]};{colors[level]};{tints[level]};{colors[level]}" keyTimes="0;{t:.4f};{t+.012:.4f};{t+.05:.4f}" calcMode="spline" keySplines="0 0 1 1;0.1 0 0.2 1;0.4 0 0.6 1" dur="7s" repeatCount="indefinite"/>'
    sparkle=f'<rect x="{x+2}" y="{y+2}" width="4" height="2" rx="1" fill="white" opacity="0"><animate attributeName="opacity" values="0;0;0.55;0" keyTimes="0;{t:.4f};{t+.012:.4f};{t+.05:.4f}" calcMode="spline" keySplines="0 0 1 1;0 0 0.3 1;0.5 0 1 1" dur="7s" repeatCount="indefinite"/></rect>'
   else:
    anim=opacity; sparkle=''
   cells.append(f'<rect x="{x}" y="{y}" width="11" height="11" rx="2" fill="{colors[level]}" opacity="0"{glow}>{anim}</rect>{sparkle}')
 labels=''.join(f'<text x="{34+((dt.date(2026,m,1)-first).days//7)*14}" y="18" fill="#8b949e" font-family="system-ui,sans-serif" font-size="10">{dt.date(2026,m,1):%b}</text>' for m in range(1,13)); return f'<svg xmlns="http://www.w3.org/2000/svg" font-family="{FONT}" width="850" height="165" viewBox="0 0 850 165"><defs><filter id="cellglow"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><rect x="0.5" y="0.5" width="849" height="164" rx="16" fill="#0d1117" stroke="#30363d"/>{labels}<g fill="#8b949e" font-family="system-ui,sans-serif" font-size="9"><text x="0" y="38">Mon</text><text x="0" y="66">Wed</text><text x="0" y="94">Fri</text></g>{"".join(cells)}</svg>'

def terminal():
 im=Image.open(A/'avatar.jpg').convert('L'); s=min(im.size); im=im.crop(((im.width-s)//2,(im.height-s)//2,(im.width+s)//2,(im.height+s)//2)); im=ImageEnhance.Contrast(ImageOps.autocontrast(im)).enhance(1.2).resize((100,53)); ramp="#@%SsC*+=:-'.` "; rows=[''.join(ramp[min(len(ramp)-1,p*len(ramp)//256)] for p in [im.getpixel((x,y)) for x in range(100)]) for y in range(53)]; body=[]
 for i,row in enumerate(rows):
  y=48.1+15*i; clip=f'<clipPath id="r{i}"><rect x="20" y="{37+15*i}" width="0" height="15"><animate attributeName="width" from="0" to="800" begin="{.11*i:.2f}s" dur=".11s" fill="freeze"/></rect></clipPath>'; cursor=f'<rect x="20" y="{y-12}" width="8" height="13" fill="#c9d1d9" opacity="0"><animate attributeName="x" from="20" to="820" begin="{.11*i:.2f}s" dur=".11s" fill="freeze"/><animate attributeName="opacity" values=".85;0" begin="{.11*i:.2f}s" dur=".11s" fill="freeze"/></rect>'; body.append(clip+f'<text xml:space="preserve" x="20" y="{y}" fill="#c9d1d9" font-family="{FONT}" font-size="12.9" textLength="800" lengthAdjust="spacing" clip-path="url(#r{i})">{escape(row)}</text>'+cursor)
 return f'<svg xmlns="http://www.w3.org/2000/svg" font-family="{FONT}" width="840" height="875" viewBox="0 0 840 875"><defs><linearGradient id="bg" x2="0" y2="1"><stop stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs><rect x=".5" y=".5" width="839" height="874" rx="12" fill="url(#bg)" stroke="#30363d"/><line x1="0" y1="30" x2="840" y2="30" stroke="#30363d"/><circle cx="20" cy="15" r="5" fill="#ff5f56"/><circle cx="36" cy="15" r="5" fill="#ffbd2e"/><circle cx="52" cy="15" r="5" fill="#27c93f"/><text x="420" y="19" text-anchor="middle" fill="#7d8590" font-family="{FONT}" font-size="12">ToshitSai@github: ~$ ./portrait.sh</text>{"".join(body)}<line x1="20" y1="832" x2="820" y2="832" stroke="#30363d"/><text x="20" y="851" fill="#7d8590" font-family="{FONT}" font-size="13">ToshitSai@github:~$ whoami <tspan fill="#c9d1d9">Toshit Sai Galam</tspan></text><rect x="250" y="838" width="8" height="14" fill="#c9d1d9"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.51;1" dur="1s" repeatCount="indefinite"/></rect></svg>'

def info():
 rows=[('Role','AI Product Developer','k'),('Focus','AI products & Prompt Engineering','k'),('College','NIAT','k'),('— Stack','', 's'),('Frontend','React','k'),('Backend','Node.js','k'),('Language','JavaScript, TypeScript, Python','k'),('AI','Prompt Engineering','k'),('— Highlights','', 's'),('●','CourseForge AI','b'),('●','Greetly','b'),('●','Job Gem Grader','b'),('●','Portfolio on Vercel','b')]; H=40+60+len(rows)*21+40; out=[]
 for i,(k,v,t) in enumerate(rows):
  y=104+i*21; a=f'<animate attributeName="opacity" from="0" to="1" begin="{.15+i*.06:.2f}s" dur=".4s" fill="freeze"/><animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" begin="{.15+i*.06:.2f}s" dur=".4s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1"/>'; col='#ffa657' if t=='k' else '#58a6ff' if t=='s' else '#3fb950';
  if t=='s': content=f'<text x="20" y="{y}" fill="{col}" font-weight="700">{k}</text><line x1="72" y1="{y-4}" x2="460" y2="{y-4}" stroke="#30363d"/>'
  elif t=='b': content=f'<circle cx="23" cy="{y-4}" r="2.5" fill="#3fb950"/><text x="34" y="{y}" fill="#c9d1d9">{escape(v)}</text>'
  else: content=f'<text x="20" y="{y}" fill="#ffa657" font-weight="700">{escape(k)}</text><text x="112" y="{y}" fill="#c9d1d9">{escape(v)}</text>'
  out.append(f'<g opacity="0" transform="translate(0,5)">{content}{a}</g>')
 return f'<svg xmlns="http://www.w3.org/2000/svg" font-family="{FONT}" width="480" height="{H}" viewBox="0 0 480 {H}"><defs><linearGradient id="bg" x2="0" y2="1"><stop stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs><rect x=".5" y=".5" width="479" height="{H-1}" rx="12" fill="url(#bg)" stroke="#30363d"/><line x1="0" y1="30" x2="480" y2="30" stroke="#30363d"/><text x="240" y="19" text-anchor="middle" fill="#7d8590" font-family="{FONT}" font-size="12">ToshitSai@github: ~$ neofetch</text><line x1="178" y1="56" x2="460" y2="56" stroke="#30363d"/><text x="20" y="60" fill="#3fb950" font-family="{FONT}" font-size="14" font-weight="700">ToshitSai <tspan fill="#7d8590">@</tspan><tspan fill="#22d3ee">github</tspan></text>{"".join(out)}</svg>'

try:
 g=get_json(); days={dt.date.fromisoformat(x['date']):int(x['contributionCount']) for w in g['weeks'] for x in w['contributionDays']}; payload={'totalContributions':int(g['totalContributions']),'levels':{d:min(4,1+n//4) for d,n in days.items()}}
 if payload['totalContributions']==0: raise RuntimeError('GraphQL returned zero')
except Exception:
 try: payload=public_data()
 except Exception as e: print(e,file=sys.stderr); sys.exit(1)
(A/'github-contribution-animation.svg').write_text(contribution_svg(payload),encoding='utf-8'); (A/'terminal-card.svg').write_text(terminal(),encoding='utf-8'); (A/'info-card.svg').write_text(info(),encoding='utf-8'); (A/'contributions.txt').write_text(f"{payload['totalContributions']} contributions in 2026\n",encoding='utf-8')
