from pathlib import Path
import json


class EventDetector:


    def __init__(self):
        pass



    # =========================================================
    # PIPELINE COMPATIBLE FUNCTION
    # =========================================================

    def detect(
        self,
        tracks,
        video_id=None
    ):

        """
        ChronoPipeline compatible event generation.

        Input:
            tracking observations from ObjectTracker

        Output:
            list of temporal events
        """


        events = []



        if not tracks:

            return events



        # Generate video id dynamically

        if video_id is None:

            video_id = tracks[0].get(
                "video_id",
                "unknown_video"
            )



        # -----------------------------------------------------
        # GROUP TRACK OBSERVATIONS
        # -----------------------------------------------------

        grouped_tracks = {}



        for observation in tracks:


            track_id = observation[
                "track_id"
            ]


            if track_id not in grouped_tracks:

                grouped_tracks[track_id] = []


            grouped_tracks[track_id].append(
                observation
            )



        # -----------------------------------------------------
        # CREATE EVENTS
        # -----------------------------------------------------

        for track_id, observations in grouped_tracks.items():


            observations.sort(
                key=lambda x:
                x["timestamp"]
            )



            first = observations[0]

            last = observations[-1]



            class_name = first[
                "class_name"
            ]



            # ------------------------------
            # OBJECT APPEARED
            # ------------------------------

            events.append({

                "event_id":
                    f"E{len(events)+1:04d}",


                "video_id":
                    video_id,


                "event_type":
                    "OBJECT_APPEARED",


                "track_id":
                    track_id,


                "class_name":
                    class_name,


                "start_time":
                    first["timestamp"],


                "end_time":
                    first["timestamp"],


                "start_frame":
                    first["frame_id"],


                "end_frame":
                    first["frame_id"],


                "confidence":
                    first["confidence"],


                "description":
                    f"{class_name} track {track_id} appeared in the scene."

            })



            # ------------------------------
            # OBJECT DISAPPEARED
            # ------------------------------

            if last["timestamp"] > first["timestamp"]:


                events.append({

                    "event_id":
                        f"E{len(events)+1:04d}",


                    "video_id":
                        video_id,


                    "event_type":
                        "OBJECT_DISAPPEARED",


                    "track_id":
                        track_id,


                    "class_name":
                        class_name,


                    "start_time":
                        last["timestamp"],


                    "end_time":
                        last["timestamp"],


                    "start_frame":
                        last["frame_id"],


                    "end_frame":
                        last["frame_id"],


                    "confidence":
                        last["confidence"],


                    "description":
                        f"{class_name} track {track_id} disappeared from the scene."

                })



        # Sort according to time

        events.sort(
            key=lambda x:
            x["start_time"]
        )


        return events





    # =========================================================
    # OLD FILE BASED FUNCTION
    # =========================================================

    def detect_events(
        self,
        tracking_manifest_path,
        output_path
    ):


        tracking_manifest_path = Path(
            tracking_manifest_path
        )

        output_path = Path(
            output_path
        )


        if not tracking_manifest_path.exists():

            raise FileNotFoundError(
                f"Tracking manifest not found: {tracking_manifest_path}"
            )


        with open(
            tracking_manifest_path,
            "r"
        ) as file:

            data = json.load(file)



        events = self.detect(
            data["observations"],
            data["video_id"]
        )



        output = {

            "video_id":
                data["video_id"],


            "total_events":
                len(events),


            "events":
                events

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
                output,
                file,
                indent=2
            )


        return output_path