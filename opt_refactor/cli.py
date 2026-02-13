"""ATOC — command-line interface for processing KML files."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .generator import generate_styled_kml_file
from .parser import parse_kml_file


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="opt-refactor",
        description="ATOC: Transform raw KML exports into visually styled KML files.",
    )
    p.add_argument("input", help="Path to the input .kml file")
    p.add_argument(
        "-o", "--output",
        default=None,
        help="Output .kml file path (default: <input>_styled.kml)",
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


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    input_path: str = args.input
    output_path: str = args.output
    if output_path is None:
        if input_path.lower().endswith(".kml"):
            output_path = input_path[:-4] + "_styled.kml"
        else:
            output_path = input_path + "_styled.kml"

    # Parse
    print(f"[ATOC] Reading {input_path} ...")
    try:
        features = parse_kml_file(input_path)
    except FileNotFoundError:
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error parsing KML: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"[ATOC] Found {len(features)} features")

    # Generate
    generate_styled_kml_file(
        features,
        output_path,
        use_folders=not args.no_folders,
        document_name=args.name,
    )
    print(f"[ATOC] Styled KML written to {output_path}")


if __name__ == "__main__":
    main()
