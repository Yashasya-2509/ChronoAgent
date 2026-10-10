from pathlib import Path

from app.object_detection.yolo_detector import YOLODetector


VIDEO_ID = "VID_0a2a093d"

FRAME_DIR = Path(
    "data/frames/VID_0a2a093d"
)


def main():

    print()
    print("=" * 60)
    print("YOLO OBJECT DETECTION TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. FIND EXTRACTED FRAMES
    # ---------------------------------------------------------

    frame_paths = sorted(
        FRAME_DIR.glob("frame_*.jpg")
    )

    if not frame_paths:

        raise FileNotFoundError(
            f"No frames found in {FRAME_DIR}"
        )

    print(
        f"[TEST] Frames found: "
        f"{len(frame_paths)}"
    )

    # ---------------------------------------------------------
    # 2. BUILD FRAME RECORDS
    # ---------------------------------------------------------

    frames = []

    for frame_path in frame_paths:

        frame_number = int(
            frame_path.stem.split("_")[1]
        )

        # Read FPS from the known video.
        # 25 FPS for VID_0a2a093d.
        timestamp = (
            frame_number / 25.0
        )

        frames.append(
            {
                "frame_path":
                    str(frame_path),

                "frame_id":
                    frame_number,

                "timestamp":
                    round(
                        timestamp,
                        3
                    )
            }
        )

    # ---------------------------------------------------------
    # 3. LOAD YOLO
    # ---------------------------------------------------------

    detector = YOLODetector(
        model_name="yolo11n.pt",
        confidence=0.25
    )

    # ---------------------------------------------------------
    # 4. RUN DETECTION
    # ---------------------------------------------------------

    detections = detector.detect_frames(
        frames=frames,
        video_id=VIDEO_ID
    )

    # ---------------------------------------------------------
    # 5. RESULTS
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("YOLO DETECTION RESULTS")
    print("=" * 60)

    print(
        f"Frames processed : "
        f"{len(frames)}"
    )

    print(
        f"Total detections : "
        f"{len(detections)}"
    )

    # ---------------------------------------------------------
    # 6. CLASS COUNTS
    # ---------------------------------------------------------

    class_counts = {}

    for detection in detections:

        class_name = detection[
            "class_name"
        ]

        class_counts[class_name] = (
            class_counts.get(
                class_name,
                0
            ) + 1
        )

    print()
    print("Detection counts:")

    if class_counts:

        for class_name, count in sorted(
            class_counts.items()
        ):

            print(
                f"{class_name:15s}: "
                f"{count}"
            )

    else:

        print(
            "No allowed objects detected."
        )

    # ---------------------------------------------------------
    # 7. SHOW SAMPLE DETECTIONS
    # ---------------------------------------------------------

    print()
    print("Sample detections:")

    for detection in detections[:10]:

        print(
            f"Frame {detection['frame_id']:4d} | "
            f"{detection['timestamp']:7.3f}s | "
            f"{detection['class_name']:15s} | "
            f"confidence="
            f"{detection['confidence']:.3f}"
        )

    # ---------------------------------------------------------
    # 8. SUCCESS
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("YOLO DETECTION TEST SUCCESSFUL")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()