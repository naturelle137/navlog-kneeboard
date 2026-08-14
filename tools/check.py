#!/usr/bin/env python3
"""Geometry checks for the built nav log.

Paper forms fail silently: a column that is 2 mm too wide still renders, it
just does not line up after cutting. These assertions pin the numbers the
README promises.

SPDX-License-Identifier: CC-BY-SA-4.0
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# WeasyPrint lays out in CSS pixels (96 per inch), not points.
PX_PER_MM = 96 / 25.4
A4_LANDSCAPE_PX = (297 * PX_PER_MM, 210 * PX_PER_MM)

SLIP_W_MM = 93.0
SLIP_H_MM = 185.0
GUTTER_MM = 4.0
PAGE_W_MM = 297.0
PAGE_H_MM = 210.0
SLIPS_PER_PAGE = 3
PAGES = 2
WAYPOINTS = 7

TOL_MM = 0.15

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if condition:
        print(f"  ok    {message}")
    else:
        print(f"  FAIL  {message}")
        failures.append(message)


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


def main() -> None:
    from weasyprint import HTML

    html = ROOT / "build" / "navlog.html"
    if not html.exists():
        sys.exit("build/navlog.html missing — run `make` first")

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

    print("form contents")
    for number, page in enumerate(document.pages, 1):
        for index, slip in enumerate(slips_of(page)):
            rows = [
                box
                for box in slip.descendants()
                if box.element is not None
                and "wp" in (box.element.get("class") or "").split()
                and box.element.tag == "tr"
            ]
            check(
                len(rows) == WAYPOINTS,
                f"page {number} slip {index + 1} has {WAYPOINTS} waypoint blocks",
            )

    print()
    if failures:
        print(f"{len(failures)} check(s) failed")
        sys.exit(1)
    print("all checks passed")


if __name__ == "__main__":
    main()
