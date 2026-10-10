import re


class TemporalReasoner:

    """
    ChronoAgent temporal reasoning engine.

    Supports interval-based temporal relations:

        BEFORE
        AFTER
        DURING
        OVERLAPS
        MEETS
        STARTS
        ENDS
        FOLLOWS

    Events are represented using:

        start_time
        end_time

    The reasoner never invents events. It only reasons
    over events supplied to it.
    """

    TEMPORAL_RELATIONS = {
        "BEFORE",
        "AFTER",
        "DURING",
        "OVERLAPS",
        "MEETS",
        "STARTS",
        "ENDS",
        "FOLLOWS",
    }

    def __init__(self, tolerance=0.15):

        self.tolerance = float(tolerance)

        print(
            "[REASONING] Temporal Reasoner initialized"
        )

    # =========================================================
    # NORMALIZE EVENT
    # =========================================================

    def normalize_event(self, event):

        start_time = event.get(
            "start_time",
            event.get("timestamp", 0.0)
        )

        end_time = event.get(
            "end_time",
            start_time
        )

        try:
            start_time = float(start_time)
        except (TypeError, ValueError):
            start_time = 0.0

        try:
            end_time = float(end_time)
        except (TypeError, ValueError):
            end_time = start_time

        if end_time < start_time:
            end_time = start_time

        class_name = event.get(
            "class_name"
        )

        object_name = event.get(
            "object",
            class_name or ""
        )

        track_id = event.get(
            "track_id"
        )

        if track_id is None:
            track_id = event.get(
                "subject_track_id"
            )

        return {
            "event_id": event.get(
                "event_id",
                ""
            ),

            "event_type": event.get(
                "event_type",
                ""
            ),

            "start_time": start_time,

            "end_time": end_time,

            "timestamp": start_time,

            "duration": max(
                0.0,
                end_time - start_time
            ),

            "description": event.get(
                "description",
                "Unknown event"
            ),

            "object": object_name or "",

            "class_name": class_name or object_name or "",

            "track_id": track_id,

            "subject_id": event.get(
                "subject_id"
            ),

            "subject_class": event.get(
                "subject_class"
            ),

            "start_frame": event.get(
                "start_frame"
            ),

            "end_frame": event.get(
                "end_frame"
            ),

            "evidence": event.get(
                "evidence",
                {}
            ),

            "confidence": float(
                event.get(
                    "confidence",
                    1.0
                ) or 0.0
            ),
        }

    # =========================================================
    # TRACK ID EXTRACTION
    # =========================================================

    def extract_track(self, text):

        if not text:
            return None

        match = re.search(
            r"track[\s_-]*(\d+)",
            str(text),
            re.IGNORECASE
        )

        if match:
            return match.group(1)

        return None

    # =========================================================
    # SORT EVENTS
    # =========================================================

    def sort_events(self, memories):

        events = [
            self.normalize_event(event)
            for event in memories
        ]

        return sorted(
            events,
            key=lambda event: (
                event["start_time"],
                event["end_time"],
                event["event_id"]
            )
        )

    # =========================================================
    # FILTER EVENTS
    # =========================================================

    def filter_events(
        self,
        memories,
        event_types=None,
        object_type=None
    ):

        events = self.sort_events(
            memories
        )

        result = []

        normalized_types = None

        if event_types:
            normalized_types = {
                str(event_type).upper()
                for event_type in event_types
            }

        for event in events:

            if normalized_types:

                if (
                    event["event_type"].upper()
                    not in normalized_types
                ):
                    continue

            if object_type:

                event_object = str(
                    event["object"]
                ).lower()

                event_class = str(
                    event["class_name"]
                ).lower()

                target = str(
                    object_type
                ).lower()

                if (
                    event_object != target
                    and event_class != target
                ):
                    continue

            result.append(event)

        return result

    # =========================================================
    # TEMPORAL RELATION
    # =========================================================

    def relation_between(
        self,
        event_a,
        event_b
    ):

        a = self.normalize_event(
            event_a
        )

        b = self.normalize_event(
            event_b
        )

        a_start = a["start_time"]
        a_end = a["end_time"]

        b_start = b["start_time"]
        b_end = b["end_time"]

        tolerance = self.tolerance

        # -----------------------------------------------------
        # BEFORE
        # -----------------------------------------------------

        if a_end < b_start - tolerance:

            return "BEFORE"

        # -----------------------------------------------------
        # AFTER
        # -----------------------------------------------------

        if a_start > b_end + tolerance:

            return "AFTER"

        # -----------------------------------------------------
        # MEETS
        # -----------------------------------------------------

        if abs(a_end - b_start) <= tolerance:

            return "MEETS"

        # -----------------------------------------------------
        # STARTS
        # -----------------------------------------------------

        if (
            abs(a_start - b_start) <= tolerance
            and
            a_end < b_end - tolerance
        ):

            return "STARTS"

        # -----------------------------------------------------
        # ENDS
        # -----------------------------------------------------

        if (
            abs(a_end - b_end) <= tolerance
            and
            a_start > b_start + tolerance
        ):

            return "ENDS"

        # -----------------------------------------------------
        # DURING
        # -----------------------------------------------------

        if (
            a_start > b_start + tolerance
            and
            a_end < b_end - tolerance
        ):

            return "DURING"

        # -----------------------------------------------------
        # OVERLAPS
        # -----------------------------------------------------

        if (
            a_start < b_start - tolerance
            and
            a_end > b_start + tolerance
            and
            a_end < b_end - tolerance
        ):

            return "OVERLAPS"

        # -----------------------------------------------------
        # CONTAINED / COVERING CASE
        #
        # If B is completely inside A, then A is not DURING B.
        # For directional querying, return the inverse relation.
        # -----------------------------------------------------

        if (
            a_start < b_start - tolerance
            and
            a_end > b_end + tolerance
        ):

            return "CONTAINS"

        # -----------------------------------------------------
        # SAME INTERVAL
        # -----------------------------------------------------

        if (
            abs(a_start - b_start) <= tolerance
            and
            abs(a_end - b_end) <= tolerance
        ):

            return "OVERLAPS"

        return "OVERLAPS"

    # =========================================================
    # GET RELATION
    # =========================================================

    def get_relation(
        self,
        event_a,
        event_b
    ):

        return self.relation_between(
            event_a,
            event_b
        )

    # =========================================================
    # FIND EVENTS BY RELATION
    # =========================================================

    def find_related_events(
        self,
        memories,
        target_event,
        relation
    ):

        relation = str(
            relation
        ).upper()

        if relation not in self.TEMPORAL_RELATIONS:

            raise ValueError(
                f"Unsupported temporal relation: "
                f"{relation}"
            )

        target = self.normalize_event(
            target_event
        )

        result = []

        for event in self.sort_events(
            memories
        ):

            if (
                event["event_id"]
                ==
                target["event_id"]
            ):
                continue

            actual_relation = (
                self.relation_between(
                    event,
                    target
                )
            )

            # FOLLOWS means directly succeeding
            # in chronological event order.
            if relation == "FOLLOWS":

                continue

            if actual_relation == relation:

                result.append(event)

        return result

    # =========================================================
    # BEFORE EVENT
    # =========================================================

    def before_event(
        self,
        memories,
        keyword
    ):

        events = self.sort_events(
            memories
        )

        target = self.find_target_event(
            events,
            keyword
        )

        if target is None:
            return []

        return [
            event
            for event in events
            if self.relation_between(
                event,
                target
            ) == "BEFORE"
        ]

    # =========================================================
    # AFTER EVENT
    # =========================================================

    def after_event(
        self,
        memories,
        keyword
    ):

        events = self.sort_events(
            memories
        )

        target = self.find_target_event(
            events,
            keyword
        )

        if target is None:
            return []

        return [
            event
            for event in events
            if self.relation_between(
                event,
                target
            ) == "AFTER"
        ]

    # =========================================================
    # FIND TARGET EVENT
    # =========================================================

    def find_target_event(
        self,
        memories,
        keyword
    ):

        keyword = str(
            keyword
        ).lower()

        events = self.sort_events(
            memories
        )

        for event in events:

            event_text = " ".join(
                [
                    str(
                        event.get(
                            "description",
                            ""
                        )
                    ),

                    str(
                        event.get(
                            "event_type",
                            ""
                        )
                    ),

                    str(
                        event.get(
                            "class_name",
                            ""
                        )
                    ),

                    str(
                        event.get(
                            "object",
                            ""
                        )
                    )
                ]
            ).lower()

            if keyword in event_text:

                return event

        return None

    # =========================================================
    # FOLLOWS EVENT
    # =========================================================

    def follows_event(
        self,
        memories,
        target_event
    ):

        events = self.sort_events(
            memories
        )

        target_id = target_event.get(
            "event_id"
        )

        for index, event in enumerate(
            events
        ):

            if event["event_id"] == target_id:

                if index + 1 < len(events):

                    return events[
                        index + 1
                    ]

                return None

        return None

    # =========================================================
    # FIRST EVENT
    # =========================================================

    def find_first_event(
        self,
        memories,
        object_type="person"
    ):

        events = self.filter_events(
            memories,
            [
                "OBJECT_ENTER",
                "OBJECT_APPEARED"
            ],
            object_type
        )

        if not events:
            return None

        first = events[0]

        return {
            "answer": first["description"],

            "event_id": first["event_id"],

            "event_type": first["event_type"],

            "track_id": first["track_id"],

            "class_name": first["class_name"],

            "start_time": first["start_time"],

            "end_time": first["end_time"],

            "timestamp": first["start_time"],

            "start_frame": first["start_frame"],

            "confidence": first["confidence"],

            "description": first["description"]
        }

    # =========================================================
    # LAST EVENT
    # =========================================================

    def find_last_event(
        self,
        memories,
        object_type="person"
    ):

        events = self.filter_events(
            memories,
            [
                "OBJECT_ENTER",
                "OBJECT_APPEARED"
            ],
            object_type
        )

        if not events:
            return None

        last = events[-1]

        return {
            "answer": last["description"],

            "event_id": last["event_id"],

            "event_type": last["event_type"],

            "track_id": last["track_id"],

            "class_name": last["class_name"],

            "start_time": last["start_time"],

            "end_time": last["end_time"],

            "timestamp": last["start_time"],

            "start_frame": last["start_frame"],

            "confidence": last["confidence"],

            "description": last["description"]
        }

    # =========================================================
    # OBJECT APPEARANCE TIME
    # =========================================================

    def object_appearance_time(
        self,
        memories,
        object_name="person"
    ):

        events = self.filter_events(
            memories,
            [
                "OBJECT_ENTER",
                "OBJECT_APPEARED"
            ],
            object_name
        )

        if not events:
            return None

        first = events[0]

        return {
            "answer": (
                f"{object_name} appeared at "
                f"{first['start_time']} seconds."
            ),

            "timestamp": first["start_time"],

            "start_time": first["start_time"],

            "event_id": first["event_id"],

            "start_frame": first["start_frame"],

            "confidence": first["confidence"],

            "description": first["description"]
        }

    # =========================================================
    # COMPLETE TIMELINE
    # =========================================================

    def create_timeline(
        self,
        memories,
        limit=100
    ):

        events = self.sort_events(
            memories
        )

        timeline = []

        for event in events[:limit]:

            timeline.append({

                "time":
                    event["start_time"],

                "start_time":
                    event["start_time"],

                "end_time":
                    event["end_time"],

                "event":
                    event["description"],

                "event_type":
                    event["event_type"],

                "event_id":
                    event["event_id"],

                "class_name":
                    event["class_name"],

                "track_id":
                    event["track_id"]

            })

        return timeline

    def get_timeline(
        self,
        memories
    ):

        return self.create_timeline(
            memories
        )

    # =========================================================
    # TIME RANGE
    # =========================================================

    def events_in_time_range(
        self,
        memories,
        start_time,
        end_time
    ):

        start_time = float(
            start_time
        )

        end_time = float(
            end_time
        )

        if end_time < start_time:

            start_time, end_time = (
                end_time,
                start_time
            )

        result = []

        for event in self.sort_events(
            memories
        ):

            # Event intersects requested interval.
            if (
                event["end_time"] >= start_time
                and
                event["start_time"] <= end_time
            ):

                result.append(event)

        return result

    # =========================================================
    # PARSE TIME RANGE
    # =========================================================

    def parse_time_range(
        self,
        query
    ):

        patterns = [

            r"between\s+(\d+(?:\.\d+)?)"
            r"\s*(?:s|sec|secs|seconds)?"
            r"\s*(?:and|to|-)"
            r"\s*(\d+(?:\.\d+)?)",

            r"from\s+(\d+(?:\.\d+)?)"
            r"\s*(?:s|sec|secs|seconds)?"
            r"\s*(?:to|-)"
            r"\s*(\d+(?:\.\d+)?)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                query.lower()
            )

            if match:

                return (
                    float(match.group(1)),
                    float(match.group(2))
                )

        return None

    # =========================================================
    # OBJECT HISTORY
    # =========================================================

    def object_history(
        self,
        memories,
        object_name
    ):

        events = self.filter_events(
            memories,
            None,
            object_name
        )

        history = []

        for event in events:

            history.append({

                "time":
                    event["start_time"],

                "start_time":
                    event["start_time"],

                "end_time":
                    event["end_time"],

                "event":
                    event["event_type"],

                "description":
                    event["description"],

                "event_id":
                    event["event_id"]

            })

        return history