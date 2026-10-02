"""Standard-library command line interface for hartreez."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from hartreez import au, canonical_unit_names, constant_names, convert, unit_aliases
from hartreez.errors import UnitError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hartreez",
        description="Convert atomistic units and query atomic-unit factors and constants.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    conversion = commands.add_parser("convert", help="convert a numeric value between units")
    conversion.add_argument("value", type=float, help="numeric value to convert")
    conversion.add_argument("from_unit", help="source unit expression")
    conversion.add_argument("to_unit", help="destination unit expression")
    conversion.add_argument(
        "--verbose", "-v", action="store_true", help="show a readable conversion equality"
    )

    factor = commands.add_parser("factor", help="query one unit expressed in atomic units")
    factor.add_argument("unit", help="unit expression")

    constant = commands.add_parser("constant", help="query a physical constant in atomic units")
    constant.add_argument("name", help="constant name, for example K_B or HBAR")

    commands.add_parser("units", help="list canonical unit spellings")
    commands.add_parser(
        "aliases", help="list aliases and their canonical spellings or equivalent expressions"
    )
    commands.add_parser("constants", help="list supported physical constant names")
    return parser


def _number(value: float) -> str:
    return format(value, ".15g")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process status code."""

    parser = _parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "convert":
            result = convert(args.value, args.from_unit, args.to_unit)
            if args.verbose:
                print(
                    f"{_number(args.value)} {args.from_unit} = "
                    f"{_number(result)} {args.to_unit}"
                )
            else:
                print(result)
        elif args.command == "factor":
            print(au.factor_from(args.unit))
        elif args.command == "constant":
            print(au.constant(args.name))
        elif args.command == "units":
            print("\n".join(canonical_unit_names()))
        elif args.command == "aliases":
            print("\n".join(f"{alias} -> {canonical}" for alias, canonical in sorted(unit_aliases().items())))
        elif args.command == "constants":
            print("\n".join(constant_names()))
        else:  # pragma: no cover - argparse enforces the command set
            parser.error("a command is required")
    except (UnitError, ValueError, TypeError) as error:
        print(f"hartreez: error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
