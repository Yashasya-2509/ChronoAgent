from pathlib import Path
import json
import re

from ultralytics import YOLO


class ObjectTracker:

    def __init__(
        self,
        model_name="yolo11n.pt",
        confidence=0.10,
        tracker_config="bytetrack.yaml"
    ):
        self.model_name = model_name
        self.confidence = confidence
        self.tracker_config = tracker_config

        print(
            f"[TRACKING] Loading model: {model_name}"
        )

        self.model = YOLO(model_name)

        print(
            "[TRACKING] Model loaded successfully."
        )

    # =========================================================
    # PUBLIC TRACK FUNCTION
    # =========================================================

    def track(
        self,
        video_path,
        detections=None,
        video_id=None,
        sample_fps=None
    ):

        if video_id is None:
            video_id = "unknown_video"

        output_path = Path(
            f"data/tracks/{video_id}_tracks.json"
        )

        print(
            "[TRACKING] Starting ByteTrack..."
        )

        self.track_video(
            video_path=video_path,
            video_id=video_id,
            output_path=output_path,
            sample_fps=sample_fps
        )

        with open(output_path, "r") as file:
            tracking_data = json.load(file)

        unique_objects = tracking_data[
            "unique_objects"
        ]

        print(
            f"[TRACKING] Unique objects: "
            f"{len(unique_objects)}"
        )

        return unique_objects

    # =========================================================
    # VIDEO TRACKING
    # =========================================================

    def track_video(
        self,
        video_path,
        video_id,
        output_path,
        sample_fps=None
    ):

        video_path = Path(video_path)
        output_path = Path(output_path)

        if not video_path.exists():
            raise FileNotFoundError(
                f"Video not found: {video_path}"
            )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            f"[TRACKING] Processing: {video_path}"
        )

        fps = self._get_fps(video_path)

        if fps <= 0:
            raise RuntimeError(
                "Unable to determine video FPS."
            )

        # -----------------------------------------------------
        # Sampling
        # -----------------------------------------------------

        if sample_fps and sample_fps > 0:

            frame_stride = max(
                1,
                round(fps / sample_fps)
            )

        else:

            frame_stride = 1

        print(
            f"[TRACKING] Video FPS   : {fps:.2f}"
        )

        print(
            f"[TRACKING] Sample FPS  : "
            f"{sample_fps if sample_fps else 'original'}"
        )

        print(
            f"[TRACKING] Frame stride: "
            f"{frame_stride}"
        )

        # -----------------------------------------------------
        # ByteTrack
        # -----------------------------------------------------

        results = self.model.track(
            source=str(video_path),
            conf=self.confidence,
            tracker=self.tracker_config,
            persist=True,
            stream=True,
            vid_stride=frame_stride,
            verbose=False
        )

        tracked_objects = []

        total_frames = 0
        frames_with_tracks = 0

        # =====================================================
        # PROCESS TRACKING RESULTS
        # =====================================================

        for frame_number, result in enumerate(results):

            total_frames += 1

            # No detections
            if result.boxes is None:
                continue

            # No tracking IDs
            if result.boxes.id is None:
                continue

            frames_with_tracks += 1

            track_ids = (
                result.boxes.id
                .int()
                .cpu()
                .tolist()
            )

            classes = (
                result.boxes.cls
                .int()
                .cpu()
                .tolist()
            )

            confidences = (
                result.boxes.conf
                .cpu()
                .tolist()
            )

            boxes = (
                result.boxes.xyxy
                .cpu()
                .tolist()
            )

            # -------------------------------------------------
            # Each tracked detection
            # -------------------------------------------------

            for (
                track_id,
                class_id,
                confidence,
                bbox
            ) in zip(
                track_ids,
                classes,
                confidences,
                boxes
            ):

                class_name = self.model.names[
                    int(class_id)
                ]

                is_person = (
                    class_name.lower() == "person"
                )

                object_type = (
                    "human"
                    if is_person
                    else "object"
                )

                # ---------------------------------------------
                # ORIGINAL VIDEO FRAME
                # ---------------------------------------------

                source_frame = (
                    frame_number * frame_stride
                )

                # ---------------------------------------------
                # ACTUAL VIDEO TIMESTAMP
                # ---------------------------------------------

                timestamp = (
                    source_frame / fps
                )

                tracked_objects.append(
                    {
                        "video_id": video_id,

                        "source_frame": int(
                            source_frame
                        ),

                        "timestamp": round(
                            timestamp,
                            3
                        ),

                        "track_id": int(
                            track_id
                        ),

                        "class_id": int(
                            class_id
                        ),

                        "class_name": class_name,

                        "object_type": object_type,

                        "is_person": is_person,

                        "confidence": round(
                            float(confidence),
                            3
                        ),

                        "bbox": {
                            "x1": float(
                                bbox[0]
                            ),
                            "y1": float(
                                bbox[1]
                            ),
                            "x2": float(
                                bbox[2]
                            ),
                            "y2": float(
                                bbox[3]
                            )
                        }
                    }
                )

        # =====================================================
        # BUILD UNIQUE OBJECT INVENTORY
        # =====================================================

        unique_objects = {}

        # Separate numbering:
        #
        # PERSON_001
        # PERSON_002
        #
        # CAR_001
        # CAR_002
        #
        # TRUCK_001
        # TRUCK_002

        class_counters = {}

        for observation in tracked_objects:

            track_id = observation[
                "track_id"
            ]

            class_name = observation[
                "class_name"
            ]

            # -------------------------------------------------
            # Internal identity
            # -------------------------------------------------

            identity_key = (
                class_name,
                track_id
            )

            # -------------------------------------------------
            # First observation of this object
            # -------------------------------------------------

            if identity_key not in unique_objects:

                normalized_class = (
                    self._normalize_class_name(
                        class_name
                    )
                )

                if normalized_class not in class_counters:

                    class_counters[
                        normalized_class
                    ] = 0

                class_counters[
                    normalized_class
                ] += 1

                object_number = class_counters[
                    normalized_class
                ]

                object_id = (
                    f"{normalized_class}_"
                    f"{object_number:03d}"
                )

                unique_objects[
                    identity_key
                ] = {

                    # -----------------------------------------
                    # Human-readable unique ID
                    # -----------------------------------------

                    "object_id": object_id,

                    # -----------------------------------------
                    # Internal ByteTrack ID
                    # -----------------------------------------

                    "track_id": track_id,

                    # -----------------------------------------
                    # Object information
                    # -----------------------------------------

                    "object": class_name,

                    "object_type":
                        observation[
                            "object_type"
                        ],

                    # -----------------------------------------
                    # First appearance
                    # -----------------------------------------

                    "first_seen":
                        observation[
                            "timestamp"
                        ],

                    "first_frame":
                        observation[
                            "source_frame"
                        ],

                    # -----------------------------------------
                    # Last appearance
                    # -----------------------------------------

                    "last_seen":
                        observation[
                            "timestamp"
                        ],

                    "last_frame":
                        observation[
                            "source_frame"
                        ],

                    # -----------------------------------------
                    # Detection count
                    # -----------------------------------------

                    "observations": 1
                }

            # -------------------------------------------------
            # Existing object
            # -------------------------------------------------

            else:

                unique_objects[
                    identity_key
                ][
                    "last_seen"
                ] = observation[
                    "timestamp"
                ]

                unique_objects[
                    identity_key
                ][
                    "last_frame"
                ] = observation[
                    "source_frame"
                ]

                unique_objects[
                    identity_key
                ][
                    "observations"
                ] += 1

        # =====================================================
        # CONVERT TO LIST
        # =====================================================

        unique_objects_list = list(
            unique_objects.values()
        )

        # =====================================================
        # CALCULATE DURATION
        # =====================================================

        for obj in unique_objects_list:

            duration = (
                obj["last_seen"]
                -
                obj["first_seen"]
            )

            obj["duration"] = round(
                max(0.0, duration),
                3
            )

        # =====================================================
        # SORT BY FIRST APPEARANCE
        # =====================================================

        unique_objects_list.sort(
            key=lambda obj: (
                obj["first_seen"],
                obj["object_id"]
            )
        )

        # =====================================================
        # FINAL JSON
        # =====================================================

        output = {

            "video_id": video_id,

            "video_path":
                str(video_path),

            "fps": fps,

            "total_frames":
                total_frames,

            "frames_with_tracks":
                frames_with_tracks,

            "unique_object_count":
                len(unique_objects_list),

            "unique_objects":
                unique_objects_list,

            # -------------------------------------------------
            # Raw observations remain in backend.
            #
            # These are NOT displayed to user.
            # They will later support:
            #
            # - event detection
            # - evidence retrieval
            # - temporal reasoning
            # - knowledge graph
            # -------------------------------------------------

            "observations":
                tracked_objects
        }

        # =====================================================
        # SAVE TRACKING DATA
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

        # =====================================================
        # USER-FACING OUTPUT
        # =====================================================

        print()

        print(
            "=" * 70
        )

        print(
            "UNIQUE OBJECT INVENTORY"
        )

        print(
            "=" * 70
        )

        print(
            f"{'ID':<15}"
            f"{'OBJECT':<15}"
            f"{'FIRST SEEN':<15}"
            f"{'LAST SEEN':<15}"
            f"{'DURATION':<10}"
        )

        print(
            "-" * 70
        )

        for obj in unique_objects_list:

            print(
                f"{obj['object_id']:<15}"
                f"{obj['object']:<15}"
                f"{obj['first_seen']:>8.2f}s"
                f"{'':7}"
                f"{obj['last_seen']:>8.2f}s"
                f"{'':7}"
                f"{obj['duration']:>7.2f}s"
            )

        print(
            "-" * 70
        )

        print(
            f"TOTAL UNIQUE OBJECTS: "
            f"{len(unique_objects_list)}"
        )

        print(
            "=" * 70
        )

        print()

        # =====================================================
        # BACKEND INFORMATION
        # =====================================================

        print(
            f"[TRACKING] Frames processed : "
            f"{total_frames}"
        )

        print(
            f"[TRACKING] Frames with tracks: "
            f"{frames_with_tracks}"
        )

        print(
            f"[TRACKING] Raw observations : "
            f"{len(tracked_objects)}"
        )

        print(
            f"[TRACKING] Unique objects   : "
            f"{len(unique_objects_list)}"
        )

        print(
            f"[TRACKING] Saved            : "
            f"{output_path}"
        )

        return output_path

    # =========================================================
    # NORMALIZE CLASS NAME
    # =========================================================

    @staticmethod
    def _normalize_class_name(
        class_name
    ):

        # Convert:
        #
        # "cell phone" → "CELL_PHONE"
        # "traffic light" → "TRAFFIC_LIGHT"
        # "person" → "PERSON"

        normalized = class_name.strip().lower()

        normalized = re.sub(
            r"[^a-z0-9]+",
            "_",
            normalized
        )

        normalized = normalized.strip(
            "_"
        )

        return normalized.upper()

    # =========================================================
    # FPS READER
    # =========================================================

    @staticmethod
    def _get_fps(
        video_path
    ):

        import cv2

        cap = cv2.VideoCapture(
            str(video_path)
        )

        fps = cap.get(
            cv2.CAP_PROP_FPS
        )

        cap.release()

        return (
            fps
            if fps > 0
            else 30.0
        )