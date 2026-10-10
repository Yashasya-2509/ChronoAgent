
from app.event_detection.event_aggregator import EventAggregator


def main():

    print()
    print("=" * 70)
    print("CHRONOAGENT — EVENT AGGREGATION TEST")
    print("=" * 70)
    print()

    # ---------------------------------------------------------
    # Simulated temporal events produced by EventDetector
    # ---------------------------------------------------------

    events = [

        {
            "event_id": "E00001",
            "video_id": "VID_TEST001",
            "event_type": "OBJECT_MOVEMENT",
            "subject_id": "PERSON_017",
            "subject_class": "person",
            "subject_track_id": 17,
            "subject": "person",
            "object": "person",
            "class_name": "person",
            "track_id": 17,
            "start_time": 10.2,
            "end_time": 10.6,
            "start_frame": 255,
            "end_frame": 265,
            "confidence": 0.91,
            "description": "PERSON_017 moved."
        },

        {
            "event_id": "E00002",
            "video_id": "VID_TEST001",
            "event_type": "OBJECT_MOVEMENT",
            "subject_id": "PERSON_017",
            "subject_class": "person",
            "subject_track_id": 17,
            "subject": "person",
            "object": "person",
            "class_name": "person",
            "track_id": 17,
            "start_time": 10.8,
            "end_time": 12.0,
            "start_frame": 270,
            "end_frame": 300,
            "confidence": 0.93,
            "description": "PERSON_017 moved."
        },

        {
            "event_id": "E00003",
            "video_id": "VID_TEST001",
            "event_type": "OBJECT_MOVEMENT",
            "subject_id": "PERSON_017",
            "subject_class": "person",
            "subject_track_id": 17,
            "subject": "person",
            "object": "person",
            "class_name": "person",
            "track_id": 17,
            "start_time": 13.0,
            "end_time": 14.0,
            "start_frame": 325,
            "end_frame": 350,
            "confidence": 0.89,
            "description": "PERSON_017 moved."
        },

        # Gap > 1.5 seconds.
        # This must create a NEW PERSON_017 event.
        {
            "event_id": "E00004",
            "video_id": "VID_TEST001",
            "event_type": "OBJECT_MOVEMENT",
            "subject_id": "PERSON_017",
            "subject_class": "person",
            "subject_track_id": 17,
            "subject": "person",
            "object": "person",
            "class_name": "person",
            "track_id": 17,
            "start_time": 18.0,
            "end_time": 18.7,
            "start_frame": 450,
            "end_frame": 467,
            "confidence": 0.91,
            "description": "PERSON_017 moved."
        },

        # -----------------------------------------------------
        # Different person
        # -----------------------------------------------------

        {
            "event_id": "E00005",
            "video_id": "VID_TEST001",
            "event_type": "OBJECT_MOVEMENT",
            "subject_id": "PERSON_021",
            "subject_class": "person",
            "subject_track_id": 21,
            "subject": "person",
            "object": "person",
            "class_name": "person",
            "track_id": 21,
            "start_time": 11.0,
            "end_time": 11.2,
            "start_frame": 275,
            "end_frame": 280,
            "confidence": 0.88,
            "description": "PERSON_021 moved."
        },

        {
            "event_id": "E00006",
            "video_id": "VID_TEST001",
            "event_type": "OBJECT_MOVEMENT",
            "subject_id": "PERSON_021",
            "subject_class": "person",
            "subject_track_id": 21,
            "subject": "person",
            "object": "person",
            "class_name": "person",
            "track_id": 21,
            "start_time": 11.5,
            "end_time": 11.8,
            "start_frame": 287,
            "end_frame": 295,
            "confidence": 0.90,
            "description": "PERSON_021 moved."
        }
    ]

    # ---------------------------------------------------------
    # Create aggregator
    # ---------------------------------------------------------

    aggregator = EventAggregator(
        max_event_gap=1.5,
        min_event_duration=0.5
    )

    # ---------------------------------------------------------
    # Aggregate
    # ---------------------------------------------------------

    aggregated_events = aggregator.aggregate(events)

    # ---------------------------------------------------------
    # Display
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("AGGREGATED EVENTS")
    print("=" * 70)

    for event in aggregated_events:

        print()

        print(f"EVENT ID    : {event['event_id']}")
        print(f"ENTITY      : {event['entity_id']}")
        print(f"OBJECT      : {event['object']}")
        print(f"EVENT       : {event['event_type']}")
        print(f"START       : {event['start_time']:.2f}s")
        print(f"END         : {event['end_time']:.2f}s")
        print(f"DURATION    : {event['duration']:.2f}s")
        print(f"OBSERVATIONS: {event['observation_count']}")
        print(f"DESCRIPTION : {event['description']}")

        print("-" * 70)

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("VALIDATION")
    print("=" * 70)

    # We expect exactly 3 aggregated events:
    #
    # E00001:
    # PERSON_017
    # 10.2 -> 14.0
    #
    # E00002:
    # PERSON_021
    # 11.0 -> 11.8
    #
    # E00003:
    # PERSON_017
    # 18.0 -> 18.7
    #
    # The ordering is chronological by start_time.

    assert len(aggregated_events) == 3, (
        f"Expected 3 aggregated events, "
        f"got {len(aggregated_events)}"
    )

    first = aggregated_events[0]
    second = aggregated_events[1]
    third = aggregated_events[2]

    # =========================================================
    # E00001 — PERSON_017 first movement
    # =========================================================

    assert first["event_id"] == "E00001"

    assert first["entity_id"] == "PERSON_017"

    assert first["event_type"] == "MOVED"

    assert abs(
        first["start_time"] - 10.2
    ) < 0.001

    assert abs(
        first["end_time"] - 14.0
    ) < 0.001

    assert abs(
        first["duration"] - 3.8
    ) < 0.001

    assert first["observation_count"] == 3

    print("PASS: E00001 PERSON_017 movement validated.")

    # =========================================================
    # E00002 — PERSON_021 movement
    # =========================================================

    assert second["event_id"] == "E00002"

    assert second["entity_id"] == "PERSON_021"

    assert second["event_type"] == "MOVED"

    assert abs(
        second["start_time"] - 11.0
    ) < 0.001

    assert abs(
        second["end_time"] - 11.8
    ) < 0.001

    assert abs(
        second["duration"] - 0.8
    ) < 0.001

    assert second["observation_count"] == 2

    print("PASS: E00002 PERSON_021 movement validated.")

    # =========================================================
    # E00003 — PERSON_017 second movement
    # =========================================================

    assert third["event_id"] == "E00003"

    assert third["entity_id"] == "PERSON_017"

    assert third["event_type"] == "MOVED"

    assert abs(
        third["start_time"] - 18.0
    ) < 0.001

    assert abs(
        third["end_time"] - 18.7
    ) < 0.001

    assert abs(
        third["duration"] - 0.7
    ) < 0.001

    assert third["observation_count"] == 1

    print("PASS: E00003 PERSON_017 second movement validated.")

    # =========================================================
    # Additional validation
    # =========================================================

    # Verify chronological ordering.

    assert (
        first["start_time"]
        <= second["start_time"]
        <= third["start_time"]
    )

    print("PASS: Events are chronologically ordered.")

    # Verify PERSON_017 identity is preserved.

    assert first["entity_id"] == "PERSON_017"
    assert third["entity_id"] == "PERSON_017"

    print("PASS: PERSON_017 identity preserved.")

    # Verify PERSON_021 identity is preserved.

    assert second["entity_id"] == "PERSON_021"

    print("PASS: PERSON_021 identity preserved.")

    # Verify first PERSON_017 event merged 3 observations.

    assert first["observation_count"] == 3

    print("PASS: PERSON_017 temporal observations merged.")

    # Verify PERSON_021 event merged 2 observations.

    assert second["observation_count"] == 2

    print("PASS: PERSON_021 temporal observations merged.")

    # Verify large gap created a separate PERSON_017 event.

    assert first["end_time"] < third["start_time"]

    assert (
        third["start_time"]
        - first["end_time"]
    ) > 1.5

    print("PASS: Large temporal gap created a new event.")

    # Verify durations.

    assert abs(first["duration"] - 3.8) < 0.001
    assert abs(second["duration"] - 0.8) < 0.001
    assert abs(third["duration"] - 0.7) < 0.001

    print("PASS: Event durations preserved.")

    # Verify chronological IDs.

    assert [
        event["event_id"]
        for event in aggregated_events
    ] == [
        "E00001",
        "E00002",
        "E00003"
    ]

    print("PASS: Event IDs assigned chronologically.")

    # =========================================================
    # SUCCESS
    # =========================================================

    print()
    print("=" * 70)
    print("✅ EVENT AGGREGATION TEST PASSED")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
