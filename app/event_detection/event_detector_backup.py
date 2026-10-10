from pathlib import Path
import json



class EventDetector:


    def __init__(self):

        print("[EVENT] Event Detector initialized")




    # =========================================================
    # MAIN PIPELINE FUNCTION
    # =========================================================

    def detect(
        self,
        tracks,
        video_id=None,
        vlm_results=None
    ):


        events = []


        if not tracks:
            return events



        # -----------------------------
        # VIDEO ID
        # -----------------------------

        if video_id is None:

            video_id = tracks[0].get(
                "video_id",
                "unknown_video"
            )




        # =====================================================
        # GROUP TRACKS
        # =====================================================

        grouped_tracks = {}


        for obs in tracks:


            track_id = obs.get(
                "track_id"
            )


            if track_id is None:
                continue



            grouped_tracks.setdefault(
                track_id,
                []
            ).append(obs)





        # =====================================================
        # OBJECT EVENTS
        # =====================================================

        for track_id, observations in grouped_tracks.items():


            observations.sort(
                key=lambda x:
                x.get(
                    "timestamp",
                    0
                )
            )


            first = observations[0]

            last = observations[-1]



            # -----------------------------
            # CLASS NAME FIX
            # -----------------------------

            class_name = (
                first.get("class_name")
                or
                first.get("label")
                or
                first.get("object")
                or
                "unknown"
            )


            confidence = first.get(
                "confidence",
                0.0
            )



            first_time = first.get(
                "timestamp",
                0.0
            )


            last_time = last.get(
                "timestamp",
                first_time
            )



            first_frame = first.get(
                "frame_id",
                "unknown"
            )


            last_frame = last.get(
                "frame_id",
                first_frame
            )




            # =================================================
            # ENTER EVENT
            # =================================================


            events.append({

                "event_id":
                    f"E{len(events)+1:05d}",


                "video_id":
                    video_id,


                "event_type":
                    "OBJECT_ENTER",


                "subject":
                    f"{class_name}_{track_id}",


                "action":
                    "entered",



                # IMPORTANT
                "object":
                    class_name,


                "class_name":
                    class_name,



                "track_id":
                    track_id,


                "start_time":
                    first_time,


                "end_time":
                    first_time,


                "start_frame":
                    first_frame,


                "end_frame":
                    first_frame,


                "confidence":
                    confidence,



                "description":
                    f"{class_name} track {track_id} appeared first in the scene."

            })





            # =================================================
            # MOVEMENT EVENT
            # =================================================


            if len(observations) > 3:


                events.append({


                    "event_id":
                        f"E{len(events)+1:05d}",


                    "video_id":
                        video_id,


                    "event_type":
                        "OBJECT_MOVEMENT",



                    "subject":
                        f"{class_name}_{track_id}",



                    "action":
                        "moving",



                    "object":
                        class_name,


                    "class_name":
                        class_name,



                    "track_id":
                        track_id,



                    "start_time":
                        first_time,


                    "end_time":
                        last_time,



                    "start_frame":
                        first_frame,


                    "end_frame":
                        last_frame,



                    "confidence":
                        confidence,



                    "description":
                        f"{class_name} track {track_id} moved in the scene."

                })





            # =================================================
            # EXIT EVENT
            # =================================================


            if last_time > first_time:


                events.append({


                    "event_id":
                        f"E{len(events)+1:05d}",


                    "video_id":
                        video_id,


                    "event_type":
                        "OBJECT_EXIT",



                    "subject":
                        f"{class_name}_{track_id}",



                    "action":
                        "left",



                    "object":
                        class_name,


                    "class_name":
                        class_name,



                    "track_id":
                        track_id,



                    "start_time":
                        last_time,


                    "end_time":
                        last_time,



                    "start_frame":
                        last_frame,


                    "end_frame":
                        last_frame,



                    "confidence":
                        last.get(
                            "confidence",
                            confidence
                        ),



                    "description":
                        f"{class_name} track {track_id} left the scene."

                })







        # =====================================================
        # VLM SEMANTIC EVENTS
        # =====================================================


        if vlm_results:


            for result in vlm_results:


                timestamp = result.get(
                    "timestamp",
                    0
                )



                events.append({


                    "event_id":
                        f"E{len(events)+1:05d}",



                    "video_id":
                        video_id,



                    "event_type":
                        "SCENE_DESCRIPTION",



                    "subject":
                        "scene",



                    "action":
                        "observed",



                    "object":
                        "scene",



                    "class_name":
                        "scene",



                    "start_time":
                        timestamp,



                    "end_time":
                        timestamp,



                    "description":
                        result.get(
                            "description",
                            ""
                        )

                })





        # =====================================================
        # SORT EVENTS
        # =====================================================


        events.sort(

            key=lambda x:
            x.get(
                "start_time",
                0
            )

        )



        return events







    # =========================================================
    # FILE BASED FUNCTION
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



        with open(
            tracking_manifest_path,
            "r"
        ) as file:

            data=json.load(file)




        events = self.detect(

            data["observations"],

            data.get(
                "video_id"
            )

        )



        output = {


            "video_id":
                data.get(
                    "video_id"
                ),



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