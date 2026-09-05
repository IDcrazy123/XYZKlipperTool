"""Retired compatibility entrypoint; use archive_pixel_diagnostics.py instead."""

from __future__ import annotations

import sys


def main() -> int:
    """Fail closed without constructing synthetic calibration or reading an image."""
    print(
        "explore_picture.py is retired; use scripts/archive_pixel_diagnostics.py "
        "with explicit source roots, manifests, output directory, and ROI.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
