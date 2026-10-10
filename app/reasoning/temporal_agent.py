class TemporalReasoner:


    def reason(
        self,
        memories,
        question,
        intent
    ):

        intent_name = intent.get(
            "intent"
        )


        if intent_name == "FIRST_EVENT":

            return self.first_event(
                memories
            )


        elif intent_name == "BEFORE_EVENT":

            return self.before_event(
                memories,
                question
            )


        elif intent_name == "AFTER_EVENT":

            return self.after_event(
                memories,
                question
            )


        elif intent_name == "OBJECT_APPEARANCE_TIME":

            return self.object_time(
                memories,
                question
            )


        elif intent_name == "COUNT_OBJECT":

            return self.count_object(
                memories,
                question
            )


        else:

            return {
                "answer":
                "No temporal reasoning available",
                "confidence":0
            }





    # -------------------------
    # FIRST EVENT
    # -------------------------

    def first_event(
        self,
        memories
    ):


        if not memories:

            return {
                "answer":
                "No events found"
            }


        event=min(
            memories,
            key=lambda x:x["start_time"]
        )


        return {

            "answer":
            event["description"],

            "timestamp":
            event["start_time"],

            "start_frame":
            event["start_frame"],

            "confidence":
            1.0
        }





    # -------------------------
    # BEFORE EVENT
    # -------------------------

    def before_event(
        self,
        memories,
        question
    ):


        target=None


        words=question.lower().split()


        for m in memories:

            name=str(
                m.get(
                    "class_name",
                    ""
                )
            )


            if name in words:

                target=m
                break



        if target is None:

            return {

            "answer":
            "Target event not found",

            "confidence":0

            }



        previous=[]


        for m in memories:


            if m["end_time"] < target["start_time"]:

                previous.append(m)



        if not previous:


            return {

            "answer":
            "No event happened before",

            "confidence":1

            }



        event=max(
            previous,
            key=lambda x:x["end_time"]
        )


        return {


            "answer":
            event["description"],


            "timestamp":
            event["end_time"],


            "start_frame":
            event["start_frame"],


            "confidence":
            1.0
        }





    # -------------------------
    # OBJECT TIME
    # -------------------------

    def object_time(
        self,
        memories,
        question
    ):


        for m in memories:


            if m["class_name"] in question.lower():

                return {


                "answer":
                f'{m["class_name"]} appeared at {m["start_time"]} seconds',


                "timestamp":
                m["start_time"],


                "start_frame":
                m["start_frame"],


                "confidence":
                1.0

                }


        return {


        "answer":
        "Object not found",

        "confidence":0

        }





    # -------------------------
    # COUNT OBJECT
    # -------------------------

    def count_object(
        self,
        memories,
        question
    ):


        objects=set()


        for m in memories:


            if "person" in question.lower():

                if m["class_name"]=="person":

                    objects.add(
                        m["track_id"]
                    )



        return {


        "answer":
        f"{len(objects)} persons appeared",

        "confidence":
        1.0

        }






    def after_event(
        self,
        memories,
        question
    ):

        return {

        "answer":
        "After reasoning not implemented",

        "confidence":
        0

        }