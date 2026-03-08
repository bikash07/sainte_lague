from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from app.service import AllocationReport, get_allocation_report

web = Blueprint("web", __name__)


def _parse_query_params() -> tuple[int, float]:
    seats = request.args.get("seats", default=110, type=int)
    threshold = request.args.get("threshold", default=3.0, type=float)
    if seats is None or seats <= 0:
        seats = 110
    if threshold is None or threshold < 0:
        threshold = 3.0
    return seats, threshold


@web.get("/")
def index():
    seats, threshold = _parse_query_params()
    error = None
    report: AllocationReport | None = None
    try:
        report = get_allocation_report(total_seats=seats, threshold=threshold)
    except Exception as exc:  # noqa: BLE001
        error = str(exc)

    return render_template(
        "index.html",
        report=report,
        error=error,
        seats=seats,
        threshold=threshold,
    )


@web.get("/api/allocation")
def api_allocation():
    seats, threshold = _parse_query_params()
    report = get_allocation_report(total_seats=seats, threshold=threshold)
    return jsonify(
        {
            "generated_at_utc": report.generated_at_utc,
            "total_seats": report.total_seats,
            "threshold": report.threshold,
            "total_votes_all_parties": report.total_votes_all_parties,
            "total_votes_eligible": report.total_votes_eligible,
            "parties_all": report.parties_all,
            "parties_eligible": report.parties_eligible,
            "parties_with_seats": report.parties_with_seats,
            "rows": [
                {
                    "party": row.party,
                    "votes": row.votes,
                    "vote_share": round(row.vote_share, 4),
                    "seats": row.seats,
                    "seat_share": round(row.seat_share, 4),
                }
                for row in report.rows
            ],
        }
    )

