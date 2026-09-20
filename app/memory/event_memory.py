from pathlib import Path
import json
from datetime import datetime


class EventMemory:

    def __init__(self):
        self.memory = []

    # -------------------------------------------------
    # ADD EVENT
    # -------------------------------------------------

    def add_event(self, event):

        video_id = event["video_id"]

        start_frame = event.get("start_frame")
        end_frame = event.get("end_frame")

        # Build visual evidence paths dynamically
        start_frame_path = None
        end_frame_path = None

        if start_frame:
            start_frame_path = str(
                Path("data/frames")
                / video_id
                / f"{start_frame}.jpg"
            )

        if end_frame:
            end_frame_path = str(
                Path("data/frames")
                / video_id
                / f"{end_frame}.jpg"
            )

        memory_item = {

            # -----------------------------
            # MEMORY ID
            # -----------------------------

            "memory_id":
                f"M{len(self.memory) + 1:05d}",

            # -----------------------------
            # VIDEO INFORMATION
            # -----------------------------

            "video_id":
                video_id,

            # -----------------------------
            # EVENT INFORMATION
            # -----------------------------

            "event_id":
                event["event_id"],

            "event_type":
                event["event_type"],

            "track_id":
                event.get("track_id"),

            "class_name":
                event.get("class_name"),

            # -----------------------------
            # TEMPORAL INFORMATION
            # -----------------------------

            "start_time":
                event["start_time"],

            "end_time":
                event["end_time"],

            # -----------------------------
            # FRAME EVIDENCE
            # -----------------------------

            "start_frame":
                start_frame,

            "end_frame":
                end_frame,

            "evidence": {

                "start_frame_path":
                    start_frame_path,

                "end_frame_path":
                    end_frame_path
            },

            # -----------------------------
            # SEMANTIC INFORMATION
            # -----------------------------

            "description":
                event.get(
                    "description",
                    ""
                ),

            "confidence":
                event.get(
                    "confidence",
                    0.0
                ),

            # -----------------------------
            # MEMORY METADATA
            # -----------------------------

            "created_at":
                datetime.now().isoformat()
        }

        self.memory.append(memory_item)

        return memory_item

    # -------------------------------------------------
    # ADD MULTIPLE EVENTS
    # -------------------------------------------------

    def add_events(self, events):

        for event in events:
            self.add_event(event)

        return self.memory

    # -------------------------------------------------
    # SAVE MEMORY
    # -------------------------------------------------

    def save(self, output_path):

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        data = {
            "total_memories":
                len(self.memory),

            "memories":
                self.memory
        }

        with open(
            output_path,
            "w"
        ) as file:

            json.dump(
                data,
                file,
                indent=2
            )

        return output_path

    # -------------------------------------------------
    # LOAD MEMORY
    # -------------------------------------------------

    def load(self, input_path):

        input_path = Path(input_path)

        if not input_path.exists():

            raise FileNotFoundError(
                input_path
            )

        with open(
            input_path,
            "r"
        ) as file:

            data = json.load(file)

        self.memory = data["memories"]

        return self.memory

    # -------------------------------------------------
    # GET ALL MEMORY
    # -------------------------------------------------

    def get_all(self):

        return self.memory
