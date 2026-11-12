#!/usr/bin/env bash
# Renders the subway profile pieces into assets/subway/.
#   profile/subway/render.sh --daily     data + log.webp + every lane-<key>.png (projects, retired, past work) + the four section signs; prints the lane order (keys, most recent first) on stdout
#   profile/subway/render.sh --all       everything (needs ffmpeg and the footage; see footage.sh)
#   profile/subway/render.sh <name>...   only these: intro linkedin connect log lanes signs vel lea cp-equity cp-before-after cp-similar ariento cards card-<key>
# Needs node + playwright (npx playwright install --with-deps chromium) and python3 with pillow. PY overrides the python.
set -euo pipefail
cd "$(dirname "$0")"
OUT=../../assets/subway
export PY="${PY:-python3}"
mkdir -p "$OUT"
r() { node render.cjs "$@" 1>&2; }                    # all render chatter goes to stderr
"$PY" make_data.py 1>&2
lanes() { while read -r k; do [ -n "$k" ] && r "lane.html?key=$k" "$OUT/lane-$k.png"; done < order.txt; }
one() {
  case "$1" in
    log)      r log.html "$OUT/log.webp" 8 20 ;;
    lanes)    lanes ;;
    intro)    r intro.html "$OUT/intro.webp" 7 24 ;;
    linkedin) r linkedin.html "$OUT/linkedin.webp" 5 20 640 ;;
    connect)  r connect.html "$OUT/sign-connect.webp" 6 20
              for n in linkedin x github; do r "xfer.html?t=$n" "$OUT/xfer-$n.png" 0 0 600; done
              r "tag.html?t=linkedin&u=in/rohankilaru" "$OUT/tag-linkedin.webp" 5 20 640
              r "tag.html?t=follow+on+github" "$OUT/tag-github.webp" 5 20 640
              r "tag.html?t=work+with+me" "$OUT/tag-collab.webp" 5 20 640
              r "tag.html?t=x&u=@roh_kil" "$OUT/tag-x.webp" 5 20 640
              r "tag.html?t=star+on+github&icon=star" "$OUT/tag-star.png" 0 0 640 ;;
    daysigns) r "sign.html?t=building+now&keys=@now" "$OUT/sign-building.png"
              r "sign.html?t=side+projects&keys=@side" "$OUT/sign-side.png" ;;
    signs)    one daysigns
              r "sign.html?t=past+work&keys=@work" "$OUT/sign-work.png"
              r "sign.html?t=past+projects&keys=retired" "$OUT/sign-projects.png"
              while read -r k; do [ -n "$k" ] && r "lane.html?key=$k" "$OUT/lane-$k.png"; done < work.txt ;;
    vel|lea|cp-equity|cp-before-after|cp-similar|ariento)
              ./footage.sh "$1" 1>&2; MAX_MB=2.4 r "film.html?id=$1" "$OUT/$1.webp" "$(node -e "global.window={};require('./films.js');console.log(window.FILMS['$1'].secs)")" 20 ;;
    cards)    for k in jobradar-ai dailygames-slackbot neetcode-submissions evision kalshi-ev-extension rohan_drone_club; do one "card-$k"; done ;;
    card-*)   k="${1#card-}"; [ "$k" = rohan_drone_club ] && ./footage.sh drone 1>&2
              MAX_MB=2.2 r "card.html?key=$k" "$OUT/card-$k.webp" "$(node -e "global.window={};require('./cards.js');console.log(window.CARDS['$k'].secs||6)")" 15 ;;
    *) echo "unknown piece: $1" 1>&2; exit 2 ;;
  esac
}
case "${1:---daily}" in
  --daily) one log; one lanes; one signs; cat order.txt ;;
  --all)   for p in intro linkedin connect log lanes signs vel lea cp-equity cp-before-after cp-similar ariento cards; do one "$p"; done; cat order.txt ;;
  *)       for p in "$@"; do one "$p"; done ;;
esac
