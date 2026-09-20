from pathlib import Path
from collections import Counter

from app.object_detection.detection_visualizer import (
    DetectionVisualizer,
    load_detection_manifest
)


# =====================================================
# DYNAMIC VIDEO ID
# =====================================================

VIDEO_ID = "VID_91bbf259"


# =====================================================
# PATHS
# =====================================================

MANIFEST_PATH = (
    Path("data/detections")
    / f"{VIDEO_ID}_detections.json"
)


OUTPUT_DIR = (
    Path("data/detections")
    / f"{VIDEO_ID}_visualized"
)


FRAMES_DIR = (
    Path("data/frames")
    / VIDEO_ID
)



def main():

    print("\n")
    print("=" * 60)
    print(" CHRONOAGENT - DETECTION VERIFICATION ")
    print("=" * 60)


    # ------------------------------------------------
    # LOAD DETECTION MANIFEST
    # ------------------------------------------------

    manifest = load_detection_manifest(
        MANIFEST_PATH
    )


    detections = manifest["detections"]


    print(
        f"\nTotal frames: "
        f"{manifest['total_frames']}"
    )


    print(
        f"Total detections: "
        f"{manifest['total_detections']}"
    )



    # ------------------------------------------------
    # OBJECT COUNTS
    # ------------------------------------------------

    object_counts = Counter(
        detection["class_name"]
        for detection in detections
    )


    print("\nObject counts:")


    if object_counts:

        for object_name, count in (
            object_counts.most_common()
        ):

            print(
                f"  {object_name}: {count}"
            )

    else:

        print(
            "  No objects detected."
        )



    # ------------------------------------------------
    # CONFIDENCE STATISTICS
    # ------------------------------------------------

    if detections:


        confidences = [

            detection["confidence"]

            for detection in detections

        ]


        print("\nConfidence statistics:")


        print(
            f"  Average: "
            f"{sum(confidences)/len(confidences):.3f}"
        )


        print(
            f"  Minimum: "
            f"{min(confidences):.3f}"
        )


        print(
            f"  Maximum: "
            f"{max(confidences):.3f}"
        )



    # ------------------------------------------------
    # VISUALIZATION
    # ------------------------------------------------

    visualizer = DetectionVisualizer(
        OUTPUT_DIR
    )


    # Dynamic keyframes
    # These exist for VID_91bbf259
    selected_frames = [

        "F00001",

        "F00013",

        "F00026"

    ]


    print(
        "\nCreating visual evidence..."
    )


    for frame_id in selected_frames:


        frame_detections = [

            detection

            for detection in detections

            if detection["frame_id"]
            == frame_id

        ]



        frame_path = (
            FRAMES_DIR
            / f"{frame_id}.jpg"
        )


        output_path = (

            OUTPUT_DIR
            / f"{frame_id}_detected.jpg"

        )


        visualizer.visualize_frame(

            frame_path,

            frame_detections,

            output_path

        )


        print(
            f"  Created: {output_path}"
        )



    print("\n")
    print("=" * 60)
    print(" DETECTION VERIFICATION COMPLETE ")
    print("=" * 60)



if __name__ == "__main__":

    main()