"""ATOC — command-line interface for processing KML files."""

from __future__ import annotations

import argparse
import os
import sys

from . import __version__
from .generator import generate_styled_kml_file
from .parser import parse_kml_file

SUPPORTED_EXTENSIONS = (".kml", ".kmz")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="opt-refactor",
        description="ATOC: Transform raw KML/KMZ exports into visually styled KML files.",
    )
    p.add_argument(
        "input",
        help="Path to a .kml/.kmz file, or a folder containing them",
    )
    p.add_argument(
        "-o", "--output",
        default=None,
        help="Output file path (single file) or directory (batch mode)",
    )
    p.add_argument(
        "--no-folders",
        action="store_true",
        default=False,
        help="Do not group features into folders by category",
    )
    p.add_argument(
        "--name",
        default="ATOC Export",
        help="Name for the KML document (default: 'ATOC Export')",
    )
    p.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return p


def _default_output_path(input_path: str) -> str:
    """Generate a default output path: replace extension with _styled.kml."""
    base, ext = os.path.splitext(input_path)
    return base + "_styled.kml"


def _process_file(
    input_path: str,
    output_path: str,
    use_folders: bool,
    document_name: str,
) -> bool:
    """Process a single KML/KMZ file. Returns True on success."""
    print(f"[ATOC] Reading {input_path} ...")
    try:
        features = parse_kml_file(input_path)
    except FileNotFoundError:
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        return False
    except Exception as exc:
        print(f"Error parsing {input_path}: {exc}", file=sys.stderr)
        return False

    print(f"[ATOC] Found {len(features)} features")
    generate_styled_kml_file(
        features,
        output_path,
        use_folders=use_folders,
        document_name=document_name,
    )
    print(f"[ATOC] Styled KML written to {output_path}")
    return True


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    input_path: str = args.input
    output_path: str | None = args.output

    # ── Batch mode: input is a directory ──
    if os.path.isdir(input_path):
        files = sorted(
            f for f in os.listdir(input_path)
            if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
        )
        if not files:
            print(f"No KML/KMZ files found in {input_path}", file=sys.stderr)
            sys.exit(1)

        # Determine output directory
        out_dir = output_path if output_path else input_path
        os.makedirs(out_dir, exist_ok=True)

        print(f"[ATOC] Batch processing {len(files)} file(s) in {input_path}")
        ok, fail = 0, 0
        for fname in files:
            src = os.path.join(input_path, fname)
            dst = os.path.join(out_dir, _default_output_path(fname))
            name = args.name if args.name != "ATOC Export" else os.path.splitext(fname)[0]
            if _process_file(src, dst, not args.no_folders, name):
                ok += 1
            else:
                fail += 1

        print(f"[ATOC] Done — {ok} succeeded, {fail} failed")
        if fail:
            sys.exit(1)
        return

    # ── Single file mode ──
    if output_path is None:
        output_path = _default_output_path(input_path)

    if not _process_file(input_path, output_path, not args.no_folders, args.name):
        sys.exit(1)


if __name__ == "__main__":
    main()
