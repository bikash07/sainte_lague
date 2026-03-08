from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class AllocationRow:
    party: str
    votes: int
    vote_share: float
    seats: int
    seat_share: float


def apply_threshold(votes: Dict[str, int], threshold_percent: float) -> Dict[str, int]:
    if threshold_percent <= 0:
        return dict(votes)
    total_votes = sum(votes.values())
    cutoff = total_votes * (threshold_percent / 100.0)
    return {party: count for party, count in votes.items() if count >= cutoff}


def sainte_lague(votes: Dict[str, int], total_seats: int) -> Dict[str, int]:
    if total_seats <= 0:
        raise ValueError("total_seats must be positive")
    if not votes:
        return {}

    seats = {party: 0 for party in votes}
    for _ in range(total_seats):
        winner = max(
            votes,
            key=lambda p: (votes[p] / (2 * seats[p] + 1), votes[p], p),
        )
        seats[winner] += 1
    return seats


def build_rows(
    eligible_votes: Dict[str, int],
    seat_alloc: Dict[str, int],
    total_seats: int,
) -> List[AllocationRow]:
    eligible_total = sum(eligible_votes.values())
    rows: List[AllocationRow] = []
    for party, votes in eligible_votes.items():
        seats = seat_alloc.get(party, 0)
        vote_share = (votes / eligible_total * 100.0) if eligible_total else 0.0
        seat_share = (seats / total_seats * 100.0) if total_seats else 0.0
        rows.append(
            AllocationRow(
                party=party,
                votes=votes,
                vote_share=vote_share,
                seats=seats,
                seat_share=seat_share,
            )
        )

    return sorted(rows, key=lambda row: (-row.seats, -row.votes, row.party))

