from pathlib import Path

from app.tracking.object_tracker import (
    ObjectTracker
)


# =====================================================
# TEMPORARY TEST VIDEO ID
# =====================================================

VIDEO_ID = "VID_91bbf259"


# =====================================================
# PATHS
# =====================================================

VIDEO_PATH = (
    Path("data/videos")
    / f"{VIDEO_ID}.mp4"
)

OUTPUT_PATH = (
    Path("data/tracks")
    / f"{VIDEO_ID}_tracks.json"
)


def main():

    print("\n")
    print("=" * 60)
    print(" CHRONOAGENT - OBJECT TRACKING ")
    print("=" * 60)

    tracker = ObjectTracker(
        model_name="yolo11n.pt",
        confidence=0.10,
        tracker_config="bytetrack.yaml"
    )

    output = tracker.track_video(
        video_path=VIDEO_PATH,
        video_id=VIDEO_ID,
        output_path=OUTPUT_PATH
    )

    print("\nTracking manifest:")
    print(output)

    print("\n")
    print("=" * 60)
    print(" OBJECT TRACKING COMPLETE ")
    print("=" * 60)


if __name__ == "__main__":
    main()