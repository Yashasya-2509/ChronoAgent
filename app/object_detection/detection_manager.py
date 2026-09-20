from pathlib import Path
import json

from app.object_detection.yolo_detector import YOLODetector


class DetectionManager:


    def __init__(
        self,
        confidence=0.15
    ):

        self.detector = YOLODetector(
            model_name="yolo11n.pt",
            confidence=confidence
        )


    def process_frames(
        self,
        frame_manifest_path,
        output_path
    ):

        frame_manifest_path = Path(
            frame_manifest_path
        )

        output_path = Path(
            output_path
        )


        with open(
            frame_manifest_path,
            "r"
        ) as file:

            manifest = json.load(file)


        frames = manifest["frames"]


        all_detections = []


        print(
            f"Processing {len(frames)} frames..."
        )


        for index, frame in enumerate(frames):

            print(
                f"Frame {index+1}/{len(frames)}"
            )


            detections = self.detector.detect_frame(
                frame_path=frame["path"],
                frame_id=frame["frame_id"],
                timestamp=frame["timestamp"]
            )


            all_detections.extend(
                detections
            )


        result = {

            "video_id":
                manifest["video_id"],

            "total_frames":
                len(frames),

            "total_detections":
                len(all_detections),

            "detections":
                all_detections

        }


        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        with open(
            output_path,
            "w"
        ) as file:

            json.dump(
                result,
                file,
                indent=2
            )


        return output_path