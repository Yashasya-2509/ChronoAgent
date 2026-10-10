from pathlib import Path


class EvidenceRetriever:

    def __init__(
        self,
        context_before=2.0,
        context_after=2.0
    ):
        """
        EvidenceRetriever handles:

        1. Evidence frame extraction
        2. Evidence timestamp extraction
        3. Evidence frame-path resolution
        4. Timeline evidence
        5. Related-event evidence
        6. Rewinder context generation

        Rewinder automatically creates a video context window
        around the detected event.

        Example:

            Event:
                31.2s - 32.1s

            Context:
                29.2s - 34.1s
        """

        self.context_before = float(
            context_before
        )

        self.context_after = float(
            context_after
        )

    # =====================================================
    # GET FRAME ID
    # =====================================================

    def _get_frame_id(
        self,
        event
    ):
        """
        Extract the best available evidence frame ID.
        """

        if not isinstance(
            event,
            dict
        ):
            return ""

        for key in (
            "start_frame",
            "frame_id",
            "frame",
            "evidence_frame"
        ):

            value = event.get(
                key
            )

            if value not in (
                None,
                ""
            ):

                return value

        evidence_frames = event.get(
            "evidence_frames",
            []
        )

        if evidence_frames:

            first_frame = (
                evidence_frames[0]
            )

            if isinstance(
                first_frame,
                dict
            ):

                for key in (
                    "frame_id",
                    "frame",
                    "id"
                ):

                    value = (
                        first_frame.get(
                            key
                        )
                    )

                    if value not in (
                        None,
                        ""
                    ):

                        return value

            else:

                return first_frame

        return ""

    # =====================================================
    # GET START TIMESTAMP
    # =====================================================

    def _get_timestamp(
        self,
        event
    ):
        """
        Extract event start timestamp.
        """

        if not isinstance(
            event,
            dict
        ):
            return 0.0

        for key in (
            "start_time",
            "timestamp",
            "time"
        ):

            value = event.get(
                key
            )

            if value is not None:

                try:

                    return float(
                        value
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    pass

        return 0.0

    # =====================================================
    # GET END TIMESTAMP
    # =====================================================

    def _get_end_timestamp(
        self,
        event
    ):
        """
        Extract event end timestamp.

        If end_time does not exist, the event is treated
        as an instantaneous event.
        """

        if not isinstance(
            event,
            dict
        ):
            return self._get_timestamp(
                event
            )

        for key in (
            "end_time",
            "end_timestamp"
        ):

            value = event.get(
                key
            )

            if value is not None:

                try:

                    return float(
                        value
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    pass

        return self._get_timestamp(
            event
        )

    # =====================================================
    # GET EVENT DESCRIPTION
    # =====================================================

    def _get_event_description(
        self,
        event
    ):
        """
        Extract human-readable event description.
        """

        if not isinstance(
            event,
            dict
        ):
            return str(event)

        for key in (
            "description",
            "event",
            "action"
        ):

            value = event.get(
                key
            )

            if value:

                return str(
                    value
                )

        # -------------------------------------------------
        # Fallback using event type
        # -------------------------------------------------

        event_type = event.get(
            "event_type",
            ""
        )

        subject = (
            event.get(
                "subject_id"
            )
            or
            event.get(
                "subject"
            )
            or
            event.get(
                "entity_id"
            )
            or
            ""
        )

        if subject and event_type:

            return (
                f"{subject} "
                f"{event_type.replace('_', ' ').lower()}"
            )

        if event_type:

            return event_type.replace(
                "_",
                " "
            ).lower()

        return ""

    # =====================================================
    # RESOLVE FRAME PATH
    # =====================================================

    def _resolve_frame_path(
        self,
        video_id,
        frame_id,
        event
    ):
        """
        Resolve the actual physical frame path.

        Priority:

        1. frame_path stored inside event
        2. path/image_path/frame_file
        3. data/frames/<video_id>/<frame_id>.jpg
        4. jpeg/png alternatives
        """

        if not isinstance(
            event,
            dict
        ):
            event = {}

        # -------------------------------------------------
        # 1. Explicit frame_path
        # -------------------------------------------------

        explicit_path = event.get(
            "frame_path"
        )

        if explicit_path:

            path = Path(
                explicit_path
            )

            if path.exists():

                return str(
                    path
                )

        # -------------------------------------------------
        # 2. Alternative path fields
        # -------------------------------------------------

        for key in (
            "path",
            "image_path",
            "frame_file"
        ):

            value = event.get(
                key
            )

            if value:

                path = Path(
                    value
                )

                if path.exists():

                    return str(
                        path
                    )

        # -------------------------------------------------
        # No frame ID
        # -------------------------------------------------

        if frame_id in (
            None,
            "",
            "None"
        ):

            return None

        # -------------------------------------------------
        # Standard ChronoAgent frame directory
        # -------------------------------------------------

        frames_path = (
            Path("data/frames")
            / str(video_id)
        )

        frame_id = str(
            frame_id
        )

        candidates = [

            frames_path /
            f"{frame_id}.jpg",

            frames_path /
            f"{frame_id}.jpeg",

            frames_path /
            f"{frame_id}.png"

        ]

        for path in candidates:

            if path.exists():

                return str(
                    path
                )

        return None

    # =====================================================
    # BUILD REWINDER
    # =====================================================

    def _build_rewinder(
        self,
        video_id,
        event
    ):
        """
        Build dynamic Rewinder metadata.

        The Rewinder does not modify the original event.

        It calculates a context window:

            context_start =
                event_start - context_before

            context_end =
                event_end + context_after

        The start time is clamped to zero.

        Example:

            event:
                31.2 - 32.1

            context:
                29.2 - 34.1
        """

        event_start = self._get_timestamp(
            event
        )

        event_end = self._get_end_timestamp(
            event
        )

        # Protect against malformed intervals.
        if event_end < event_start:

            event_end = event_start

        context_start = max(
            0.0,
            event_start
            -
            self.context_before
        )

        context_end = (
            event_end
            +
            self.context_after
        )

        event_id = ""

        if isinstance(
            event,
            dict
        ):

            event_id = (
                event.get(
                    "event_id"
                )
                or
                event.get(
                    "memory_id"
                )
                or
                ""
            )

        return {

            "available":
                True,

            "event_id":
                event_id,

            "video_id":
                video_id,

            "event_start":
                event_start,

            "event_end":
                event_end,

            "context_start":
                round(
                    context_start,
                    3
                ),

            "context_end":
                round(
                    context_end,
                    3
                ),

            "context_before":
                self.context_before,

            "context_after":
                self.context_after,

            "action":
                self._get_event_description(
                    event
                ),

            "seek_time":
                event_start

        }

    # =====================================================
    # NORMALIZE EVENT
    # =====================================================

    def _normalize_event(
        self,
        video_id,
        event
    ):
        """
        Convert ChronoAgent event data into a
        consistent evidence structure.

        Rewinder metadata is included automatically.
        """

        if not isinstance(
            event,
            dict
        ):

            return {

                "time":
                    0.0,

                "event":
                    str(event),

                "frame_id":
                    "",

                "frame_path":
                    None,

                "rewinder":
                    {

                        "available":
                            False

                    }

            }

        frame_id = (
            self._get_frame_id(
                event
            )
        )

        timestamp = (
            self._get_timestamp(
                event
            )
        )

        end_timestamp = (
            self._get_end_timestamp(
                event
            )
        )

        description = (
            self._get_event_description(
                event
            )
        )

        frame_path = (
            self._resolve_frame_path(
                video_id,
                frame_id,
                event
            )
        )

        rewinder = (
            self._build_rewinder(
                video_id,
                event
            )
        )

        return {

            "time":
                timestamp,

            "end_time":
                end_timestamp,

            "event":
                description,

            "event_id":
                event.get(
                    "event_id",
                    ""
                ),

            "event_type":
                event.get(
                    "event_type",
                    ""
                ),

            "frame_id":
                frame_id,

            "frame_path":
                frame_path,

            "rewinder":
                rewinder

        }

    # =====================================================
    # GET EVIDENCE
    # =====================================================

    def get_evidence(
        self,
        video_id,
        reasoning_result
    ):
        """
        Convert reasoning output into evidence
        and Rewinder metadata.
        """

        if not isinstance(
            reasoning_result,
            dict
        ):

            reasoning_result = {

                "description":
                    str(reasoning_result)

            }

        # =================================================
        # TIMELINE EVIDENCE
        # =================================================

        if "timeline" in reasoning_result:

            evidence = []

            for event in reasoning_result[
                "timeline"
            ]:

                evidence.append(

                    self._normalize_event(

                        video_id,

                        event

                    )

                )

            return {

                "video_id":
                    video_id,

                "type":
                    "timeline",

                "events":
                    evidence

            }

        # =================================================
        # RELATED EVENTS
        # =================================================

        if "related_events" in reasoning_result:

            evidence = []

            for event in reasoning_result[
                "related_events"
            ]:

                evidence.append(

                    self._normalize_event(

                        video_id,

                        event

                    )

                )

            return {

                "video_id":
                    video_id,

                "type":
                    "timeline",

                "events":
                    evidence

            }

        # =================================================
        # SINGLE EVENT EVIDENCE
        # =================================================

        evidence = (
            self._normalize_event(
                video_id,
                reasoning_result
            )
        )

        return {

            "video_id":
                video_id,

            "type":
                "single_event",

            "event":
                evidence

        }