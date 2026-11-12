#!/usr/bin/env python3
"""Data for the subway map, and the README block of station signs under it.

    python3 profile/lines.py            # fetch commits (gh login, or PROFILE_TOKEN in the Action) -> profile/data/ledger.json
    python3 profile/lines.py --readme   # rewrite the README between <!-- log:start --> and <!-- log:end --> from ledger.json

Which lines exist: profile/data/lines.json lists the projects with their names and click targets.
On top of that, any PUBLIC repo you commit to gets a line on its own (name and description from GitHub).
A PRIVATE repo only appears once its full name is in private_allow, so a new private project never
shows up on your public profile by surprise.
"""
import html, json, os, re, subprocess, sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "profile" / "data" / "ledger.json"
LINES = ROOT / "profile" / "data" / "lines.json"
ASSETS = ROOT / "assets" / "subway"
LOGIN = "rohankilaru-ai"
TZ = ZoneInfo("America/Los_Angeles")                    # commit days are counted in the owner's time zone
# the map and the station signs change every day, so they live on an orphan branch that the Action
# force-pushes (one commit, no history growth); everything else stays on main
DAILY = f"https://github.com/{LOGIN}/{LOGIN}/raw/subway-daily/"
CAL_Q = ('query{ user(login:"%s"){ contributionsCollection{ restrictedContributionsCount '
         'contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } } '
         'commitContributionsByRepository(maxRepositories:100){ repository{ nameWithOwner isPrivate isFork description } '
         'contributions{ totalCount } } } } }' % LOGIN)


def gh(args, env):
    return subprocess.run(["gh", "api", *args], capture_output=True, text=True, env=env, check=True).stdout


def day(ts):
    """an ISO timestamp from the API as a date in the owner's time zone"""
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(TZ).date().isoformat()


def commits(repo, first, env):
    """my commits on every branch since `first` (dates only), plus my last commit date ever"""
    default = gh([f"repos/{repo}", "--jq", ".default_branch"], env).strip()
    seen = {}
    for ln in gh([f"repos/{repo}/commits?author={LOGIN}&since={first}T00:00:00Z&per_page=100", "--paginate",
                  "--jq", ".[] | [.sha, .commit.author.date] | @tsv"], env).splitlines():
        sha, d = ln.split("\t"); seen[sha] = day(d)
    for b in gh([f"repos/{repo}/branches?per_page=100", "--paginate", "--jq", ".[].name"], env).split():
        if b == default:                                  # work that never reached the default branch
            continue
        try:
            out = gh([f"repos/{repo}/compare/{quote(default, safe='')}...{quote(b, safe='')}?per_page=100", "--paginate", "--jq",
                      f'.commits[] | select(.author.login == "{LOGIN}") | [.sha, .commit.author.date] | @tsv'], env)
        except subprocess.CalledProcessError:             # an orphan branch shares no history: list it whole
            out = gh([f"repos/{repo}/commits?sha={quote(b, safe='')}&author={LOGIN}&since={first}T00:00:00Z&per_page=100",
                      "--paginate", "--jq", ".[] | [.sha, .commit.author.date] | @tsv"], env)
        for ln in out.splitlines():
            sha, d = ln.split("\t")
            if day(d) >= first:
                seen[sha] = day(d)
    last = max(seen.values(), default="") or gh([f"repos/{repo}/commits?author={LOGIN}&per_page=1",
                                                 "--jq", ".[0].commit.author.date // empty"], env).strip()
    last = day(last) if "T" in (last or "") else last
    return {"dates": sorted(seen.values()), "last": last or None}


def short(desc):
    """a repo description as a sign line: lowercase, no trailing period, about 48 characters"""
    s = re.sub(r"\s+", " ", (desc or "").strip()).rstrip(".").lower()
    if len(s) <= 48:
        return s
    return s[:48].rsplit(" ", 1)[0].rstrip(",;:-")


