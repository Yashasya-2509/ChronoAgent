from pathlib import Path
import json

import cv2


class DetectionVisualizer:

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def visualize_frame(
        self,
        frame_path,
        detections,
        output_path
    ):

        frame = cv2.imread(
            str(frame_path)
        )

        if frame is None:
            raise ValueError(
                f"Could not read frame: {frame_path}"
            )

        for detection in detections:

            bbox = detection["bbox"]

            x1 = int(bbox["x1"])
            y1 = int(bbox["y1"])
            x2 = int(bbox["x2"])
            y2 = int(bbox["y2"])

            class_name = detection[
                "class_name"
            ]

            confidence = detection[
                "confidence"
            ]

            label = (
                f"{class_name} "
                f"{confidence:.2f}"
            )

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        cv2.imwrite(
            str(output_path),
            frame
        )


def load_detection_manifest(
    manifest_path
):

    with open(
        manifest_path,
        "r"
    ) as file:

        return json.load(file)