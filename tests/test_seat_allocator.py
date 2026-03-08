from app.seat_allocator import apply_threshold, sainte_lague


def test_threshold_filters_small_parties():
    votes = {"A": 1000, "B": 400, "C": 50}
    eligible = apply_threshold(votes, threshold_percent=10)
    assert eligible == {"A": 1000, "B": 400}


def test_sainte_lague_allocation_sum_matches_seat_count():
    votes = {"A": 1000, "B": 800, "C": 200}
    seat_alloc = sainte_lague(votes, total_seats=10)
    assert sum(seat_alloc.values()) == 10
    assert seat_alloc["A"] >= seat_alloc["B"] >= seat_alloc["C"]
