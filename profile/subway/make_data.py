#!/usr/bin/env python3
"""ledger.json -> data.js for the subway pages. Only numbers found in the ledger are written.

    python3 make_data.py [ledger.json] [data.js]

ledger["projects"] ([{key,name,repo,line,link}]) are the lines on the map, in lane order; ledger["retired"] are listed
projects that dropped off the map and get a faded lane. Without a projects array every key in ledger["repos"] is drawn."""
import json, sys, os, datetime as D, collections

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'data', 'ledger.json')
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'data.js')
MON = 'jan feb mar apr may jun jul aug sep oct nov dec'.split()
fmt = lambda d: f'{MON[d.month-1]} {d.day}'
# used only when the ledger has no projects array yet
FALLBACK = {
 'vel': ('vel', 'an ai tutor that draws on your screen while it explains', '#vel'),
 'lea': ('lea', 'scan a device with your iphone and see the broken part circled in 3d', '#lea'),
 'jobradar-ai': ('jobradar', 'my internship radar. it pings my phone when a new listing shows up', 'card'),
 'dailygames-slackbot': ('sportsgrid', "a slack bot that posts the day's puzzles and keeps a leaderboard", 'card'),
 'neetcode-submissions': ('neetcode', 'interview practice, synced so every attempt is versioned', 'card'),
 'evision': ('evision', 'the web-app version of kalshi ev', 'card'),
 'kalshi-ev-extension': ('kalshi ev', 'a chrome extension that shows expected value on kalshi sports markets', 'card'),
 'rohan_drone_club': ('drone stitcher', 'turns a drone flight video into one panorama', 'card'),
}

L = json.load(open(SRC))
weeks = L['weeks']
w0 = D.date.fromisoformat(weeks[0][0][0])
end = D.date.fromisoformat(weeks[-1][-1][0])
wk = lambda s: (D.date.fromisoformat(s[:10]) - w0).days // 7
meta = {p['key']: p for p in L.get('projects', []) + L.get('retired', [])}
ON_MAP = [p['key'] for p in L['projects'] if p['key'] in L['repos']] if L.get('projects') else list(L['repos'])
RETIRED = [p['key'] for p in L.get('retired', []) if p['key'] in L['repos'] and p['key'] not in ON_MAP]

per = {}
for key, r in L['repos'].items():
    per[key] = collections.Counter(wk(x) for x in r.get('dates', []) if 0 <= wk(x) < len(weeks))
active = sorted({w for k in ON_MAP for w in per[k]})          # a week where any project has a commit = one column
col = {w: i for i, w in enumerate(active)}
columns, seen = [], set()
for w in active:
    d = w0 + D.timedelta(days=7 * w); m = (d.year, d.month)
    columns.append({'week': w, 'date': fmt(d), 'month': MON[d.month-1] if m not in seen else ''})
    seen.add(m)
gaps = []                                                       # long empty stretches; the map draws the longest as water
for a, b in zip(active, active[1:]):
    if b - a >= 8:
        gaps.append({'after': col[a], 'weeks': b - a - 1,
                     'from': fmt(w0 + D.timedelta(days=7 * (a + 1))), 'to': fmt(w0 + D.timedelta(days=7 * b - 1))})
def entry(key, on_map):
    r = L['repos'][key]; m = meta.get(key, {}); fb = FALLBACK.get(key)
    last = D.date.fromisoformat(r['last'][:10]) if r.get('last') else None
    dates = [x for x in r.get('dates', [])]
    return ({'key': key,
                  'name': (m.get('name') or (fb[0] if fb else key.replace('-', ' ').replace('_', ' '))).lower(),
                  'what': m.get('line') or (fb[1] if fb else ''),
                  'link': m.get('link') or (fb[2] if fb else ''),
                  'commits': len(dates),
                  'stops': [{'col': col.get(w, -1), 'week': w, 'n': n} for w, n in sorted(per[key].items())],
                  'first': fmt(D.date.fromisoformat(min(dates)[:10])) if dates else '',
                  'last': fmt(last) if last else '', 'last_year': last.year if last else 0,
                  'last_month': f'{MON[last.month-1]} {last.year}' if last else '',
                  'last_iso': last.isoformat() if last else '',
                  'running': bool(last) and (end - last).days < 7})   # committed in the final week: the line runs off the edge
lines = [entry(k, True) for k in ON_MAP]
if not L.get('projects'): lines.sort(key=lambda l: (l['last_iso'], l['commits']), reverse=True)
retired = [entry(k, False) for k in RETIRED]
# past work (jobs) comes from profile/data/lines.json: [{key, name, line, role, color_key}]
work = []
try:
    for w in json.load(open(os.path.join(HERE, '..', 'data', 'lines.json'))).get('work', []):
        work.append({k: w.get(k, '') for k in ('key', 'name', 'line', 'role', 'color_key')})
except (OSError, ValueError):
    pass
tot = [sum(d[1] for d in w) for w in weeks]
bw = max(range(len(tot)), key=tot.__getitem__)
data = {'total': L['total'], 'private': L['private'], 'nweeks': len(weeks), 'end_year': end.year,
        'from': f'{MON[w0.month-1]} {w0.year}', 'to': f'{MON[end.month-1]} {end.year}', 'today': fmt(end),
        'busiest': {'n': tot[bw], 'date': fmt(w0 + D.timedelta(days=7 * bw))},
        'columns': columns, 'gaps': gaps, 'lines': lines, 'retired': retired, 'work': work,
        'names': {k: (meta.get(k, {}).get('name') or (FALLBACK[k][0] if k in FALLBACK else k)).lower() for k in L['repos']}}
open(OUT, 'w').write('window.DATA = ' + json.dumps(data, indent=1) + ';\n')
open(os.path.join(os.path.dirname(OUT), 'order.txt'), 'w').write('\n'.join(l['key'] for l in lines + retired) + '\n')
open(os.path.join(os.path.dirname(OUT), 'work.txt'), 'w').write(''.join(w['key'] + '\n' for w in work))
print(OUT, len(columns), 'columns', len(lines), 'lines', data['total'], data['private'], file=sys.stderr)
