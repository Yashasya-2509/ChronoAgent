from pathlib import Path



class EvidenceRetriever:


    def __init__(self):

        pass



    # ==========================================
    # GET EVIDENCE
    # ==========================================

    def get_evidence(
        self,
        video_id,
        reasoning_result
    ):


        frames_path = Path(
            "data/frames"
        ) / video_id



        # =====================================
        # TIMELINE EVIDENCE
        # =====================================

        if "timeline" in reasoning_result:


            evidence=[]


            for event in reasoning_result["timeline"]:


                frame_id = event.get(
                    "frame",
                    ""
                )


                frame_path = (
                    frames_path /
                    f"{frame_id}.jpg"
                )


                evidence.append({

                    "time":
                    event.get(
                        "time",
                        0
                    ),


                    "event":
                    event.get(
                        "event",
                        ""
                    ),


                    "frame_id":
                    frame_id,


                    "frame_path":
                    str(frame_path)
                    if frame_path.exists()
                    else None

                })


            return {


                "video_id":
                video_id,


                "type":
                "timeline",


                "events":
                evidence

            }



        # =====================================
        # SINGLE EVENT EVIDENCE
        # =====================================


        frame_id = reasoning_result.get(
            "start_frame",
            ""
        )



        frame_path = (
            frames_path /
            f"{frame_id}.jpg"
        )



        return {


            "video_id":
            video_id,


            "frame_id":
            frame_id,


            "timestamp":
            reasoning_result.get(
                "start_time",
                0
            ),


            "frame_path":

            str(frame_path)
            if frame_path.exists()
            else None

        }