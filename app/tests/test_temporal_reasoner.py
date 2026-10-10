from app.reasoning.temporal_reasoner import TemporalReasoner


def make_event(
    event_id,
    start,
    end,
    description
):
    return {
        "event_id": event_id,
        "event_type": "TEST_EVENT",
        "start_time": start,
        "end_time": end,
        "description": description,
        "class_name": "test"
    }


def main():

    print()
    print("=" * 70)
    print("CHRONOAGENT — TEMPORAL REASONER TEST")
    print("=" * 70)

    reasoner = TemporalReasoner(
        tolerance=0.15
    )

    # =====================================================
    # BEFORE
    # =====================================================

    a = make_event(
        "E001",
        0,
        5,
        "Person entered"
    )

    b = make_event(
        "E002",
        10,
        15,
        "Person moved"
    )

    assert (
        reasoner.relation_between(a, b)
        == "BEFORE"
    )

    print("PASS: BEFORE")

    # =====================================================
    # AFTER
    # =====================================================

    assert (
        reasoner.relation_between(b, a)
        == "AFTER"
    )

    print("PASS: AFTER")

    # =====================================================
    # DURING
    # =====================================================

    outer = make_event(
        "E003",
        10,
        30,
        "Person in room"
    )

    inner = make_event(
        "E004",
        15,
        20,
        "Person sat"
    )

    assert (
        reasoner.relation_between(
            inner,
            outer
        )
        == "DURING"
    )

    print("PASS: DURING")

    # =====================================================
    # OVERLAPS
    # =====================================================

    overlap_a = make_event(
        "E005",
        10,
        20,
        "Person approaches"
    )

    overlap_b = make_event(
        "E006",
        15,
        25,
        "Vehicle arrives"
    )

    assert (
        reasoner.relation_between(
            overlap_a,
            overlap_b
        )
        == "OVERLAPS"
    )

    print("PASS: OVERLAPS")

    # =====================================================
    # MEETS
    # =====================================================

    meets_a = make_event(
        "E007",
        30,
        40,
        "Person enters"
    )

    meets_b = make_event(
        "E008",
        40,
        50,
        "Person moves"
    )

    assert (
        reasoner.relation_between(
            meets_a,
            meets_b
        )
        == "MEETS"
    )

    print("PASS: MEETS")

    # =====================================================
    # STARTS
    # =====================================================

    starts_a = make_event(
        "E009",
        60,
        70,
        "Person enters"
    )

    starts_b = make_event(
        "E010",
        60,
        80,
        "Scene activity"
    )

    assert (
        reasoner.relation_between(
            starts_a,
            starts_b
        )
        == "STARTS"
    )

    print("PASS: STARTS")

    # =====================================================
    # ENDS
    # =====================================================

    ends_a = make_event(
        "E011",
        75,
        80,
        "Person leaves"
    )

    ends_b = make_event(
        "E012",
        70,
        80,
        "Scene activity"
    )

    assert (
        reasoner.relation_between(
            ends_a,
            ends_b
        )
        == "ENDS"
    )

    print("PASS: ENDS")

    # =====================================================
    # FOLLOWS
    # =====================================================

    events = [
        a,
        b,
        outer,
        inner
    ]

    following = reasoner.follows_event(
        events,
        a
    )

    assert (
        following["event_id"]
        == "E002"
    )

    print("PASS: FOLLOWS")

    # =====================================================
    # TIME RANGE
    # =====================================================

    range_events = (
        reasoner.events_in_time_range(
            events,
            4,
            11
        )
    )

    ids = [
        event["event_id"]
        for event in range_events
    ]

    assert "E001" in ids
    assert "E002" in ids

    print("PASS: TIME RANGE")

    print()
    print("=" * 70)
    print("✅ ALL TEMPORAL REASONING TESTS PASSED")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()