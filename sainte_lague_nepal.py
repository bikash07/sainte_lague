#!/usr/bin/env python3
"""CLI wrapper for the web app's seat allocation service."""

from __future__ import annotations

import argparse
import sys

from app.service import get_allocation_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute Nepal HoR proportional seats using Sainte-Lague."
    )
    parser.add_argument("--seats", type=int, default=110)
    parser.add_argument("--threshold", type=float, default=3.0)
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    args = parse_args()
    try:
        report = get_allocation_report(total_seats=args.seats, threshold=args.threshold)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}")
        return 1

    print(f"Total PR votes (all parties): {report.total_votes_all_parties:,}")
    print(f"Eligible PR votes used for allocation: {report.total_votes_eligible:,}")
    print()
    print("Seat allocation:")
    for row in report.rows:
        if row.seats == 0:
            continue
        print(
            f"{row.party}: {row.seats} seat(s) | "
            f"votes={row.votes:,} | share={row.vote_share:.2f}%"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
