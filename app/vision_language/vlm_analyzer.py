from pathlib import Path
import json


class VLMAnalyzer:


    def __init__(
        self,
        model_name="mock-vlm"
    ):

        self.model_name = model_name



    def analyze_frame(
        self,
        image_path,
        detections=None
    ):


        image_path = Path(image_path)


        if not image_path.exists():

            raise FileNotFoundError(
                image_path
            )


        description = {

            "image_path": str(image_path),

            "model":
            self.model_name,

            "description":
            "A CCTV surveillance frame containing detected objects.",

            "objects":
            detections or []

        }


        return description



    def analyze_keyframes(
        self,
        keyframe_manifest,
        detection_manifest=None
    ):


        with open(
            keyframe_manifest,
            "r"
        ) as f:

            keyframes=json.load(f)



        detections=[]


        if detection_manifest:

            with open(
                detection_manifest,
                "r"
            ) as f:

                detection_data=json.load(f)

                detections = detection_data["detections"]



        results=[]


        for frame in keyframes["keyframes"]:


            frame_objects=[

                d

                for d in detections

                if d["frame_id"] 
                == frame["frame_id"]

            ]



            result=self.analyze_frame(

                frame["path"],

                frame_objects

            )


            result["frame_id"] = frame["frame_id"]

            result["timestamp"] = frame["timestamp"]


            results.append(result)



        return results