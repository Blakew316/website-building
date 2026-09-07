#!/usr/bin/env bash
# Rebuild the Meridian Local site from the archived zips.
set -euo pipefail
cd "$(dirname "$0")"

SRC="${SRC:-.build-src}"
if [ ! -d "$SRC/www.townsquareinteractive.com" ]; then
  echo "▸ unpacking archive into $SRC"
  mkdir -p "$SRC"
  for z in tsi-*.zip; do unzip -oq "$z" -d "$SRC"; done
fi

echo "▸ extracting content"
python3 build/extract.py --src "$SRC" --out content

echo "▸ rendering site"
python3 build/site.py --content content --out site

echo "▸ checking links"
python3 build/checklinks.py site
