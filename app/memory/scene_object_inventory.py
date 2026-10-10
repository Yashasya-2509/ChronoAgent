import json
from pathlib import Path


class SceneObjectInventory:

    """
    Builds a compact scene-level inventory from
    ObjectTracker output.

    The inventory represents unique tracked entities,
    not individual frame detections.
    """

    def __init__(self):

        print("[SCENE INVENTORY] Initialized")

    # =========================================================
    # NORMALIZE CLASS NAME
    # =========================================================

    @staticmethod
    def normalize_class_name(class_name):

        if not class_name:
            return "UNKNOWN"

        name = (
            str(class_name)
            .strip()
            .lower()
            .replace("_", " ")
        )

        mapping = {
            "person": "PERSON",
            "human": "PERSON",
            "backpack": "BACKPACK",
            "handbag": "HANDBAG",
            "suitcase": "SUITCASE",
            "laptop": "LAPTOP",
            "cell phone": "CELL_PHONE",
            "cellphone": "CELL_PHONE",
            "phone": "CELL_PHONE",
            "chair": "CHAIR",
            "car": "CAR",
            "truck": "TRUCK",
            "bus": "BUS",
            "bicycle": "BICYCLE",
            "motorcycle": "MOTORCYCLE",
            "dog": "DOG",
            "cat": "CAT"
        }

        return mapping.get(
            name,
            name.upper().replace(" ", "_")
        )

    # =========================================================
    # LOAD TRACK DATA
    # =========================================================

    @staticmethod
    def load_tracks(track_path):

        track_path = Path(track_path)

        if not track_path.exists():

            raise FileNotFoundError(
                f"Track file not found: {track_path}"
            )

        with open(
            track_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return data

    # =========================================================
    # BUILD OBJECT RECORD
    # =========================================================

    def build_object_record(self, obj):

        object_id = obj.get(
            "object_id",
            "UNKNOWN"
        )

        class_name = self.normalize_class_name(
            obj.get("object")
        )

        first_seen = float(
            obj.get("first_seen", 0.0)
        )

        last_seen = float(
            obj.get("last_seen", first_seen)
        )

        duration = max(
            0.0,
            last_seen - first_seen
        )

        return {
            "object_id": object_id,

            "track_id": obj.get(
                "track_id"
            ),

            "class_name": class_name,

            "original_class": obj.get(
                "object"
            ),

            "object_type": obj.get(
                "object_type",
                "object"
            ),

            "first_seen": first_seen,

            "first_frame": obj.get(
                "first_frame"
            ),

            "last_seen": last_seen,

            "last_frame": obj.get(
                "last_frame"
            ),

            "duration": duration,

            "observation_count": obj.get(
                "observations",
                0
            ),

            # These fields are intentionally empty
            # until verified event evidence exists.
            "owner_id": None,

            "interactions": [],

            "evidence_frames": []
        }

    # =========================================================
    # BUILD INVENTORY
    # =========================================================

    def build_inventory(self, track_data):

        video_id = track_data.get(
            "video_id"
        )

        unique_objects = track_data.get(
            "unique_objects",
            []
        )

        inventory = {
            "video_id": video_id,

            "total_objects": len(
                unique_objects
            ),

            "objects": [],

            "by_class": {}
        }

        # -----------------------------------------------------
        # Convert every tracked entity
        # -----------------------------------------------------

        for obj in unique_objects:

            record = self.build_object_record(
                obj
            )

            inventory["objects"].append(
                record
            )

        # -----------------------------------------------------
        # Group objects by class
        # -----------------------------------------------------

        for obj in inventory["objects"]:

            class_name = obj["class_name"]

            if class_name not in inventory["by_class"]:

                inventory["by_class"][class_name] = []

            inventory["by_class"][class_name].append(
                obj["object_id"]
            )

        # -----------------------------------------------------
        # Sort objects
        # -----------------------------------------------------

        inventory["objects"].sort(
            key=lambda obj: (
                obj["class_name"],
                obj["object_id"]
            )
        )

        return inventory

    # =========================================================
    # BUILD FROM FILE
    # =========================================================

    def build_from_file(
        self,
        track_path,
        output_path=None
    ):

        print(
            f"[SCENE INVENTORY] Loading: "
            f"{track_path}"
        )

        track_data = self.load_tracks(
            track_path
        )

        inventory = self.build_inventory(
            track_data
        )

        if output_path:

            output_path = Path(
                output_path
            )

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            with open(
                output_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    inventory,
                    file,
                    indent=2
                )

            print(
                f"[SCENE INVENTORY] Saved: "
                f"{output_path}"
            )

        return inventory

    # =========================================================
    # PRINT INVENTORY
    # =========================================================

    @staticmethod
    def print_inventory(inventory):

        print()
        print("=" * 70)
        print("SCENE OBJECT INVENTORY")
        print("=" * 70)

        print(
            f"VIDEO ID       : "
            f"{inventory.get('video_id')}"
        )

        print(
            f"TOTAL OBJECTS  : "
            f"{inventory.get('total_objects')}"
        )

        print()

        for class_name in sorted(
            inventory.get("by_class", {})
        ):

            print(class_name)

            object_ids = inventory[
                "by_class"
            ][class_name]

            for object_id in object_ids:

                obj = next(
                    item
                    for item in inventory["objects"]
                    if item["object_id"] == object_id
                )

                print(
                    f"  ├── {object_id}"
                )

                print(
                    f"  │   First seen : "
                    f"{obj['first_seen']:.2f}s"
                )

                print(
                    f"  │   Last seen  : "
                    f"{obj['last_seen']:.2f}s"
                )

                print(
                    f"  │   Duration   : "
                    f"{obj['duration']:.2f}s"
                )

                print(
                    f"  │   Observations: "
                    f"{obj['observation_count']}"
                )

            print()

        print("=" * 70)