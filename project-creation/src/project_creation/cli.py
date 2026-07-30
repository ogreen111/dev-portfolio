"""Command-line entry point."""

from __future__ import annotations

import argparse
from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        prog="project-creation",
        description="Post-award Cyber project provisioning",
    )


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
