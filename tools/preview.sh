#!/usr/bin/env bash
# Regenerate the README preview images from the built PDF.
# SPDX-License-Identifier: CC-BY-SA-4.0
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p docs

pdftoppm -r 150 -png -f 1 -l 1 build/NavLog-A4-3up.pdf docs/preview-sheet
mv docs/preview-sheet-1.png docs/preview-sheet.png

# A single slip at its cut size, for reading the form itself.
# Page geometry: 5 mm left margin, 12.5 mm top margin, slip 93 x 185 mm.
pdftoppm -r 300 -png -f 1 -l 1 \
  -x $((300 * 5 / 254 * 10)) -y $((300 * 125 / 254)) \
  -W $((300 * 930 / 254)) -H $((300 * 1850 / 254)) \
  build/NavLog-A4-3up.pdf docs/preview-slip
mv docs/preview-slip-1.png docs/preview-slip.png

echo "wrote docs/preview-sheet.png docs/preview-slip.png"
