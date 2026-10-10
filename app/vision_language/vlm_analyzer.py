from pathlib import Path
from collections import Counter


class VLMAnalyzer:


    def __init__(
        self,
        mode="mock",
        model_name="yolo11n.pt",
        confidence=0.25
    ):

        self.mode = mode
        self.model_name = model_name
        self.confidence = confidence
        self.model = None

        if self.mode.lower() == "yolo":
            try:
                from ultralytics import YOLO
                self.model = YOLO(model_name)
            except Exception as error:
                print(f"[VLM] YOLO mode unavailable, using mock mode: {error}")
                self.mode = "mock"

        print(
            f"[VLM] Mode: {self.mode}"
        )



    def analyze_frame(
        self,
        image_path
    ):

        if not image_path:
            return {
                "description": "Image unavailable",
                "objects": [],
                "confidence": 0.0,
            }

        image_path = Path(
            image_path
        )


        if not image_path.exists():

            return {

                "description":
                "Image unavailable",

                "objects": [],

                "confidence": 0.0,

            }



        if self.mode.lower() == "yolo" and self.model is not None:
            predictions = self.model.predict(
                source=str(image_path),
                conf=self.confidence,
                verbose=False,
            )
            result = predictions[0]
            labels = [
                self.model.names[int(class_id)]
                for class_id in result.boxes.cls.tolist()
            ] if result.boxes is not None else []
            counts = Counter(labels)
            description = ", ".join(
                f"{count} {label}{'s' if count != 1 else ''}"
                for label, count in sorted(counts.items())
            ) or "No supported objects detected"
            confidence = max(
                result.boxes.conf.tolist(),
                default=0.0,
            ) if result.boxes is not None else 0.0
            return {
                "image": str(image_path),
                "description": f"CCTV frame contains {description}.",
                "objects": sorted(counts),
                "object_counts": dict(counts),
                "detections": len(labels),
                "confidence": round(float(confidence), 3),
            }

        result = {


            "image":
            str(image_path),


            "description":
            "A CCTV frame containing people and objects. "
            "Possible human activity detected.",


            "objects":
            [
                "person"
            ],


            "confidence":
            0.70

        }


        return result




    def analyze_frames(
        self,
        frames
    ):


        results = []


        for frame in frames:


            image_path = frame.get("path", frame.get("frame_path"))
            result = self.analyze_frame(image_path)
            result["frame_id"] = frame.get("frame_id")
            result["timestamp"] = frame.get("timestamp", 0.0)


            results.append(
                result
            )


        return results