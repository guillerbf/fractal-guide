import argparse
import sys
from dotenv import load_dotenv


def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog="fractal-guide",
        description="Fractal tourism guide MVP using OpenAI",
    )
    subparsers = parser.add_subparsers(dest="command")

    # ping command
    subparsers.add_parser("ping", help="Health check")

    # version command
    subparsers.add_parser("version", help="Show version")

    return parser


def cmd_ping() -> int:
    print("pong")
    return 0


def cmd_version() -> int:
    # Defer import to avoid hard dependency on package metadata at import time
    try:
        from importlib.metadata import version, PackageNotFoundError  # type: ignore
    except Exception:  # pragma: no cover - extremely unlikely
        print("unknown")
        return 0

    try:
        print(version("fractal-guide"))
    except PackageNotFoundError:
        print("0.1.0")
    return 0


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    args = build_parser().parse_args(argv)
    if args.command == "ping":
        return cmd_ping()
    if args.command == "version":
        return cmd_version()

    # Default behavior: show help when no command is provided
    build_parser().print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())


