from pathlib import Path
import json


class ManifestManager:

    def __init__(self, output_dir):

        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    # =========================================================
    # SAVE FRAME MANIFEST
    # =========================================================

    def save_frames(
        self,
        video_id,
        frames
    ):

        output_file = (
            self.output_dir
            / f"{video_id}_frames.json"
        )

        data = {
            "video_id": video_id,
            "frame_count": len(frames),
            "frames": frames
        }

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=2
            )

        return output_file

    # =========================================================
    # SAVE SCENE MANIFEST
    # =========================================================

    def save_scenes(
        self,
        video_id,
        scenes
    ):

        output_file = (
            self.output_dir
            / f"{video_id}_scenes.json"
        )

        data = {
            "video_id": video_id,
            "scene_count": len(scenes),
            "scenes": scenes
        }

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=2
            )

        return output_file

    # =========================================================
    # SAVE KEYFRAME MANIFEST
    # =========================================================

    def save_keyframes(
        self,
        video_id,
        keyframes
    ):

        output_file = (
            self.output_dir
            / f"{video_id}_keyframes.json"
        )

        data = {
            "video_id": video_id,
            "keyframe_count": len(keyframes),
            "keyframes": keyframes
        }

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=2
            )

        return output_file