from pathlib import Path

from app.tracking.object_tracker import ObjectTracker


VIDEO_ID = "VID_0a2a093d"

VIDEO_PATH = Path(
    "data/videos/VID_0a2a093d.mov"
)


def main():

    print()
    print("=" * 70)
    print("CHRONOAGENT — UNIQUE OBJECT TRACKING TEST")
    print("=" * 70)
    print()

    # ---------------------------------------------------------
    # Check video
    # ---------------------------------------------------------

    if not VIDEO_PATH.exists():

        raise FileNotFoundError(
            f"Video not found: {VIDEO_PATH}"
        )

    print(
        f"[TEST] Video: {VIDEO_PATH}"
    )

    print(
        f"[TEST] Video ID: {VIDEO_ID}"
    )

    print()

    # ---------------------------------------------------------
    # Create tracker
    # ---------------------------------------------------------

    tracker = ObjectTracker(
        model_name="yolo11n.pt",
        confidence=0.25,
        tracker_config="bytetrack.yaml"
    )

    # ---------------------------------------------------------
    # Run tracking
    # ---------------------------------------------------------

    unique_objects = tracker.track(
        video_path=VIDEO_PATH,
        video_id=VIDEO_ID,
        sample_fps=5
    )

    # ---------------------------------------------------------
    # Final test output
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("FINAL UNIQUE OBJECT RESULT")
    print("=" * 70)

    print(
        f"{'ID':<15}"
        f"{'OBJECT':<15}"
        f"{'FIRST SEEN':<15}"
        f"{'LAST SEEN':<15}"
    )

    print("-" * 70)

    for obj in unique_objects:

        print(
            f"{obj['object_id']:<15}"
            f"{obj['object']:<15}"
            f"{obj['first_seen']:>8.2f}s"
            f"{'':7}"
            f"{obj['last_seen']:>8.2f}s"
        )

    print("-" * 70)

    print(
        f"TOTAL UNIQUE OBJECTS: "
        f"{len(unique_objects)}"
    )

    print("=" * 70)
    print()

    print(
        "[TEST] UNIQUE OBJECT TRACKING SUCCESSFUL"
    )


if __name__ == "__main__":
    main()