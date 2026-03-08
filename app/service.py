from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Dict, List

from app.election_client import fetch_fptp_results, fetch_pr_votes
from app.seat_allocator import AllocationRow, apply_threshold, build_rows, sainte_lague


@dataclass(frozen=True)
class AllocationReport:
    generated_at_utc: str
    total_seats: int
    threshold: float
    total_votes_all_parties: int
    total_votes_eligible: int
    parties_all: int
    parties_eligible: int
    parties_with_seats: int
    rows: List[AllocationRow]


@dataclass(frozen=True)
class FPTPResultRow:
    party: str
    won: int
    leading: int
    total: int
    won_share: float


@dataclass(frozen=True)
class FPTPReport:
    generated_at_utc: str
    total_constituencies: int
    total_won: int
    total_leading: int
    rows: List[FPTPResultRow]


@dataclass(frozen=True)
class DashboardReport:
    generated_at_utc: str
    pr: AllocationReport
    fptp: FPTPReport


def get_allocation_report(total_seats: int, threshold: float) -> AllocationReport:
    party_votes = fetch_pr_votes()
    raw_votes: Dict[str, int] = {item.party: item.votes for item in party_votes}

    eligible_votes = apply_threshold(raw_votes, threshold_percent=threshold)
    seat_alloc = sainte_lague(eligible_votes, total_seats=total_seats) if eligible_votes else {}
    rows = build_rows(eligible_votes, seat_alloc, total_seats=total_seats)

    parties_with_seats = sum(1 for row in rows if row.seats > 0)
    generated_at_utc = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    return AllocationReport(
        generated_at_utc=generated_at_utc,
        total_seats=total_seats,
        threshold=threshold,
        total_votes_all_parties=sum(raw_votes.values()),
        total_votes_eligible=sum(eligible_votes.values()),
        parties_all=len(raw_votes),
        parties_eligible=len(eligible_votes),
        parties_with_seats=parties_with_seats,
        rows=rows,
    )


def get_fptp_report() -> FPTPReport:
    results = fetch_fptp_results()
    total_won = sum(item.won for item in results)
    total_leading = sum(item.leading for item in results)
    total_constituencies = total_won + total_leading

    rows = [
        FPTPResultRow(
            party=item.party,
            won=item.won,
            leading=item.leading,
            total=item.total,
            won_share=(item.won / total_won * 100.0) if total_won else 0.0,
        )
        for item in results
    ]
    rows.sort(key=lambda row: (-row.won, -row.leading, row.party))

    generated_at_utc = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    return FPTPReport(
        generated_at_utc=generated_at_utc,
        total_constituencies=total_constituencies,
        total_won=total_won,
        total_leading=total_leading,
        rows=rows,
    )


def get_dashboard_report(total_seats: int, threshold: float) -> DashboardReport:
    pr = get_allocation_report(total_seats=total_seats, threshold=threshold)
    fptp = get_fptp_report()
    generated_at_utc = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    return DashboardReport(generated_at_utc=generated_at_utc, pr=pr, fptp=fptp)
