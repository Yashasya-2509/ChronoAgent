class AnswerGenerator:


    def __init__(self):

        pass



    # =====================================================
    # GENERATE FINAL ANSWER
    # =====================================================

    def generate(
        self,
        query,
        reasoning_result
    ):


        # ==========================================
        # NO RESULT
        # ==========================================

        if reasoning_result is None:


            return {


                "question":
                query,


                "answer":
                "No relevant event found in the video.",


                "timestamp":
                0,


                "evidence_frame":
                "",


                "confidence":
                0.0

            }



        # ==========================================
        # TIMELINE ANSWER
        # ==========================================

        if "timeline" in reasoning_result:


            timeline = (
                reasoning_result["timeline"]
            )


            timeline_text = (
                "Complete Event Timeline:\n\n"
            )


            for event in timeline:


                timeline_text += (

                    f"{event.get('time',0):.2f}s : "

                    f"{event.get('event','Unknown event')}"

                )


                if event.get("frame"):


                    timeline_text += (

                        f" "
                        f"(Frame: {event['frame']})"

                    )


                timeline_text += "\n"



            return {


                "question":
                query,


                "answer":
                timeline_text,


                "timestamp":
                0,


                "evidence_frame":
                "",


                "confidence":
                1.0

            }



        # ==========================================
        # NORMAL EVENT ANSWER
        # ==========================================


        return {


            "question":
            query,


            "answer":

            reasoning_result.get(
                "description",
                "Unknown event."
            ),



            "timestamp":

            reasoning_result.get(
                "start_time",
                0
            ),



            "evidence_frame":

            reasoning_result.get(
                "start_frame",
                ""
            ),



            "confidence":

            reasoning_result.get(
                "confidence",
                0.0
            )

        }