def discover(cfg, cc, env, first):
    """listed projects first, then public repos with my commits this year, then allowed private ones"""
    listed = {p["repo"].lower() for p in cfg["projects"]}
    skip = {r.lower() for r in cfg.get("ignore", [])} | listed
    found = []
    # my own public repos (this endpoint never returns private ones)
    for r in json.loads(gh([f"users/{LOGIN}/repos?type=owner&sort=pushed&per_page=100"], env)):
        if r["fork"] or r["archived"] or r["full_name"].lower() in skip or r["pushed_at"][:10] < first:
            continue
        found.append((r["full_name"], r["name"], r.get("description")))
    # public repos owned by others that I committed to
    for c in cc["commitContributionsByRepository"]:
        repo = c["repository"]
        if repo["isPrivate"] or repo["isFork"] or repo["nameWithOwner"].lower() in skip:
            continue
        if repo["nameWithOwner"].split("/")[0].lower() != LOGIN.lower() and c["contributions"]["totalCount"] >= 3:
            found.append((repo["nameWithOwner"], repo["nameWithOwner"].split("/")[1], repo.get("description")))
    # private repos the owner chose to show
    for full in cfg.get("private_allow", []):
        if full.lower() not in skip:
            r = json.loads(gh([f"repos/{full}"], env))
            found.append((r["full_name"], r["name"], r.get("description")))
    auto, seen = [], set()
    for full, name, desc in found:
        if full.lower() in seen:
            continue
        seen.add(full.lower())
        auto.append({"key": full.split("/")[1].lower(), "name": name, "repo": full, "line": short(desc),
                     "link": f"https://github.com/{full}", "auto": True})
    return cfg["projects"] + auto


def rank(projects, repos, cfg):
    """the map keeps the max_lines projects with the most commits in the last active_days (newest work first);
    listed projects that fall off are 'retired' (shown faded, card still opens); hidden ones never show"""
    hide = {r.lower() for r in cfg.get("hide", [])}
    since = (date.today() - timedelta(days=cfg.get("active_days", 120))).isoformat()
    recent = {p["key"]: sum(1 for d in repos[p["key"]]["dates"] if d >= since) for p in projects}
    live = [p for p in projects if p["repo"].lower() not in hide and recent[p["key"]] > 0]
    live = sorted(live, key=lambda p: (recent[p["key"]], repos[p["key"]]["last"] or ""), reverse=True)[:cfg.get("max_lines", 5)]
    live.sort(key=lambda p: repos[p["key"]]["last"] or "", reverse=True)          # on the page: most recent work first
    keys = {p["key"] for p in live}
    retired = [p for p in projects if p["key"] not in keys and p["repo"].lower() not in hide and not p.get("auto")]
    retired.sort(key=lambda p: repos[p["key"]]["last"] or "", reverse=True)
    return live, retired


def fetch():
    env = dict(os.environ)
    if os.environ.get("PROFILE_TOKEN"):
        env["GH_TOKEN"] = os.environ["PROFILE_TOKEN"]
    elif os.environ.get("GITHUB_ACTIONS"):
        print("no PROFILE_TOKEN: VEL's private commits would be missing, so the map is left as it is"); sys.exit(0)
    cfg = json.loads(LINES.read_text())
    cc = json.loads(gh(["graphql", "-f", f"query={CAL_Q}"], env))["data"]["user"]["contributionsCollection"]
    cal = cc["contributionCalendar"]
    first = cal["weeks"][0]["contributionDays"][0]["date"]
    old = json.loads(DATA.read_text()).get("repos", {}) if DATA.exists() else {}
    projects, repos = [], {}
    for p in discover(cfg, cc, env, first):
        try:
            repos[p["key"]] = commits(p["repo"], first, env)
        except (subprocess.CalledProcessError, ValueError) as e:     # empty, renamed or unreadable: keep what we had
            print(f'{p["repo"]}: {e}; keeping the last good data')
            repos[p["key"]] = old.get(p["key"], {"dates": [], "last": None})
        if p.get("auto") and not repos[p["key"]]["dates"]:
            continue                                                  # auto lines need commits this year
        projects.append(p)
    projects, retired = rank(projects, repos, cfg)
    data = {"private": cc["restrictedContributionsCount"], "total": cal["totalContributions"],
            "weeks": [[(d["date"], d["contributionCount"]) for d in w["contributionDays"]] for w in cal["weeks"]],
            "projects": projects, "retired": retired, "repos": repos}
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(data))
    for p in projects + retired:
        r = repos[p["key"]]
        tag = "  (faded, past projects)" if p in retired else ("  (new line)" if p.get("auto") else "")
        print(f'{p["name"]:<22} {len(r["dates"]):>5} commits  last {r["last"]}{tag}')
    return data


def daily(name):
    return DAILY + name


def asset(stem):
    for ext in (".webp", ".png"):
        if (ASSETS / f"{stem}{ext}").exists():
            return f"assets/subway/{stem}{ext}"
    return f"assets/subway/{stem}.png"


def star(p):
    """a link to the repo page (where its Star button is): markdown cannot star a repo by itself"""
    return (f'<a href="https://github.com/{p["repo"]}"><img src="assets/subway/tag-star.png" width="260" '
            f'alt="star {html.escape(p["name"])} on GitHub"></a>')


