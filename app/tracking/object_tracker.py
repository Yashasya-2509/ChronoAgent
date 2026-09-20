from pathlib import Path
import json

from ultralytics import YOLO


class ObjectTracker:


    def __init__(
        self,
        model_name="yolo11n.pt",
        confidence=0.10,
        tracker_config="bytetrack.yaml"
    ):

        self.model_name = model_name
        self.confidence = confidence
        self.tracker_config = tracker_config


        print(
            f"[TRACKING] Loading model: {model_name}"
        )


        self.model = YOLO(
            model_name
        )


        print(
            "[TRACKING] Model loaded successfully."
        )



    # =========================================================
    # PIPELINE TRACK FUNCTION
    # =========================================================

    def track(
        self,
        video_path,
        detections,
        video_id=None
    ):

        """
        ChronoAgent pipeline compatible tracker.

        Dynamically tracks objects from any CCTV video.
        """


        if video_id is None:

            video_id = "unknown_video"



        output_path = Path(
            f"data/tracks/{video_id}_tracks.json"
        )


        print(
            "[TRACKING] Starting ByteTrack..."
        )


        self.track_video(
            video_path=video_path,
            video_id=video_id,
            output_path=output_path
        )


        with open(
            output_path,
            "r"
        ) as file:

            tracking_data = json.load(
                file
            )


        observations = tracking_data[
            "observations"
        ]


        print(
            f"[TRACKING] Total observations: {len(observations)}"
        )


        return observations




    # =========================================================
    # VIDEO TRACKING
    # =========================================================

    def track_video(
        self,
        video_path,
        video_id,
        output_path
    ):


        video_path = Path(
            video_path
        )


        output_path = Path(
            output_path
        )


        if not video_path.exists():

            raise FileNotFoundError(
                f"Video not found: {video_path}"
            )


        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        print(
            f"[TRACKING] Processing: {video_path}"
        )



        results = self.model.track(

            source=str(video_path),

            conf=self.confidence,

            tracker=self.tracker_config,

            persist=True,

            stream=True,

            verbose=False

        )



        tracked_objects = []


        total_frames = 0


        frames_with_tracks = 0


        fps = self._get_fps(
            video_path
        )



        for frame_number, result in enumerate(results):


            total_frames += 1



            if result.boxes is None:

                continue



            if result.boxes.id is None:

                continue



            frames_with_tracks += 1



            track_ids = (
                result.boxes.id
                .int()
                .cpu()
                .tolist()
            )


            classes = (
                result.boxes.cls
                .int()
                .cpu()
                .tolist()
            )


            confidences = (
                result.boxes.conf
                .cpu()
                .tolist()
            )


            boxes = (
                result.boxes.xyxy
                .cpu()
                .tolist()
            )



            for (
                track_id,
                class_id,
                confidence,
                bbox
            ) in zip(
                track_ids,
                classes,
                confidences,
                boxes
            ):


                tracked_objects.append({

                    "video_id":
                        video_id,


                    "frame_id":
                        f"F{frame_number+1:05d}",


                    "frame_number":
                        frame_number,


                    "timestamp":
                        frame_number / fps,


                    "track_id":
                        int(track_id),


                    "class_id":
                        int(class_id),


                    "class_name":
                        self.model.names[
                            int(class_id)
                        ],


                    "confidence":
                        float(confidence),


                    "bbox":{

                        "x1":
                            float(bbox[0]),

                        "y1":
                            float(bbox[1]),

                        "x2":
                            float(bbox[2]),

                        "y2":
                            float(bbox[3])

                    }

                })




        # =====================================================
        # TRACK SUMMARY
        # =====================================================


        unique_tracks = {}



        for obj in tracked_objects:


            tid = obj["track_id"]



            if tid not in unique_tracks:


                unique_tracks[tid] = {

                    "track_id":
                        tid,


                    "class_name":
                        obj["class_name"],


                    "first_frame":
                        obj["frame_id"],


                    "first_timestamp":
                        obj["timestamp"],


                    "last_frame":
                        obj["frame_id"],


                    "last_timestamp":
                        obj["timestamp"],


                    "observations":
                        0
                }




            unique_tracks[tid][
                "last_frame"
            ] = obj["frame_id"]



            unique_tracks[tid][
                "last_timestamp"
            ] = obj["timestamp"]



            unique_tracks[tid][
                "observations"
            ] += 1




        output = {

            "video_id":
                video_id,


            "video_path":
                str(video_path),


            "total_frames":
                total_frames,


            "frames_with_tracks":
                frames_with_tracks,


            "unique_track_count":
                len(unique_tracks),


            "tracks":
                list(unique_tracks.values()),


            "observations":
                tracked_objects

        }



        with open(
            output_path,
            "w"
        ) as file:


            json.dump(
                output,
                file,
                indent=2
            )



        print(
            f"[TRACKING] Frames processed: {total_frames}"
        )


        print(
            f"[TRACKING] Frames with tracks: {frames_with_tracks}"
        )


        print(
            f"[TRACKING] Unique tracks: {len(unique_tracks)}"
        )


        print(
            f"[TRACKING] Saved: {output_path}"
        )


        return output_path




    # =========================================================
    # FPS READER
    # =========================================================

    @staticmethod
    def _get_fps(video_path):

        import cv2


        cap = cv2.VideoCapture(
            str(video_path)
        )


        fps = cap.get(
            cv2.CAP_PROP_FPS
        )


        cap.release()


        return fps if fps > 0 else 30.0