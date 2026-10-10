from app.query.query_classifier import QueryClassifier
from app.reasoning.temporal_reasoner import TemporalReasoner


def make_event(
    event_id,
    event_type,
    subject_id,
    description,
    start,
    end,
    class_name="person",
    track_id=1,
):
    return {
        "event_id": event_id,
        "event_type": event_type,
        "subject_id": subject_id,
        "subject_class": class_name,
        "subject_track_id": track_id,
        "class_name": class_name,
        "track_id": track_id,
        "start_time": start,
        "end_time": end,
        "start_frame": int(start * 25),
        "end_frame": int(end * 25),
        "description": description,
        "confidence": 0.95,
        "video_id": "VID_TEST_TEMPORAL",
    }


def main():

    print()
    print("=" * 70)
    print("CHRONOAGENT — TEMPORAL QUERY INTEGRATION TEST")
    print("=" * 70)

    # ============================================================
    # 1. SYNTHETIC CCTV EVENTS
    # ============================================================

    events = [

        make_event(
            "E00001",
            "OBJECT_ENTER",
            "PERSON_001",
            "Person entered the room",
            5.0,
            8.0,
            "person",
            1,
        ),

        make_event(
            "E00002",
            "OBJECT_MOVEMENT",
            "PERSON_001",
            "Person moved toward the table",
            9.0,
            14.0,
            "person",
            1,
        ),

        make_event(
            "E00003",
            "OBJECT_MOVEMENT",
            "PERSON_001",
            "Person moved near the laptop",
            15.0,
            20.0,
            "person",
            1,
        ),

        make_event(
            "E00004",
            "OBJECT_ENTER",
            "PERSON_002",
            "Second person entered the room",
            22.0,
            25.0,
            "person",
            2,
        ),

        make_event(
            "E00005",
            "OBJECT_MOVEMENT",
            "PERSON_002",
            "Second person moved across the room",
            26.0,
            30.0,
            "person",
            2,
        ),

        make_event(
            "E00006",
            "OBJECT_EXIT",
            "PERSON_001",
            "Person left the room",
            35.0,
            38.0,
            "person",
            1,
        ),

        make_event(
            "E00007",
            "OBJECT_MOVEMENT",
            "PERSON_002",
            "Second person remained in the room",
            39.0,
            45.0,
            "person",
            2,
        ),
    ]

    print()
    print("Synthetic events created:", len(events))

    # ============================================================
    # 2. QUERY CLASSIFIER
    # ============================================================

    classifier = QueryClassifier()

    queries = [
        (
            "What happened before the person left?",
            "BEFORE_EVENT",
        ),
        (
            "What happened after the person left?",
            "AFTER_EVENT",
        ),
        (
            "What happened between 20 and 40 seconds?",
            "TIME_RANGE",
        ),
        (
            "Who entered first?",
            "FIRST_EVENT",
        ),
        (
            "What happened during the person's movement?",
            "DURING_EVENT",
        ),
        (
            "What happened immediately after the person entered?",
            "AFTER_EVENT",
        ),
    ]

    print()
    print("-" * 70)
    print("QUERY CLASSIFICATION")
    print("-" * 70)

    for query, expected in queries:

        result = classifier.classify(query)

        if isinstance(result, dict):
            intent = result.get("intent")
        else:
            intent = result

        print()
        print("Query    :", query)
        print("Expected :", expected)
        print("Detected :", intent)

        assert intent == expected, (
            f"Classification failed: "
            f"{query} -> {intent}, expected {expected}"
        )

    print()
    print("PASS: Query classification")

    # ============================================================
    # 3. TEMPORAL REASONER
    # ============================================================

    reasoner = TemporalReasoner(
        tolerance=0.15
    )

    print()
    print("-" * 70)
    print("TEMPORAL REASONING")
    print("-" * 70)

    # ------------------------------------------------------------
    # BEFORE EVENT
    # ------------------------------------------------------------

    result = reasoner.before_event(
        events,
        "left"
    )

    print()
    print("Events before 'left':")

    for event in result:

        print(
            event["event_id"],
            "|",
            event["start_time"],
            "-",
            event["end_time"],
            "|",
            event["description"],
        )

    assert len(result) > 0

    # The final event before the exit should be E00005.
    assert result[-1]["event_id"] == "E00005"

    print("PASS: BEFORE_EVENT")

    # ------------------------------------------------------------
    # AFTER EVENT
    # ------------------------------------------------------------

    result = reasoner.after_event(
        events,
        "entered"
    )

    print()
    print("Events after 'entered':")

    for event in result:

        print(
            event["event_id"],
            "|",
            event["start_time"],
            "-",
            event["end_time"],
            "|",
            event["description"],
        )

    assert len(result) > 0

    # There should be events after the first entry.
    assert result[0]["event_id"] == "E00002"

    print("PASS: AFTER_EVENT")

    # ------------------------------------------------------------
    # TIME RANGE
    # ------------------------------------------------------------

    result = reasoner.events_in_time_range(
        events,
        20.0,
        40.0,
    )

    print()
    print("Events between 20s and 40s:")

    for event in result:

        print(
            event["event_id"],
            "|",
            event["start_time"],
            "-",
            event["end_time"],
            "|",
            event["description"],
        )

    ids = [
        event["event_id"]
        for event in result
    ]

    assert "E00003" in ids
    assert "E00004" in ids
    assert "E00005" in ids
    assert "E00006" in ids

    print("PASS: TIME_RANGE")

    # ------------------------------------------------------------
    # FIRST EVENT
    # ------------------------------------------------------------

    first = reasoner.find_first_event(
        events,
        object_type="person"
    )

    print()
    print(
        "First person event:",
        first["event_id"],
        "|",
        first["description"],
    )

    assert first["event_id"] == "E00001"

    print("PASS: FIRST_EVENT")

    # ============================================================
    # 4. TEMPORAL RELATION MATRIX
    # ============================================================

    print()
    print("-" * 70)
    print("TEMPORAL RELATION CHECK")
    print("-" * 70)

    checks = [
        ("E00001", "E00002", "BEFORE"),
        ("E00002", "E00001", "AFTER"),
        ("E00002", "E00003", "BEFORE"),
        ("E00003", "E00004", "BEFORE"),
        ("E00004", "E00005", "BEFORE"),
        ("E00005", "E00006", "BEFORE"),
    ]

    event_map = {
        event["event_id"]: event
        for event in events
    }

    for a_id, b_id, expected in checks:

        relation = reasoner.relation_between(
            event_map[a_id],
            event_map[b_id],
        )

        print(
            f"{a_id} -> {b_id}: "
            f"{relation}"
        )

        assert relation == expected, (
            f"{a_id} -> {b_id}: "
            f"expected {expected}, "
            f"got {relation}"
        )

    print()
    print("PASS: Temporal relation matrix")

    # ============================================================
    # SUCCESS
    # ============================================================

    print()
    print("=" * 70)
    print("✅ TEMPORAL QUERY INTEGRATION TEST PASSED")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()