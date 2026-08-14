# VFR Nav Log — Kneeboard Template

A compact VFR navigation log that prints **three slips to a landscape A4 sheet**,
duplex, and cuts into **93 × 185 mm** double-sided slips. Sized for the
[Design4Pilot KB-1 mini](https://www.design4pilots.de/) kneeboard: the slips fit
under the clamp, and the spare ones stow under the front flap so they do not
flap around in a draughty cockpit.

![One slip](docs/preview-slip.png)

The form is designed around one awkward fact about small kneeboards: **the clamp
covers the top ~16 mm of the sheet.** So the top strip carries only
identification you fill in on the ground and glance at later, and everything you
actually write in the air — take-off and landing times, QNH, the ATIS letter —
starts below it.

## Print it

Grab [`build/NavLog-A4-3up.pdf`](build/NavLog-A4-3up.pdf) and print with:

| setting | value |
|---|---|
| paper | A4, plain |
| orientation | landscape |
| scale | **100 % / actual size** — *not* "fit to page" or "shrink to fit" |
| duplex | two-sided, **flip on short edge** |
| margins | none / minimum (the PDF already has 12.5 × 5 mm) |

Scaling is the one that bites: at "fit to page" the slips come out a few
millimetres narrow and stop matching the clamp.

**Check the flip before you cut.** Every slip prints a faint `▲ TOP` in its top
right corner. Hold a printed sheet up to the light — the `▲ TOP` marks on both
sides must be at the *same* end. If the back is upside down, either switch the
duplex option to the other edge, or print
[`build/NavLog-A4-3up-longedge.pdf`](build/NavLog-A4-3up-longedge.pdf), which is
the same document with the back page pre-rotated.

## Cut it

Cut along the thin frame around each slip. The three slips are laid out
symmetrically on the page — equal margins left and right, equal top and bottom —
so the front and back register exactly and one cut goes through both sides
cleanly. Slip pitch is 97 mm (93 mm slip + 4 mm gutter).

Six slips per printed sheet: three fronts and three backs, giving you three
double-sided nav logs, or one out-and-back per slip.

## The form

```
┌──────────────────────────────────────────┐  ─┐
│  FROM [    ] RWY [  ]  TO [    ] RWY [ ] │   │ clamp zone —
│  DATE ______  A/C ______        ▲ TOP    │   │ ground info only
│                                          │  ─┘
├──────────────────────────────────────────┤
│  T/O [        ]   LDG [        ]         │  first block clear
│  QNH/INFO  DEP Q [  ] ◯   DEST Q [  ] ◯  │  of the clamp
├──────────────────────────────────────────┤
│  DEP _________     DEST _________        │  frequencies
│  ______________________________________  │
├────┬─────┬───┬────┬────┬────┬─────┬──────┤
│ CL │ MAX │ALT│ MC │ GS │LEG │ MIN │ ETO  │
│    │ MIN │   │ MH │DIST│TOT │ ACT │ ATO  │
├────┴─────┴───┴────┴────┴────┴─────┴──────┤
│  waypoint / notes              │ W/V     │
│  ...  7 waypoint blocks  ...             │
├──────────────────────────────────────────┤
│  notes                                   │
└──────────────────────────────────────────┘
```

| field | what goes in it |
|---|---|
| `FROM` / `TO` / `RWY` | departure and destination, with the runway pair |
| `DATE` / `A/C` | for filing the slip after the flight |
| `T/O` / `LDG` | actual times, written in the cockpit |
| `QNH  Q [ ]` | last two digits — the leading ones are obvious in context |
| `◯` | the ATIS information letter, circled |
| `DEP` / `DEST` freq | tower or info frequency at each end |
| free lines | en-route FIS and any other frequencies |
| `CL` | airspace class letter (C / D / E / R). Optional, but it makes the altitude limits next to it mean something |
| `MAX ALT` / `MIN ALT` | the airspace band you have to stay inside |
| `ALT` | planned cruising altitude for the leg |
| `MC` / `MH` | magnetic course and heading |
| `GS` / `DIST` | planned groundspeed and leg distance — your in-flight cross-check |
| `LEG` / `TOTAL` | leg time and accumulated time en route |
| `MIN FUEL` / `ACT. FUEL` | fuel required at this point, and what the gauge says |
| `ETO` / `ATO` | estimated and actual time overhead. Minutes alone is usually enough |
| waypoint row | the waypoint, plus whatever the leg needs (`! EDR A15`, `≈ Weser`, `→ Alsfeld`) |
| `W/V` | wind direction/speed, e.g. from SkyDemon. Optional |
| notes | fuel and mass, squawk, clearances, anything else |

Seven waypoint blocks. Typical cross-country routes use four to six, so there is
room to spare without wasting a whole slip on blank grid.

## Customise it

Everything dimensional lives in the `:root` block at the top of
[`src/navlog.css`](src/navlog.css) — slip size, the height of each block, and
the eight column widths. The notes block at the bottom takes up whatever height
is left over, so changing any block above it does not cascade into retuning
everything else.

A few you might want:

```css
--slip-h: 185mm;   /* 177mm matches the original spreadsheet version */
--h-clamp: 18mm;   /* grow this if your kneeboard's clamp reaches further */
--c-eto: 16mm;     /* the eight column widths must add up to --slip-w */
```

If you change a column width, run `make check` — it will tell you if the columns
no longer add up and the grid has drifted off the cut line.

## Build it

Needs Python and [WeasyPrint](https://weasyprint.org/).

```sh
pip install weasyprint pypdf
make          # -> build/navlog.html and both PDFs
make check    # assert the geometry still matches this README
make preview  # regenerate docs/preview-*.png
```

`src/slip.html` is the single source of truth for the form — one slip, with the
waypoint block written once. `tools/build.py` stamps it out three times per
page, two pages, and inlines the CSS into `build/navlog.html`. That generated
file is self-contained, so you can also just open it in a browser and print from
there; the result is close, though a browser's own margin handling makes the PDF
the more reliable route.

`make check` asserts what this README promises: two A4 landscape pages, three
93 × 185 mm slips each, 97 mm pitch, symmetric margins, nothing overhanging a
cut line, seven waypoint blocks per slip. Paper forms fail quietly — a column
2 mm too wide still renders, it just stops lining up — so the numbers are pinned
in code rather than in prose alone.

## What changed from the spreadsheet version

The original was an `.xlsx` ([`legacy/NavLog.xlsx`](legacy/NavLog.xlsx), kept
for reference). Changes in this version, all driven by what actually got
scribbled into the margins of real flights:

- **Clamp zone.** T/O, LDG and the frequencies moved out from under the clamp.
- **QNH and the ATIS letter** got printed fields instead of being squeezed into
  the blank area.
- **Runways** got boxes next to `FROM` / `TO` instead of being crammed in after
  the ICAO code.
- **`W/V`** got a labelled slot at the end of each waypoint row.
- **Airspace class** got a narrow `CL` box, instead of drawing one by hand
  around the letter each time.
- **`TIME` split** into `LEG` and `TOTAL`.
- **Notes lines** at the bottom, for the fuel and mass figures that used to go
  wherever there was space.
- Seven waypoint blocks, all of them complete — the old sheet's eighth
  `WAYPOINT:` label was orphaned by the page break with no data rows under it.
- Plain-text source: the layout is now diffable and builds reproducibly, instead
  of depending on how Excel or LibreOffice feels about rendering the sheet.

Column order and the top/bottom split of every existing field are unchanged, so
the form still reads the way it always did.

## Licence

[![CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

Licensed under [Creative Commons Attribution-ShareAlike 4.0
International](https://creativecommons.org/licenses/by-sa/4.0/). Use it, print
it, change it, publish your changes — just credit the original and keep the same
licence. Full text in [`LICENSE`](LICENSE).

## Not a legal document

This is a piece of paper for organising your own planning. It is not an approved
form and it replaces nothing: check your own figures, and comply with whatever
your operating rules and the aircraft flight manual actually require.
