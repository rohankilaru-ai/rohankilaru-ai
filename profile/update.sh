#!/usr/bin/env bash
# One command to refresh everything that comes from data: commits -> map, signs, README.
#   profile/update.sh            fetch with your gh login, redraw, rewrite the README
#   profile/update.sh --offline  redraw from the saved profile/data/ledger.json
set -euo pipefail
cd "$(dirname "$0")/.."
[ "${1:-}" = "--offline" ] || python3 profile/lines.py
bash profile/subway/render.sh --daily >/dev/null
python3 profile/lines.py --readme
echo "done: look at README.md and assets/subway/, then commit. (the daily Action does this on its own once PROFILE_TOKEN is set)"
