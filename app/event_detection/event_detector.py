from pathlib import Path
import json


class EventDetector:

    def __init__(self):

        print("[EVENT] Event Detector initialized")

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _get_class_name(observation):

        return (
            observation.get("class_name")
            or observation.get("label")
            or observation.get("object")
            or "unknown"
        )

    @staticmethod
    def _make_entity_id(class_name, track_id):

        normalized = str(class_name).upper()
        normalized = normalized.replace(" ", "_")

        try:

            track_number = int(track_id)

            return f"{normalized}_{track_number:03d}"

        except (TypeError, ValueError):

            return f"{normalized}_{track_id}"

    @staticmethod
    def _make_event_id(events):

        return f"E{len(events) + 1:05d}"

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

        if not tracks and not vlm_results:

            return events

        # =====================================================
        # VIDEO ID
        # =====================================================

        if video_id is None:

            if tracks:

                video_id = tracks[0].get(
                    "video_id",
                    "unknown_video"
                )

            elif vlm_results:

                video_id = vlm_results[0].get(
                    "video_id",
                    "unknown_video"
                )

            else:

                video_id = "unknown_video"

        # =====================================================
        # GROUP TRACKS
        # =====================================================

        grouped_tracks = {}

        for observation in tracks or []:

            track_id = observation.get(
                "track_id"
            )

            if track_id is None:

                continue

            grouped_tracks.setdefault(
                track_id,
                []
            ).append(observation)

        # =====================================================
        # OBJECT EVENTS
        # =====================================================

        for track_id, observations in grouped_tracks.items():

            observations.sort(
                key=lambda item:
                item.get(
                    "timestamp",
                    0.0
                )
            )

            if not observations:

                continue

            first = observations[0]

            last = observations[-1]

            # =================================================
            # CLASS NAME
            # =================================================

            class_name = self._get_class_name(
                first
            )

            # =================================================
            # CANONICAL ENTITY ID
            # =================================================

            subject_id = self._make_entity_id(
                class_name,
                track_id
            )

            # =================================================
            # CONFIDENCE
            # =================================================

            confidence = first.get(
                "confidence",
                0.0
            )

            # =================================================
            # TIME
            # =================================================

            first_time = first.get(
                "timestamp",
                0.0
            )

            last_time = last.get(
                "timestamp",
                first_time
            )

            # =================================================
            # FRAME
            # =================================================

            first_frame = first.get(
                "frame_id",
                first.get(
                    "frame_number",
                    "unknown"
                )
            )

            last_frame = last.get(
                "frame_id",
                last.get(
                    "frame_number",
                    first_frame
                )
            )

            # =================================================
            # ENTER EVENT
            # =================================================

            events.append({

                "event_id":
                    self._make_event_id(events),

                "video_id":
                    video_id,

                "event_type":
                    "OBJECT_ENTER",

                # Canonical subject fields
                "subject_id":
                    subject_id,

                "subject_class":
                    class_name,

                "subject_track_id":
                    track_id,

                # Backward-compatible fields
                "subject":
                    subject_id,

                "action":
                    "entered",

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
                    (
                        f"{class_name} track {track_id} "
                        "appeared first in the scene."
                    )

            })

            # =================================================
            # MOVEMENT EVENT
            # =================================================

            if len(observations) > 3:

                events.append({

                    "event_id":
                        self._make_event_id(events),

                    "video_id":
                        video_id,

                    "event_type":
                        "OBJECT_MOVEMENT",

                    "subject_id":
                        subject_id,

                    "subject_class":
                        class_name,

                    "subject_track_id":
                        track_id,

                    "subject":
                        subject_id,

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
                        (
                            f"{class_name} track {track_id} "
                            "moved in the scene."
                        )

                })

            # =================================================
            # EXIT EVENT
            # =================================================

            if last_time > first_time:

                events.append({

                    "event_id":
                        self._make_event_id(events),

                    "video_id":
                        video_id,

                    "event_type":
                        "OBJECT_EXIT",

                    "subject_id":
                        subject_id,

                    "subject_class":
                        class_name,

                    "subject_track_id":
                        track_id,

                    "subject":
                        subject_id,

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
                        (
                            f"{class_name} track {track_id} "
                            "left the scene."
                        )

                })

        # =====================================================
        # VLM SCENE EVENTS
        # =====================================================

        if vlm_results:

            for result in vlm_results:

                timestamp = result.get(
                    "timestamp",
                    0.0
                )

                description = result.get(
                    "description",
                    ""
                )

                if not description:

                    continue

                events.append({

                    "event_id":
                        self._make_event_id(events),

                    "video_id":
                        video_id,

                    "event_type":
                        "SCENE_DESCRIPTION",

                    "subject_id":
                        "SCENE",

                    "subject_class":
                        "scene",

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

                    "start_frame":
                        result.get(
                            "frame_id"
                        ),

                    "end_frame":
                        result.get(
                            "frame_id"
                        ),

                    "confidence":
                        result.get(
                            "confidence",
                            0.0
                        ),

                    "description":
                        description,

                    # VLM evidence
                    "vlm_objects":
                        result.get(
                            "objects",
                            []
                        ),

                    "vlm_object_counts":
                        result.get(
                            "object_counts",
                            {}
                        ),

                    "vlm_detections":
                        result.get(
                            "detections",
                            0
                        )

                })

        # =====================================================
        # SORT EVENTS CHRONOLOGICALLY
        # =====================================================

        events.sort(
            key=lambda event:
            event.get(
                "start_time",
                0.0
            )
        )

        # =====================================================
        # RE-NUMBER EVENTS AFTER SORTING
        #
        # This ensures event IDs themselves follow the
        # chronological order of the video.
        #
        # Example:
        #
        # E00001 -> 10.2 sec
        # E00002 -> 15.7 sec
        # E00003 -> 21.4 sec
        #
        # instead of IDs being assigned according to the
        # order in which different event types were created.
        # =====================================================

        for index, event in enumerate(
            events,
            start=1
        ):

            event["event_id"] = (
                f"E{index:05d}"
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

        # =====================================================
        # LOAD TRACKING MANIFEST
        # =====================================================

        with open(
            tracking_manifest_path,
            "r"
        ) as file:

            data = json.load(file)

        video_id = data.get(
            "video_id",
            "unknown_video"
        )

        tracks = data.get(
            "tracks",
            data.get(
                "observations",
                []
            )
        )

        # =====================================================
        # DETECT EVENTS
        # =====================================================

        events = self.detect(
            tracks,
            video_id=video_id
        )

        # =====================================================
        # CREATE OUTPUT DIRECTORY
        # =====================================================

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # =====================================================
        # OUTPUT
        # =====================================================

        output = {

            "video_id":
                video_id,

            "total_events":
                len(events),

            "events":
                events

        }

        # =====================================================
        # SAVE
        # =====================================================

        with open(
            output_path,
            "w"
        ) as file:

            json.dump(
                output,
                file,
                indent=2
            )

        print(
            f"[EVENT] Saved: {output_path}"
        )

        print(
            f"[EVENT] Total events: {len(events)}"
        )

        return events