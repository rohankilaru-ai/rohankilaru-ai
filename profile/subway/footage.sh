#!/usr/bin/env bash
# footage.sh <film id | drone>: cuts the source clip into frames under .cache/<id>/ (skipped when already there; FORCE=1 redoes it)
set -euo pipefail
cd "$(dirname "$0")"
id="$1"; dir=".cache/$id"; mkdir -p "$dir"
[ -z "${FORCE:-}" ] && [ -f "$dir/f_001.jpg" ] && exit 0
if [ "$id" = drone ]; then
  [ -f "$dir/src.mp4" ] || curl -sfL -o "$dir/src.mp4" "https://raw.githubusercontent.com/rohankilaru-ai/rohan_drone_club/HEAD/Minecraft_stitch_test.mp4"
  ffmpeg -v error -y -i "$dir/src.mp4" -vf "setpts=PTS/2.5,fps=20,scale=840:-2" -q:v 5 "$dir/f_%03d.jpg"
  exit 0
fi
read -r src start dur speed crop width < <(node -e "
  global.window={};require('./films.js');const f=window.FILMS['$id'];
  console.log(f.src.replace('~',process.env.HOME),f.start,f.end-f.start,f.speed,f.crop[2]+':'+f.crop[3]+':'+f.crop[0]+':'+f.crop[1],f.layout==='side'?Math.round((f.screenW||540)*1.5):1632)")
ffmpeg -v error -y -ss "$start" -t "$dur" -i "$src" -vf "crop=$crop,setpts=PTS/$speed,fps=20,scale='min(iw,$width)':-2" -q:v 4 "$dir/f_%03d.jpg"
