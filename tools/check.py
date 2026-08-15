#!/usr/bin/env python3
"""Geometry checks for the built nav log.

Paper forms fail silently: a column that is 2 mm too wide still renders, it
just does not line up after cutting. These assertions pin the numbers the
README promises, for every variant tools/build.py emits.

SPDX-License-Identifier: CC0-1.0
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import VARIANTS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# WeasyPrint lays out in CSS pixels (96 per inch), not points.
PX_PER_MM = 96 / 25.4
A4_LANDSCAPE_PX = (297 * PX_PER_MM, 210 * PX_PER_MM)

SLIP_W_MM = 93.0
SLIP_H_MM = 175.0
GUTTER_MM = 4.0
PAGE_W_MM = 297.0
PAGE_H_MM = 210.0
SLIPS_PER_PAGE = 3
PAGES = 2

# The clamp's wire handle, measured off a KB-1 mini with a rule against the
# sheet's edges and calibrated on the slip's own 93 mm width. It is a flat
# loop lying on the paper, so it obstructs four strips, not one band: an upper
# bar along the top edge, a lower bar, and the two side rails joining them.
#
# Two photos of the same board gave the rails at 14.5-17.2 / 77.3-80.0 mm and
# at 17.4-20.1 / 78.6-81.2 mm, and the lower bar at 16.4-19.8 / 15.5-18.5 mm.
# The sheet sits about 3 mm further left in one than the other; the figures
# below are the union plus a little tolerance for that. Re-measure these for a
# different kneeboard and the layout will be held to whatever you find.
WIRE_TOP_MM = 15.5  # top of the lower bar — also the header's content floor
WIRE_BOTTOM_MM = 20.0  # bottom of the lower bar — the first write-on field
WIRE_HEAD_MM = 2.0  # bottom of the upper bar, along the sheet's top edge
WIRE_LEFT_MM = 12.0  # outer edge of the left-hand rail
WIRE_RAIL_MM = 8.0  # rail width, tolerance for lateral slack included
WIRE_RIGHT_MM = 81.0  # outer edge of the right-hand rail

# Everything the handle covers, as (x0, y0, x1, y1) in mm from a slip's top
# left corner. Nothing printed may intersect any of these.
WIRE_FOOTPRINT = (
    (WIRE_LEFT_MM, 0.0, WIRE_RIGHT_MM, WIRE_HEAD_MM),  # upper bar
    (WIRE_LEFT_MM, WIRE_TOP_MM, WIRE_RIGHT_MM, WIRE_BOTTOM_MM),  # lower bar
    (WIRE_LEFT_MM, 0.0, WIRE_LEFT_MM + WIRE_RAIL_MM, WIRE_BOTTOM_MM),  # left rail
    (WIRE_RIGHT_MM - WIRE_RAIL_MM, 0.0, WIRE_RIGHT_MM, WIRE_BOTTOM_MM),  # right rail
)

TOL_MM = 0.15

failures: list[str] = []


def check(condition: bool, message: str) -> bool:
    if condition:
        print(f"  ok    {message}")
    else:
        print(f"  FAIL  {message}")
        failures.append(message)
    return condition


def close(a: float, b: float, tol: float = TOL_MM) -> bool:
    return abs(a - b) <= tol


def slips_of(page) -> list:
    """Every .slip box on a page, in document order.

    element_tag rather than element.tag, so the ::before cut frame — which
    shares the same element — is not counted as a second slip.
    """
    return [
        box
        for box in page._page_box.descendants()
        if box.element is not None
        and "slip" in (box.element.get("class") or "").split()
        and box.element_tag == "section"
    ]


def boxes_of(slip, name: str) -> list:
    """Every box inside a slip whose element carries the given class."""
    return [
        box
        for box in slip.descendants()
        if box.element is not None
        and name in (box.element.get("class") or "").split()
    ]


def mm_rect(box, slip) -> tuple[float, float, float, float]:
    """A box's border rectangle, in mm from the slip's top left corner."""
    x = (box.border_box_x() - slip.border_box_x()) / PX_PER_MM
    y = (box.border_box_y() - slip.border_box_y()) / PX_PER_MM
    return (x, y, x + box.border_width() / PX_PER_MM, y + box.border_height() / PX_PER_MM)


def intersects(a, b, tol: float = 0.05) -> bool:
    """Do two (x0, y0, x1, y1) rectangles overlap by more than a hair?

    The tolerance keeps a box that merely touches an edge — a column ending
    exactly where a rail begins — from reading as an overlap.
    """
    return (
        a[0] < b[2] - tol
        and b[0] < a[2] - tol
        and a[1] < b[3] - tol
        and b[1] < a[3] - tol
    )


def fmt(rect) -> str:
    return f"[{rect[0]:.1f}-{rect[2]:.1f} x {rect[1]:.1f}-{rect[3]:.1f} mm]"


def label(box) -> str:
    """Something recognisable to name a box by in a failure message."""
    text = (box.element.text or "").strip() if box.element is not None else ""
    classes = " ".join((box.element.get("class") or "").split()) or box.element_tag
    return f"{classes!r}{f' ({text!r})' if text else ''}"


def rows_of(slip, *classes: str) -> list:
    """Every <tr> in a slip carrying all of the given classes."""
    wanted = set(classes)
    return [
        box
        for box in slip.descendants()
        if box.element is not None
        and box.element_tag == "tr"
        and wanted <= set((box.element.get("class") or "").split())
    ]


def check_variant(variant) -> None:
    from weasyprint import HTML

    html = ROOT / "build" / f"navlog-{variant.tag}.html"
    if not html.exists():
        sys.exit(f"{html.relative_to(ROOT)} missing — run `make` first")

    waypoint_blocks = variant.waypoints  # name row + two data rows: one leg each
    wp_rows = waypoint_blocks + 1  # those, plus the bare destination row

    print(f"=== {variant.tag}: {variant.note} ===")

    document = HTML(filename=str(html)).render()

    print("page setup")
    check(len(document.pages) == PAGES, f"{PAGES} pages (front and back)")
    for number, page in enumerate(document.pages, 1):
        check(
            close(page.width, A4_LANDSCAPE_PX[0], 1.0)
            and close(page.height, A4_LANDSCAPE_PX[1], 1.0),
            f"page {number} is A4 landscape "
            f"({page.width / PX_PER_MM:.1f} x {page.height / PX_PER_MM:.1f} mm)",
        )

    print("slip geometry")
    for number, page in enumerate(document.pages, 1):
        slips = slips_of(page)
        check(len(slips) == SLIPS_PER_PAGE, f"page {number} carries {SLIPS_PER_PAGE} slips")
        if len(slips) != SLIPS_PER_PAGE:
            continue

        for index, slip in enumerate(slips):
            width = slip.border_width() / PX_PER_MM
            height = slip.border_height() / PX_PER_MM
            check(
                close(width, SLIP_W_MM) and close(height, SLIP_H_MM),
                f"page {number} slip {index + 1} is "
                f"{width:.2f} x {height:.2f} mm (want {SLIP_W_MM} x {SLIP_H_MM})",
            )

        # Cut lines must be mirror symmetric, so the two sides register
        # whichever edge the printer flips on.
        left = slips[0].border_box_x() / PX_PER_MM
        right = PAGE_W_MM - (
            slips[-1].border_box_x() + slips[-1].border_width()
        ) / PX_PER_MM
        check(
            close(left, right),
            f"page {number} left/right margins match ({left:.2f} vs {right:.2f} mm)",
        )

        top = slips[0].border_box_y() / PX_PER_MM
        bottom = PAGE_H_MM - (
            slips[0].border_box_y() + slips[0].border_height()
        ) / PX_PER_MM
        check(
            close(top, bottom),
            f"page {number} top/bottom margins match ({top:.2f} vs {bottom:.2f} mm)",
        )

        pitch = (slips[1].border_box_x() - slips[0].border_box_x()) / PX_PER_MM
        check(
            close(pitch, SLIP_W_MM + GUTTER_MM),
            f"page {number} slip pitch is {pitch:.2f} mm "
            f"(want {SLIP_W_MM + GUTTER_MM})",
        )

    print("content fits")
    for number, page in enumerate(document.pages, 1):
        for index, slip in enumerate(slips_of(page)):
            # Slack of half a collapsed table rule: those straddle the cut
            # line by design, and anything at that scale is well under the
            # precision of a paper guillotine.
            slack = 0.15 * PX_PER_MM
            limit_x = slip.border_box_x() + slip.border_width()
            limit_y = slip.border_box_y() + slip.border_height()
            overflow = [
                box
                for box in slip.descendants()
                if box is not slip
                and (
                    box.border_box_x() + box.border_width() > limit_x + slack
                    or box.border_box_y() + box.border_height() > limit_y + slack
                )
            ]
            check(
                not overflow,
                f"page {number} slip {index + 1}: nothing overflows the cut line"
                + (f" ({len(overflow)} boxes do)" if overflow else ""),
            )

    print("clamp wire")
    for number, page in enumerate(document.pages, 1):
        for index, slip in enumerate(slips_of(page)):
            where = f"page {number} slip {index + 1}"

            # Nothing in the clamp zone may sit under the handle. Only the
            # <span>s are tested: they are the labels and boxes, the only
            # things in that block carrying ink. The divs around them are
            # bare containers, and the clamp block's own bottom rule is the
            # divider at 21 mm, below the whole footprint.
            clamps = boxes_of(slip, "clamp")
            if check(len(clamps) == 1, f"{where} has one clamp block"):
                fouled = [
                    (span, rect)
                    for span in clamps[0].descendants()
                    if span.element_tag == "span"
                    for rect in WIRE_FOOTPRINT
                    if intersects(rect, mm_rect(span, slip))
                ]
                check(
                    not fouled,
                    f"{where}: nothing in the clamp zone lies under the wire"
                    + (
                        "".join(
                            f"\n          {label(span)} at {fmt(mm_rect(span, slip))}"
                            f" fouls {fmt(rect)}"
                            for span, rect in fouled
                        )
                        if fouled
                        else ""
                    ),
                )

            # The first block you write on in the cockpit must start past the
            # handle, or its lower bar sits on top of T/O and LDG.
            infos = boxes_of(slip, "info")
            if check(len(infos) == 1, f"{where} has one info block"):
                starts = (infos[0].border_box_y() - slip.border_box_y()) / PX_PER_MM
                check(
                    starts >= WIRE_BOTTOM_MM,
                    f"{where}: first write-on block starts at {starts:.2f} mm, "
                    f"clear of the wire at {WIRE_BOTTOM_MM} mm",
                )

    print("form contents")
    for number, page in enumerate(document.pages, 1):
        for index, slip in enumerate(slips_of(page)):
            where = f"page {number} slip {index + 1}"

            # Two counts, not one: the destination row is a name row with no
            # data rows under it, and that asymmetry is the point.
            names = rows_of(slip, "wp")
            legs = rows_of(slip, "data", "upper")
            check(len(names) == wp_rows, f"{where} has {wp_rows} waypoint name rows")
            check(
                len(legs) == waypoint_blocks,
                f"{where} has {waypoint_blocks} legs "
                f"(the last waypoint carries no data rows)",
            )

            # The free-text block absorbs leftover height, so the table must end
            # exactly on the bottom cut line. If it does not, that block hit its
            # min-height and the vertical budget no longer adds up.
            last = rows_of(slip, "wp", "last")
            if check(len(last) == 1, f"{where} has one destination row"):
                gap = (
                    slip.border_box_y()
                    + slip.border_height()
                    - (last[0].border_box_y() + last[0].border_height())
                ) / PX_PER_MM
                check(
                    close(gap, 0.0),
                    f"{where}: table ends flush with the bottom cut line "
                    f"({gap:.2f} mm short)",
                )

    print()


def main() -> None:
    for variant in VARIANTS:
        check_variant(variant)

    if failures:
        print(f"{len(failures)} check(s) failed")
        sys.exit(1)
    print("all checks passed")


if __name__ == "__main__":
    main()
