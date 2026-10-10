import re


class QueryClassifier:

    def classify(self, query):

        query = query.lower().strip()

        # =====================================================
        # TIME RANGE
        # =====================================================

        if re.search(
            r"between\s+\d+(?:\.\d+)?"
            r".*(?:and|to|-)\s*\d+(?:\.\d+)?"
            r"\s*(?:s|sec|secs|seconds)?",
            query
        ):

            return {
                "intent": "TIME_RANGE"
            }

        if re.search(
            r"from\s+\d+(?:\.\d+)?"
            r".*(?:to|-)\s*\d+(?:\.\d+)?"
            r"\s*(?:s|sec|secs|seconds)?",
            query
        ):

            return {
                "intent": "TIME_RANGE"
            }

        # =====================================================
        # BEFORE
        # =====================================================

        if (
            "before" in query
            or "prior to" in query
            or "earlier than" in query
        ):

            return {
                "intent": "BEFORE_EVENT"
            }

        # =====================================================
        # AFTER
        # =====================================================

        if (
            "after" in query
            or "later than" in query
            or "following" in query
        ):

            return {
                "intent": "AFTER_EVENT"
            }

        # =====================================================
        # DURING
        # =====================================================

        if (
            "during" in query
            or "while" in query
            or "within" in query
        ):

            return {
                "intent": "DURING_EVENT"
            }

        # =====================================================
        # OVERLAP
        # =====================================================

        if (
            "overlap" in query
            or "overlapped" in query
            or "overlapping" in query
        ):

            return {
                "intent": "OVERLAPS_EVENT"
            }

        # =====================================================
        # MEETS
        # =====================================================

        if (
            "meets" in query
            or "meet" in query
            or "immediately when" in query
        ):

            return {
                "intent": "MEETS_EVENT"
            }

        # =====================================================
        # STARTS
        # =====================================================

        if (
            "starts with" in query
            or "started when" in query
            or "start together" in query
        ):

            return {
                "intent": "STARTS_EVENT"
            }

        # =====================================================
        # ENDS
        # =====================================================

        if (
            "ends with" in query
            or "ended when" in query
            or "end together" in query
        ):

            return {
                "intent": "ENDS_EVENT"
            }

        # =====================================================
        # FOLLOWS
        # =====================================================

        if (
            "immediately after" in query
            or "directly after" in query
            or "what followed" in query
            or "what happened next" in query
            or "next event" in query
        ):

            return {
                "intent": "FOLLOWS_EVENT"
            }

        # =====================================================
        # FIRST EVENT
        # =====================================================

        if (
            "first" in query
            or "earliest" in query
            or "appeared first" in query
            or "came first" in query
            or "entered first" in query
        ):

            return {
                "intent": "FIRST_EVENT"
            }

        # =====================================================
        # LAST EVENT
        # =====================================================

        if (
            "last" in query
            or "latest" in query
            or "appeared last" in query
            or "ended last" in query
        ):

            return {
                "intent": "LAST_EVENT"
            }

        # =====================================================
        # TIMELINE
        # =====================================================

        if (
            "timeline" in query
            or "sequence" in query
            or "order of events" in query
            or (
                "what happened" in query
                and "step" in query
            )
        ):

            return {
                "intent": "TIMELINE"
            }

        # =====================================================
        # COUNT OBJECTS
        # =====================================================

        if (
            "how many" in query
            or "number of" in query
            or "count" in query
        ):

            return {
                "intent": "COUNT_OBJECT"
            }

        # =====================================================
        # OBJECT APPEARANCE TIME
        # =====================================================

        if (
            "when" in query
            and (
                "appear" in query
                or "enter" in query
                or "come" in query
            )
        ):

            return {
                "intent": "OBJECT_APPEARANCE_TIME"
            }

        # =====================================================
        # OBJECT LOCATION
        # =====================================================

        if (
            "where" in query
            or "location" in query
            or "position" in query
        ):

            return {
                "intent": "OBJECT_LOCATION"
            }

        # =====================================================
        # GENERAL
        # =====================================================

        return {
            "intent": "GENERAL_QUERY"
        }