from pathlib import Path

from app.event_detection.event_detector import (
    EventDetector
)


VIDEO_ID = "VID_91bbf259"


TRACKING_MANIFEST = (
    Path("data/tracks")
    / f"{VIDEO_ID}_tracks.json"
)


OUTPUT_PATH = (
    Path("data/events")
    / f"{VIDEO_ID}_events.json"
)


def main():

    print("\n")
    print("=" * 60)
    print(" CHRONOAGENT - EVENT DETECTION ")
    print("=" * 60)

    detector = EventDetector()

    output = detector.detect_events(
        tracking_manifest_path=TRACKING_MANIFEST,
        output_path=OUTPUT_PATH
    )

    print("\nEvent manifest:")
    print(output)

    print("\n")
    print("=" * 60)
    print(" EVENT DETECTION COMPLETE ")
    print("=" * 60)


if __name__ == "__main__":
    main()