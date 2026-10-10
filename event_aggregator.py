cat > app/event_detection/event_aggregator.py <<'PY'
from collections import defaultdict


class EventAggregator:
    """
    Converts low-level temporal observations into compact
    event-centric memory units.

    Example:

        PERSON_017
        OBJECT_MOVEMENT 10.2 -> 10.6
        OBJECT_MOVEMENT 10.8 -> 12.0
        OBJECT_MOVEMENT 13.0 -> 14.0

    becomes:

        PERSON_017
        MOVED
        10.2 -> 14.0

    A temporal gap greater than max_event_gap creates
    a new event.
    """

    def __init__(
        self,
        time_window=2.0,
        max_event_gap=1.5,
        min_event_duration=0.5
    ):

        self.time_window = float(time_window)
        self.max_event_gap = float(max_event_gap)
        self.min_event_duration = float(
            min_event_duration
        )

        print("[EVENT AGGREGATOR] Initialized")
        print(
            f"[EVENT AGGREGATOR] Max gap: "
            f"{self.max_event_gap}s"
        )
        print(
            f"[EVENT AGGREGATOR] Min duration: "
            f"{self.min_event_duration}s"
        )

    # =========================================================
    # ENTITY ID
    # =========================================================

    @staticmethod
    def get_entity_id(event):

        # Preferred canonical ID
        if event.get("subject_id"):
            return str(event["subject_id"])

        # Existing entity ID
        if event.get("entity_id"):
            return str(event["entity_id"])

        # Object ID
        if event.get("object_id"):
            return str(event["object_id"])

        # Construct ID from class + track
        track_id = event.get("subject_track_id")

        if track_id is None:
            track_id = event.get("track_id")

        if track_id is not None:

            class_name = (
                event.get("subject_class")
                or event.get("class_name")
                or event.get("object")
                or "object"
            )

            class_name = (
                str(class_name)
                .strip()
                .upper()
                .replace(" ", "_")
            )

            try:
                return f"{class_name}_{int(track_id):03d}"
            except (ValueError, TypeError):
                return f"{class_name}_{track_id}"

        return str(
            event.get("object")
            or event.get("class_name")
            or "UNKNOWN"
        )

    # =========================================================
    # TIME
    # =========================================================

    @staticmethod
    def get_start_time(event):

        if event.get("start_time") is not None:
            return float(event["start_time"])

        if event.get("timestamp") is not None:
            return float(event["timestamp"])

        if event.get("time") is not None:
            return float(event["time"])

        return 0.0

    @staticmethod
    def get_end_time(event):

        if event.get("end_time") is not None:
            return float(event["end_time"])

        if event.get("timestamp") is not None:
            return float(event["timestamp"])

        if event.get("time") is not None:
            return float(event["time"])

        return EventAggregator.get_start_time(event)

    # =========================================================
    # EVENT TYPE
    # =========================================================

    @staticmethod
    def get_event_type(event):

        event_type = str(
            event.get("event_type")
            or event.get("type")
            or "UNKNOWN"
        ).upper()

        mapping = {
            "OBJECT_MOVEMENT": "MOVED",
            "OBJECT_STATIONARY": "STATIONARY",
            "OBJECT_ENTER": "ENTERED",
            "OBJECT_EXIT": "EXITED",
            "SCENE_DESCRIPTION": "SCENE_DESCRIPTION"
        }

        return mapping.get(
            event_type,
            event_type
        )

    # =========================================================
    # DURATION
    # =========================================================

    @staticmethod
    def get_duration(event):

        if event.get("duration") is not None:
            return max(
                0.0,
                float(event["duration"])
            )

        start = EventAggregator.get_start_time(
            event
        )

        end = EventAggregator.get_end_time(
            event
        )

        return max(
            0.0,
            end - start
        )

    # =========================================================
    # SORT
    # =========================================================

    @staticmethod
    def sort_events(events):

        return sorted(
            events,
            key=lambda event: (
                EventAggregator.get_start_time(
                    event
                ),
                EventAggregator.get_entity_id(
                    event
                )
            )
        )

    # =========================================================
    # DEDUPLICATION
    # =========================================================

    def remove_duplicates(self, events):

        unique = []
        seen = set()

        for event in events:

            key = (
                self.get_event_type(event),
                self.get_entity_id(event),
                round(
                    self.get_start_time(event),
                    3
                ),
                round(
                    self.get_end_time(event),
                    3
                )
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(event.copy())

        return unique

    # =========================================================
    # EVIDENCE
    # =========================================================

    @staticmethod
    def collect_evidence_frames(events):

        frames = []

        for event in events:

            evidence = event.get(
                "evidence_frames"
            )

            if evidence:
                frames.extend(evidence)

            for field in [
                "source_frame",
                "start_frame",
                "end_frame"
            ]:

                value = event.get(field)

                if value is not None:
                    frames.append(value)

        # Remove duplicates while preserving order
        result = []
        seen = set()

        for frame in frames:

            key = str(frame)

            if key in seen:
                continue

            seen.add(key)
            result.append(frame)

        return result

    # =========================================================
    # CREATE AGGREGATED EVENT
    # =========================================================

    def create_aggregated_event(
        self,
        events
    ):

        events = self.sort_events(events)

        first = events[0]
        last = events[-1]

        entity_id = self.get_entity_id(
            first
        )

        event_type = self.get_event_type(
            first
        )

        start_time = min(
            self.get_start_time(event)
            for event in events
        )

        end_time = max(
            self.get_end_time(event)
            for event in events
        )

        duration = max(
            0.0,
            end_time - start_time
        )

        # Average confidence
        confidence_values = [
            float(event["confidence"])
            for event in events
            if event.get("confidence") is not None
        ]

        if confidence_values:

            confidence = (
                sum(confidence_values)
                / len(confidence_values)
            )

        else:

            confidence = 0.0

        subject_class = (
            first.get("subject_class")
            or first.get("class_name")
            or first.get("object")
        )

        subject_track_id = (
            first.get("subject_track_id")
        )

        if subject_track_id is None:
            subject_track_id = first.get(
                "track_id"
            )

        # Description
        if event_type == "MOVED":

            description = (
                f"{entity_id} moved from "
                f"{start_time:.2f}s to "
                f"{end_time:.2f}s."
            )

        elif event_type == "STATIONARY":

            description = (
                f"{entity_id} remained stationary "
                f"from {start_time:.2f}s to "
                f"{end_time:.2f}s."
            )

        else:

            description = (
                first.get("description")
                or f"{entity_id} "
                f"{event_type.lower()}."
            )

        aggregated = {

            # Assigned later
            "event_id": "",

            "video_id": first.get(
                "video_id"
            ),

            "event_type": event_type,

            # Canonical identity
            "entity_id": entity_id,
            "subject_id": first.get(
                "subject_id",
                entity_id
            ),
            "subject_class": subject_class,
            "subject_track_id": subject_track_id,

            # Compatibility
            "subject": first.get(
                "subject",
                subject_class
            ),
            "object": first.get(
                "object"
            ),
            "class_name": first.get(
                "class_name",
                subject_class
            ),
            "track_id": first.get(
                "track_id",
                subject_track_id
            ),

            # Action / target
            "action": first.get(
                "action"
            ),
            "target_id": first.get(
                "target_id"
            ),
            "target_class": first.get(
                "target_class"
            ),
            "target_track_id": first.get(
                "target_track_id"
            ),

            # Temporal
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,

            "start_frame": first.get(
                "start_frame",
                first.get("source_frame")
            ),

            "end_frame": last.get(
                "end_frame",
                last.get("source_frame")
            ),

            # Metadata
            "confidence": confidence,
            "observation_count": len(events),

            "description": description,

            "evidence_frames":
                self.collect_evidence_frames(
                    events
                )
        }

        # Preserve useful fields
        for field in [
            "scene_id",
            "location",
            "target",
            "camera_id"
        ]:

            if first.get(field) is not None:
                aggregated[field] = first[field]

        # Preserve VLM information
        if event_type == "SCENE_DESCRIPTION":

            aggregated[
                "vlm_objects"
            ] = first.get(
                "vlm_objects",
                []
            )

            aggregated[
                "vlm_object_counts"
            ] = first.get(
                "vlm_object_counts",
                {}
            )

            aggregated[
                "vlm_detections"
            ] = first.get(
                "vlm_detections",
                []
            )

        return aggregated

    # =========================================================
    # TEMPORAL AGGREGATION
    # =========================================================

    def aggregate_temporal_events(
        self,
        events
    ):

        if not events:
            return []

        groups = defaultdict(list)

        # Group by entity + event type
        for event in self.sort_events(events):

            key = (
                self.get_entity_id(event),
                self.get_event_type(event)
            )

            groups[key].append(event)

        aggregated = []

        # Process every entity independently
        for group_events in groups.values():

            group_events = self.sort_events(
                group_events
            )

            current_group = []
            current_end = None

            for event in group_events:

                start_time = (
                    self.get_start_time(event)
                )

                end_time = (
                    self.get_end_time(event)
                )

                # First event
                if not current_group:

                    current_group = [event]
                    current_end = end_time
                    continue

                # Gap from current group's END
                gap = start_time - current_end

                # Merge
                if gap <= self.max_event_gap:

                    current_group.append(event)

                    current_end = max(
                        current_end,
                        end_time
                    )

                # New event
                else:

                    aggregated.append(
                        self.create_aggregated_event(
                            current_group
                        )
                    )

                    current_group = [event]
                    current_end = end_time

            # Flush last group
            if current_group:

                aggregated.append(
                    self.create_aggregated_event(
                        current_group
                    )
                )

        return self.sort_events(
            aggregated
        )

    # =========================================================
    # FILTER SHORT EVENTS
    # =========================================================

    def filter_short_events(self, events):

        filtered = []

        always_keep = {
            "ENTERED",
            "EXITED",
            "SCENE_DESCRIPTION"
        }

        for event in events:

            event_type = self.get_event_type(
                event
            )

            duration = self.get_duration(
                event
            )

            if event_type in always_keep:

                filtered.append(event)

            elif duration >= self.min_event_duration:

                filtered.append(event)

        return filtered

    # =========================================================
    # ASSIGN EVENT IDS
    # =========================================================

    @staticmethod
    def assign_event_ids(events):

        events = EventAggregator.sort_events(
            events
        )

        for index, event in enumerate(
            events,
            start=1
        ):

            event["event_id"] = (
                f"E{index:05d}"
            )

        return events

    # =========================================================
    # MAIN PIPELINE
    # =========================================================

    def aggregate(self, events):

        print(
            f"[EVENT AGGREGATOR] Input events: "
            f"{len(events)}"
        )

        if not events:
            return []

        # Step 1
        unique_events = (
            self.remove_duplicates(events)
        )

        print(
            f"[EVENT AGGREGATOR] "
            f"After deduplication: "
            f"{len(unique_events)}"
        )

        # Step 2
        temporal_events = (
            self.aggregate_temporal_events(
                unique_events
            )
        )

        print(
            f"[EVENT AGGREGATOR] "
            f"After temporal aggregation: "
            f"{len(temporal_events)}"
        )

        # Step 3
        filtered_events = (
            self.filter_short_events(
                temporal_events
            )
        )

        # Step 4
        final_events = (
            self.assign_event_ids(
                filtered_events
            )
        )

        print(
            f"[EVENT AGGREGATOR] Final events: "
            f"{len(final_events)}"
        )

        return final_events
PY