from pathlib import Path

from app.object_detection.yolo_detector import YOLODetector


FRAME_DIR = Path(
    "data/frames/VID_PHASEA001"
)


def main():

    print("\n")
    print("=" * 60)
    print("        CHRONOAGENT - YOLO TEST")
    print("=" * 60)

    detector = YOLODetector(
        model_name="yolo11n.pt",
        confidence=0.05
    )

    frame_paths = sorted(
        FRAME_DIR.glob("*.jpg")
    )

    print(
        f"\nFrames available: {len(frame_paths)}"
    )

    if not frame_paths:
        raise RuntimeError(
            f"No frames found in {FRAME_DIR}"
        )

    # Test first frame
    frame_path = frame_paths[0]

    print(
        f"\nTesting frame: {frame_path}"
    )

    detections = detector.detect_frame(
        frame_path,
        frame_id=frame_path.stem,
        timestamp=0.0
    )

    print(
        f"\nDetections found: {len(detections)}"
    )

    for detection in detections:

        print(
            f"\nObject: "
            f"{detection['class_name']}"
        )

        print(
            f"Confidence: "
            f"{detection['confidence']:.3f}"
        )

        print(
            f"Bounding Box: "
            f"{detection['bbox']}"
        )

    print("\n")
    print("=" * 60)
    print("        YOLO TEST SUCCESSFUL")
    print("=" * 60)


if __name__ == "__main__":
    main()