def section(sign, alt, open_):
    """a section sign is the summary of its own dropdown, so its arrow opens and closes the section;
    95% wide so GitHub's disclosure triangle sits beside it instead of on a line of its own"""
    return (f'<details{" open" if open_ else ""}><summary><picture><img src="{daily(sign)}" width="95%" alt="{alt}">'
            f'</picture></summary>\n')


def stop(p, data, body, open_=False):
    """one stop: the lane image is the summary, the body opens under it; clicking the arrow closes it again"""
    r = data["repos"][p["key"]]; n = len(r["dates"])
    alt = html.escape(f'{p["name"]}: {p["line"]}. {n:,} commit{"s" if n != 1 else ""} this year, last {r["last"] or "none"}. Click to open.')
    return [f'<a name="{p["key"]}"></a>',
            f'<details{" open" if open_ else ""}><summary><picture><img src="{daily("lane-" + p["key"] + ".png")}" width="94%" alt="{alt}"></picture></summary>', '',
            *body, '</details>', '']


def readme_block(data):
    cfg = {p["key"]: p for p in json.loads(LINES.read_text())["projects"]}
    live = [{**p, **cfg.get(p["key"], {})} for p in data["projects"]]          # names, films and links from lines.json
    retired = [{**p, **cfg.get(p["key"], {})} for p in data.get("retired", [])]
    building = [p for p in live if p["link"] == "film"]
    side = [p for p in live if p["link"] != "film"]
    out = []
    if building:
        out += ['<a name="building-now"></a>', section("sign-building.png", "building now", True)]
        for p in building:
            f = p["film"]
            body = [f'<img src="{f["src"]}" width="94%" alt="{html.escape(f["alt"])}">', '', f.get("note", ""), '']
            if f.get("star"):
                body += [star(p), '']
            out += stop(p, data, body, open_=True)
    if side:
        out += ['</details>', ''] if building else []
        out += ['<a name="side-projects"></a>', section("sign-side.png", "side projects", True)]
        for p in side:
            if p["link"] == "card":
                out += stop(p, data, [f'<img src="{asset("card-" + p["key"])}" width="94%" alt="{html.escape(p["name"])} details">', '', star(p), ''])
            else:                                         # a repo that earned a line on its own: no card yet
                out += stop(p, data, [f'**[{html.escape(p["name"])}]({p["link"]})**: {html.escape(p["line"])}', ''])
    if side:
        out += ['</details>', '']
    elif building:
        out += ['</details>', '']
    if retired:
        out += ['<a name="past-projects"></a>', section("sign-projects.png", "past projects: click to open", False)]
        for p in retired:
            out += stop(p, data, [f'<img src="{asset("card-" + p["key"])}" width="94%" alt="{html.escape(p["name"])} details">', '', star(p), ''])
        out += ['</details>', '']
    return "\n".join(out).rstrip() + "\n"


def work_block():
    """past work: a dropdown of stops, one per job, each opening into its clips and a line of text (lines.json "work")"""
    out = ['<a name="past-work"></a>', section("sign-work.png", "past work", True)]
    for w in json.loads(LINES.read_text()).get("work", []):
        body = []
        for b in w["body"]:
            body += [f'<img src="{b["img"]}" width="94%" alt="{html.escape(b["alt"])}">' if "img" in b else b["text"], '']
        out += [f'<a name="{w["key"]}"></a>',
                f'<details open><summary><picture><img src="{daily("lane-" + w["key"] + ".png")}" width="94%" '
                f'alt="{html.escape(w["name"])}: {html.escape(w["line"])}, {html.escape(w["role"])}. Click to open."></picture></summary>', '',
                *body, '</details>', '']
    out += ['</details>', '']
    return "\n".join(out)


def write_readme(data):
    p = ROOT / "README.md"; s = p.read_text()
    block = readme_block(data)
    new = re.sub(r"(<!-- log:start -->\n).*?(<!-- log:end -->)",
                 lambda m: m.group(1) + LOG_HEAD + "\n" + block + m.group(2), s, flags=re.S)
    new = re.sub(r"(<!-- work:start -->\n).*?(<!-- work:end -->)", lambda m: m.group(1) + work_block() + m.group(2), new, flags=re.S)
    p.write_text(new)


LOG_HEAD = ('<a name="log"></a>\n<img src="' + DAILY + 'log.webp" width="100%" alt="Practice log as a subway map: '
            'every project is a line, every week with commits is a station, most recent work on the right">\n')


if __name__ == "__main__":
    if "--readme" in sys.argv:
        write_readme(json.loads(DATA.read_text()))
    else:
        fetch()
