from pathlib import Path

from ultralytics import YOLO



class YOLODetector:


    def __init__(
        self,
        model_name="yolo11n.pt",
        confidence=0.25
    ):


        self.model_name = model_name

        self.confidence = confidence


        print(
            f"[YOLO] Loading model: {model_name}"
        )


        self.model = YOLO(
            model_name
        )


        # COCO objects useful for CCTV understanding
        self.allowed_classes = {

            "person",

            "backpack",

            "handbag",

            "suitcase",

            "chair",

            "laptop",

            "cell phone",

            "car",

            "truck",

            "bus",

            "bicycle",

            "motorcycle",

            "dog",

            "cat"

        }



        print(
            "[YOLO] Model loaded successfully"
        )



    # ==================================================
    # SINGLE FRAME DETECTION
    # ==================================================

    def detect_frame(
        self,
        frame_path,
        frame_id=None,
        timestamp=None
    ):


        frame_path = Path(
            frame_path
        )


        if not frame_path.exists():

            raise FileNotFoundError(
                f"Frame not found: {frame_path}"
            )



        results = self.model.predict(

            source=str(frame_path),

            conf=self.confidence,

            verbose=False

        )



        detections=[]



        result = results[0]



        if result.boxes is None:

            return detections



        boxes=result.boxes



        for i in range(len(boxes)):



            confidence=float(
                boxes.conf[i].item()
            )


            if confidence < self.confidence:

                continue



            class_id=int(
                boxes.cls[i].item()
            )



            class_name=self.model.names[
                class_id
            ]



            # Ignore unwanted COCO classes
            if class_name not in self.allowed_classes:

                continue



            xyxy = boxes.xyxy[i].tolist()



            detection={


                "frame_id":

                    frame_id,


                "timestamp":

                    timestamp,


                "class_id":

                    class_id,


                "class_name":

                    class_name,


                "confidence":

                    round(
                        confidence,
                        3
                    ),



                "bbox":{


                    "x1":

                        float(xyxy[0]),


                    "y1":

                        float(xyxy[1]),


                    "x2":

                        float(xyxy[2]),


                    "y2":

                        float(xyxy[3])

                }

            }



            detections.append(
                detection
            )



        return detections





    # ==================================================
    # MULTI FRAME PIPELINE
    # ==================================================

    def detect_frames(
        self,
        frames,
        video_id
    ):


        all_detections=[]



        print(
            f"[YOLO] Processing {len(frames)} frames"
        )



        for index, frame in enumerate(frames):


            print(
                f"[YOLO] Frame {index+1}/{len(frames)}"
            )



            if isinstance(
                frame,
                dict
            ):


                frame_path = frame.get(
                    "frame_path"
                )


                frame_id = frame.get(
                    "frame_id"
                )


                timestamp = frame.get(
                    "timestamp"
                )


            else:


                frame_path = frame

                frame_id=None

                timestamp=None





            detections=self.detect_frame(

                frame_path,

                frame_id,

                timestamp

            )



            for detection in detections:


                detection["video_id"]=video_id



            all_detections.extend(
                detections
            )



        print(
            f"[YOLO] Total detections: {len(all_detections)}"
        )



        return all_detections