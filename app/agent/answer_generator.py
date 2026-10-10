class AnswerGenerator:


    def __init__(self):

        print("[GENERATOR] Answer Generator initialized")


    # =====================================================
    # GENERATE FINAL ANSWER
    # =====================================================

    def generate(
        self,
        query,
        reasoning_result
    ):


        if reasoning_result is None:

            return {

                "question":query,

                "answer":
                "No relevant event found in the video.",

                "timestamp":0,

                "evidence_frame":"",

                "confidence":0.0
            }



        # =====================================================
        # TIMELINE RESPONSE
        # =====================================================

        if "timeline" in reasoning_result:


            timeline = reasoning_result["timeline"]


            text = "Complete Event Timeline:\n\n"


            evidence=[]


            for event in timeline:


                description = (
                    event.get(
                        "description",
                        event.get(
                            "event",
                            "Unknown event"
                        )
                    )
                )


                timestamp = event.get(
                    "timestamp",
                    event.get(
                        "time",
                        0
                    )
                )


                frame = event.get(
                    "frame",
                    event.get(
                        "start_frame",
                        ""
                    )
                )


                text += (

                    f"{timestamp:.2f}s : "
                    f"{description}"

                )


                if frame:

                    text += (
                        f" (Frame: {frame})"
                    )


                text+="\n"



                evidence.append({

                    "time":timestamp,

                    "event":description,

                    "frame_id":frame

                })



            return {


                "question":query,


                "answer":text,


                "timestamp":0,


                "evidence_frame":"",


                "confidence":1.0

            }





        # =====================================================
        # NORMAL EVENT ANSWER
        # =====================================================


        description = (

            reasoning_result.get(
                "description"
            )

            or

            reasoning_result.get(
                "event"
            )

            or

            reasoning_result.get(
                "answer"
            )

            or

            "Unknown event"

        )



        timestamp = (

            reasoning_result.get(
                "timestamp"
            )

            or

            reasoning_result.get(
                "start_time"
            )

            or

            0

        )


        frame = (

            reasoning_result.get(
                "start_frame"
            )

            or

            reasoning_result.get(
                "frame"
            )

            or

            ""

        )



        return {


            "question":query,


            "answer":description,


            "timestamp":timestamp,


            "evidence_frame":frame,


            "confidence":

                reasoning_result.get(
                    "confidence",
                    1.0
                )

        }