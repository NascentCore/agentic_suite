"""CLI: aggregate security benchmark manifests."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from security_benchmark.aggregate import aggregate_runs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Security benchmark utilities")
    sub = parser.add_subparsers(dest="cmd", required=True)
    agg = sub.add_parser("aggregate", help="Build markdown table from results tree")
    agg.add_argument("results_root", type=Path)
    args = parser.parse_args(argv)
    if args.cmd == "aggregate":
        print(aggregate_runs(args.results_root))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
