#!/usr/bin/env bash
# Regenerate the README preview images from the built PDF.
# The 7L variant is the one shown; 6L differs only in the grid below the
# frequencies.
# SPDX-License-Identifier: CC0-1.0
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p docs

PDF=build/NavLog-A4-3up-7L.pdf

pdftoppm -r 150 -png -f 1 -l 1 "$PDF" docs/preview-sheet
mv docs/preview-sheet-1.png docs/preview-sheet.png

# A single slip at its cut size, for reading the form itself.
# Page geometry: 5 mm left margin, 17.5 mm top margin, slip 93 x 175 mm.
# Tenths of a millimetre throughout, so integer division stays honest.
pdftoppm -r 300 -png -f 1 -l 1 \
  -x $((300 * 50 / 254)) -y $((300 * 175 / 254)) \
  -W $((300 * 930 / 254)) -H $((300 * 1750 / 254)) \
  "$PDF" docs/preview-slip
mv docs/preview-slip-1.png docs/preview-slip.png

echo "wrote docs/preview-sheet.png docs/preview-slip.png"
