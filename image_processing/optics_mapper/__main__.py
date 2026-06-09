"""
CLI entry point: python -m optics_mapper [options] image1 [image2 ...]

Single image  → Phase 1 (grid detection + OCR)
Multiple images → Phase 2 (multi-image registration + fusion)
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        prog="python -m optics_mapper",
        description="Map optical components on a breadboard from photos.",
    )
    parser.add_argument(
        "images", nargs="+", metavar="IMAGE",
        help="One image (Phase 1) or multiple images (Phase 2)",
    )
    parser.add_argument(
        "--out-dir", metavar="DIR", default=None,
        help=(
            "Output directory. "
            "Phase 1 default: same directory as the input image. "
            "Phase 2 default: ./optics_output"
        ),
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Save annotated debug images alongside normal outputs",
    )
    args = parser.parse_args()

    paths = [Path(p) for p in args.images]
    missing = [p for p in paths if not p.exists()]
    if missing:
        print(f"ERROR: files not found: {[str(p) for p in missing]}")
        sys.exit(1)

    if len(paths) == 1:
        from .mapper import process_image
        out_dir = Path(args.out_dir) if args.out_dir else None
        process_image(str(paths[0]), debug=args.debug, out_dir=out_dir)
    else:
        from .register import run_registration
        out_dir = Path(args.out_dir) if args.out_dir else Path("optics_output")
        run_registration(paths, out_dir=out_dir, debug=args.debug)


if __name__ == "__main__":
    main()
