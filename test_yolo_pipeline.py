from pathlib import Path

from app.object_detection.detection_manager import DetectionManager


def main():

    print("\n")
    print("=" * 60)
    print(" CHRONOAGENT - OBJECT DETECTION PIPELINE ")
    print("=" * 60)

    # --------------------------------------------------
    # INPUT VIDEO ID
    # --------------------------------------------------

    video_id = "VID_91bbf259"

    frame_manifest = (
        Path("data/manifests")
        / f"{video_id}_frames.json"
    )

    output_path = (
        Path("data/detections")
        / f"{video_id}_detections.json"
    )

    # --------------------------------------------------
    # OBJECT DETECTION
    # --------------------------------------------------

    manager = DetectionManager(
        confidence=0.10
    )

    output = manager.process_frames(
        frame_manifest,
        output_path
    )

    # --------------------------------------------------
    # RESULT
    # --------------------------------------------------

    print("\nDetection manifest:")
    print(output)

    print("\nOBJECT DETECTION COMPLETE")


if __name__ == "__main__":
    main()