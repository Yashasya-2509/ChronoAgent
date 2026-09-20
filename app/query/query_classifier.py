class QueryClassifier:


    def classify(
        self,
        query
    ):


        query = query.lower()



        # =====================================
        # BEFORE RELATION
        # =====================================

        if (
            "before" in query
            or
            "prior to" in query
            or
            "earlier than" in query
        ):


            return {

                "intent":
                "BEFORE_EVENT"

            }



        # =====================================
        # AFTER RELATION
        # =====================================

        if (
            "after" in query
            or
            "later than" in query
            or
            "following" in query
        ):


            return {

                "intent":
                "AFTER_EVENT"

            }



        # =====================================
        # TIMELINE / SEQUENCE
        # =====================================

        if (
            "timeline" in query
            or
            "sequence" in query
            or
            "order of events" in query
            or
            "what happened" in query
            and
            "step" in query
        ):


            return {

                "intent":
                "TIMELINE"

            }



        # =====================================
        # FIRST EVENT
        # =====================================

        if (
            "first" in query
            or
            "earliest" in query
            or
            "appeared first" in query
            or
            "came first" in query
        ):


            return {

                "intent":
                "FIRST_EVENT"

            }



        # =====================================
        # LAST EVENT
        # =====================================

        if (
            "last" in query
            or
            "latest" in query
            or
            "appeared last" in query
            or
            "ended last" in query
        ):


            return {

                "intent":
                "LAST_EVENT"

            }



        # =====================================
        # COUNT OBJECTS
        # =====================================

        if (
            "how many" in query
            or
            "number of" in query
            or
            "count" in query
        ):


            return {

                "intent":
                "COUNT_OBJECT"

            }



        # =====================================
        # OBJECT APPEARANCE TIME
        # =====================================

        if (
            "when" in query
            and
            (
                "appear" in query
                or
                "enter" in query
                or
                "come" in query
            )
        ):


            return {

                "intent":
                "OBJECT_APPEARANCE_TIME"

            }



        # =====================================
        # OBJECT LOCATION
        # =====================================

        if (
            "where" in query
            or
            "location" in query
            or
            "position" in query
        ):


            return {

                "intent":
                "OBJECT_LOCATION"

            }



        # =====================================
        # GENERAL QUESTION
        # =====================================

        return {


            "intent":

            "GENERAL_QUERY"

        }