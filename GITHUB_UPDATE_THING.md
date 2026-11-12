# GitHub update thing

This is the handoff for anyone, AI agent or person, who updates Rohan's GitHub profile (github.com/rohankilaru-ai, this repo). Read all of it before changing anything. Then do what the owner asked, in the style that's already here, and keep the change small.

## What the profile is
`README.md` is the page, and almost everything on it is an image drawn as a **New York subway diagram**: Vignelli 1972 style, the Overpass font, white on sign-black, one colour per line. There are no MTA logos or line letters. The page reads top to bottom as one route:

1. **Intro** (`assets/subway/intro.webp`): "hi, i'm rohan." plus the intro sentence over a route. It stops at uc berkeley → whoosh → climate plans → underdog → ariento, then forks into **vel** (yellow) and **lea** (pink). The forks come from `INTRO_BRANCHES` at the top of `profile/subway/intro.html`.
2. **Connect tags**, 2×2: linkedin, x (@Roh_Kil), follow on github, and "work with me", which jumps to `#connect`. They live in `README.md`.
3. **The map** (`log.webp`, practice log): every project is a line, every week with commits is a station, plus a legend. A white route leaves the map's bottom left and runs down the whole page.
4. **Building now**: a dropdown, open by default. VEL and LEA are stops whose films open in place.
5. **Side projects**: a dropdown, open. JobRadar and SportsGrid are stops that open their cards and a "star on github" tag.
6. **Past projects**: a dropdown, closed. Faded grey stops for Kalshi EV, EVision and Drone Stitcher, each still opening its card.
7. **Past work**: a dropdown, open. Climate Plans (sage) and Ariento (dusty blue) are stops that open their clips and a line of text.
8. **Last stop** (`#connect`): the route ends at a terminal ("want to build something together?…"), then one transfer row with linkedin, x and github (`xfer-*.png` at `width="32%"`).

## What updates by itself
`.github/workflows/subway.yml` runs every morning (09:17 UTC). It can also be started by hand from Actions → "subway map" → Run workflow.

1. `python profile/lines.py` fetches commits into `profile/data/ledger.json`: every branch, Pacific time, using the `PROFILE_TOKEN` secret (already set).
2. `bash profile/subway/render.sh --daily` redraws the map, every lane (stop sign) and the four section signs.
3. `python profile/lines.py --readme` rewrites the README between `<!-- log:start/end -->` and `<!-- work:start/end -->`. **Never hand-edit inside those markers**; edit `profile/data/lines.json` instead.
4. The daily images are force-pushed to the **`subway-daily`** branch (always one commit, so history doesn't grow). The README loads them from `https://github.com/rohankilaru-ai/rohankilaru-ai/raw/subway-daily/<file>`. On `main`, `assets/subway/log.*` and `lane-*.png` are gitignored for that reason.
5. `ledger.json` and `README.md` are committed to `main` by "subway bot" when they change.

Browsers keep these images for up to 5 minutes, so a hard refresh shows a new version sooner.

**Ranking is automatic:**
- The map shows the `max_lines` (5) projects with the most commits in the last `active_days` (120), newest work first.
- When something newer passes one of them, the weakest drops into "past projects".
- A new **public** repo with commits gets its own line, sign and colour the next morning.
- A **private** repo only appears once it's in `private_allow`.

## The one config file: `profile/data/lines.json`
- `projects`: `key` (repo name in lowercase), `name`, `repo` (`owner/name`), `line` (≤ 48 chars, plain lowercase), and `link`:
  - `"film"` puts it under **building now**. It needs a `film` object: `src`, `alt`, `note` (markdown), and `star: true` if the repo is public.
  - `"card"` makes it a side or past project that opens `assets/subway/card-<key>.webp` and a star tag.
  - a URL means an auto-discovered repo with no card yet.
- `work`: past jobs, in order: `key`, `name`, `line`, `role`, `color_key`, and `body` (a list of `{img, alt}` and `{text}` items).
- `max_lines`, `active_days`, `hide` (never shown; NeetCode is hidden), `private_allow` (VEL), `ignore` (never fetched).

## Recipes
Run them from the repo root. After a data change, run `profile/update.sh`: it fetches, redraws and rewrites the README. Use `--offline` to skip the fetch. Look at the result, commit and push.

- **Start showing a new project now, without waiting for the morning:** run `profile/update.sh`, push, and publish the daily images (copy the block from the Action's "publish" step), or just run the workflow by hand.
- **Promote a project to building now:**
  1. Set `link: "film"` and fill in `film`.
  2. Make the clip with `profile/subway/film.html` and `films.js`; `footage.sh` extracts frames from a recording.
  3. Render it with `bash profile/subway/render.sh <id>`.
  4. Add the key to `INTRO_BRANCHES` in `intro.html` and run `render.sh intro`.
- **Give a project a card:** add it to `profile/subway/cards.js` (what it is, one note, how-it-works steps, optional demo). Run `render.sh card-<key>`, then set `link: "card"`.
- **Add a job:** add a `work` entry, plus a muted colour for its `color_key` in `profile/subway/colors.js`. Make its clips, then run `render.sh signs` and `profile/update.sh --offline`.
- **Change the intro text or the stops:** edit `intro.html` and run `render.sh intro`. Keep the README `alt` text in sync.
- **Change contact links:** the link targets are in `README.md` (top 2×2 and the bottom transfer row). The images come from `render.sh connect` (`tag.html`, `xfer.html`, `connect.html`).
- **Hide or show something:** edit `hide` or `private_allow`.

## Colours (`profile/subway/colors.js`, tier rule in `lib.js`)
| Tier | Look | Projects |
|---|---|---|
| building now (`link: "film"`) | brightest | vel yellow, lea pink |
| side projects | mid | jobradar green, sportsgrid blue |
| past work | muted | climate plans sage, ariento dusty blue |
| past projects | grey | faded ones |

New keys get a colour from their tier automatically, and existing keys stay pinned. The map legend shows the tiers.

## Layout rules (don't break these)
- The left route lines up only if these widths stay as they are: section signs 95%, lanes 94%, map and last stop 100%. The column position lives in `ROUTE` in `profile/subway/lib.js`.
- Every `<summary>` image is wrapped in `<picture>`, so GitHub doesn't turn it into a link, and has `align="middle"`, so the ▶ arrow sits centred. `lines.py` does both.
- GitHub always draws a ▶ beside each dropdown and leaves about 16 px between `<details>` blocks. Neither can be removed.

## Rules
- **Real content only.** No invented numbers, dates, users or claims. Facts come from `ledger.json`, the repos' READMEs, or the owner's resume (only the file the owner names).
- **Privacy.** Never put an email, phone number, token or private commit message on the page. Private repo names appear only via `private_allow`.
- **Commits on this repo carry NO "Co-Authored-By: Claude" or any other AI attribution line.** The owner asked for this, because it lists the AI as a repo contributor.
- **Copy** is plain lowercase, like the intro. No emoji, no "X, not Y" phrasing.
- **Images:** each loop ≤ 3 MB, starts on a finished-looking frame, and stays readable at 360 px wide (no text under 34 px at the 1200 px stage).
- **Ask before pushing** unless the owner already said to.

## Tools
- Python 3 with Pillow.
- Node with Playwright: `npm install --prefix profile/subway --no-save playwright && npx --prefix profile/subway playwright install chromium`. Locally you can point `NODE_PATH` at an existing install.
- `gh`, logged in as rohankilaru-ai.
- ffmpeg, only for footage. Footage frames go in `profile/subway/.cache/` (gitignored).
