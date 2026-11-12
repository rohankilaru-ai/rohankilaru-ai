# Updating this profile (for any AI agent or person)

This repo is Rohan's GitHub profile. `README.md` is the page; everything on it is an image drawn in a New York subway-diagram style (Vignelli 1972 language, no MTA marks). Read this file fully, then do what the owner asked. Keep changes small and in the style that's here.

## What updates by itself (don't do these by hand)
A GitHub Action (`.github/workflows/subway.yml`) runs every morning:
1. `python profile/lines.py` fetches commit data into `profile/data/ledger.json` (every branch, Pacific time).
2. `bash profile/subway/render.sh --daily` redraws the map (`log.webp`), every station sign (`lane-*.png`) and the section signs (`sign-*.png`).
3. `python profile/lines.py --readme` rewrites the README between `<!-- log:start/end -->` and `<!-- work:start/end -->`.
4. The images are force-pushed to the `subway-daily` branch (one commit, so history doesn't grow). The README points at them with `https://github.com/rohankilaru-ai/rohankilaru-ai/raw/subway-daily/...`.

Ranking is automatic: the map keeps the `max_lines` projects with the most commits in the last `active_days`, newest work first. When a newer project passes one, the weakest drops to "past projects" (faded). A new PUBLIC repo with commits gets its own line, sign and colour the next morning. A PRIVATE repo appears only after it's added to `private_allow`. The Action needs the `PROFILE_TOKEN` secret (a fine-grained token with read access to the owner's repos); without it, it does nothing.

## The one file to edit: `profile/data/lines.json`
- `projects`: the named projects. Fields: `key` (lowercase repo name), `name`, `repo` (`owner/name`), `line` (one plain lowercase sentence, ≤ 48 chars), `link`:
  - `"film"`: a **building now** project. It opens its film in place under the map. Needs a `film` object: `src`, `alt`, `note` (markdown), optional `star: true` (public repos only).
  - `"card"`: a side or past project. It opens `assets/subway/card-<key>.webp`.
  - a URL: an auto-discovered repo with no card yet. Clicking opens the repo.
- `work`: past jobs, shown as stops under "past work". Fields: `key`, `name`, `line`, `role`, `color_key`, and `body` (a list of `{img, alt}` and `{text}` items, in order).
- `max_lines`, `active_days`, `hide` (never shown), `private_allow`, `ignore` (never fetched).

## Recipes
Run them from the repo root. After any change, run `profile/update.sh` (it fetches, redraws and rewrites the README), look at the result, then commit.

- **Promote a project to "building now"**: set its `link` to `"film"` and add a `film`. Make the film with `profile/subway/film.html` + `films.js` (add an entry with its footage; `footage.sh` extracts frames), render it with `bash profile/subway/render.sh <id>`, then add the new branch to `INTRO_BRANCHES` at the top of `profile/subway/intro.html` and render `intro`.
- **Give a project a card**: add it to `profile/subway/cards.js` (what it is, one note, how-it-works steps, optional demo). Facts must come from the repo's README or the owner. Render with `bash profile/subway/render.sh card-<key>` and set `link: "card"`.
- **Add a job to past work**: add an entry to `work` (and a colour for its `color_key` in `profile/subway/colors.js`, past-work tier = muted). Record or make its clips, render them, then run `bash profile/subway/render.sh signs`.
- **Hide or show something**: edit `hide` or `private_allow`.
- **Change the intro or contact tags**: `profile/subway/intro.html` (keep the sentence text in sync with the README alt text), `tag.html` via `render.sh connect`. The contact links live in `README.md` itself.

## Colours (`profile/subway/colors.js`)
| Tier | Look | Projects |
|---|---|---|
| building now | brightest | vel yellow, lea pink |
| side projects | mid | jobradar green, sportsgrid blue |
| past work | muted | climate plans sage, ariento dusty blue |
| past projects | grey | faded ones |

A new key gets a colour from its tier automatically. Existing keys stay pinned.

## Rules
- Real content only: no invented numbers, dates, users or claims. Facts come from `ledger.json`, the repos' READMEs, or the owner's resume (only the file the owner names).
- Never put an email, phone number, token or private commit message on the page. Private repo names appear only via `private_allow`.
- Copy is plain and lowercase, like the intro. No emoji, no "X, not Y" phrasing.
- Every loop: ≤ 3 MB, the first frame already looks finished, readable at 360 px wide (no text under 34 px at the 1200 px stage).
- Don't push to the owner's GitHub without them saying so.

## Tools
Python 3 with Pillow; Node with Playwright (`npm install --prefix profile/subway --no-save playwright && npx --prefix profile/subway playwright install chromium`); `gh` logged in; ffmpeg only for footage.
