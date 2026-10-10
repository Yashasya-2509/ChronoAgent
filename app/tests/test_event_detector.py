from app.event_detection.event_detector import EventDetector


def main():

    detector = EventDetector()

    tracks = [
        {
            "track_id": 17,
            "class_name": "person",
            "timestamp": 10.2,
            "frame_id": 255,
            "confidence": 0.91
        },
        {
            "track_id": 17,
            "class_name": "person",
            "timestamp": 12.0,
            "frame_id": 300,
            "confidence": 0.92
        },
        {
            "track_id": 17,
            "class_name": "person",
            "timestamp": 15.7,
            "frame_id": 392,
            "confidence": 0.90
        },
        {
            "track_id": 17,
            "class_name": "person",
            "timestamp": 18.4,
            "frame_id": 460,
            "confidence": 0.89
        }
    ]

    vlm_results = [
        {
            "timestamp": 10.2,
            "frame_id": 255,
            "description": "A person is visible in the CCTV scene.",
            "objects": ["person"],
            "object_counts": {
                "person": 1
            },
            "detections": 1,
            "confidence": 0.91
        }
    ]

    events = detector.detect(
        tracks=tracks,
        video_id="VID_TEST001",
        vlm_results=vlm_results
    )

    print("\n" + "=" * 70)
    print("EVENT DETECTOR TEST")
    print("=" * 70)

    print(f"\nTOTAL EVENTS: {len(events)}")

    print("\nEVENTS:")

    for event in events:

        print(
            f"{event['event_id']} | "
            f"{event['event_type']} | "
            f"{event['subject_id']} | "
            f"{event['start_time']}s"
        )

    print("\n" + "=" * 70)
    print("CHRONOLOGICAL ID CHECK")
    print("=" * 70)

    expected_ids = [
        f"E{index:05d}"
        for index in range(1, len(events) + 1)
    ]

    actual_ids = [
        event["event_id"]
        for event in events
    ]

    print("Expected:", expected_ids)
    print("Actual:  ", actual_ids)

    assert actual_ids == expected_ids, (
        "Event IDs are not sequential after chronological sorting."
    )

    # Verify chronological ordering
    timestamps = [
        event["start_time"]
        for event in events
    ]

    assert timestamps == sorted(timestamps), (
        "Events are not chronologically sorted."
    )

    print("\n✅ Event IDs are chronological.")
    print("✅ Events are sorted by timestamp.")
    print("✅ EventDetector test PASSED.")


if __name__ == "__main__":
    main()