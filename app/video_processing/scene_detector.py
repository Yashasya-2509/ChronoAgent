"""
Minpro - Scene Detection Module

Robust scene detection using OpenCV frame analysis.

This implementation avoids PySceneDetect timestamp issues
by comparing consecutive frames directly.
"""

from pathlib import Path
from typing import List, Dict

import cv2


class SceneDetector:
    """Detect scenes in CCTV/video footage."""

    def __init__(
        self,
        threshold: float = 30.0,
        min_scene_length: int = 15
    ):
        self.threshold = threshold
        self.min_scene_length = min_scene_length

    def detect_scenes(self, video_path: str) -> List[Dict]:
        """Detect scenes using frame-to-frame visual differences."""

        video_path = Path(video_path)

        if not video_path.exists():
            raise FileNotFoundError(
                f"Video not found: {video_path}"
            )

        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise RuntimeError(
                f"Could not open video: {video_path}"
            )

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(
            cap.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        if fps <= 0:
            cap.release()
            raise RuntimeError(
                f"Invalid FPS: {fps}"
            )

        if frame_count <= 0:
            cap.release()
            raise RuntimeError(
                f"Invalid frame count: {frame_count}"
            )

        duration = frame_count / fps

        print(f"Video FPS: {fps}")
        print(f"Video frames: {frame_count}")
        print(f"Video duration: {duration:.2f}s")

        scenes = []

        scene_start = 0
        previous_gray = None
        last_scene_boundary = 0

        frame_index = 0

        while True:

            success, frame = cap.read()

            if not success:
                break

            # Resize frame for faster comparison.
            small_frame = cv2.resize(
                frame,
                (320, 180)
            )

            gray = cv2.cvtColor(
                small_frame,
                cv2.COLOR_BGR2GRAY
            )

            if previous_gray is not None:

                difference = cv2.absdiff(
                    previous_gray,
                    gray
                )

                score = float(
                    difference.mean()
                )

                frames_since_boundary = (
                    frame_index -
                    last_scene_boundary
                )

                if (
                    score >= self.threshold
                    and
                    frames_since_boundary >=
                    self.min_scene_length
                ):

                    scene_number = len(scenes) + 1

                    scenes.append(
                        self._create_scene(
                            scene_number,
                            scene_start,
                            frame_index,
                            fps
                        )
                    )

                    scene_start = frame_index
                    last_scene_boundary = frame_index

            previous_gray = gray
            frame_index += 1

        cap.release()

        # Add final scene.
        if scene_start < frame_index:

            scene_number = len(scenes) + 1

            scenes.append(
                self._create_scene(
                    scene_number,
                    scene_start,
                    frame_index,
                    fps
                )
            )

        print(
            f"\nDetected {len(scenes)} scene(s)."
        )

        return scenes

    def _create_scene(
        self,
        scene_number: int,
        start_frame: int,
        end_frame: int,
        fps: float
    ) -> Dict:

        return {
            "scene_id": f"S{scene_number:04d}",
            "start_frame": start_frame,
            "end_frame": end_frame,
            "start_time": start_frame / fps,
            "end_time": end_frame / fps,
        }


if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python "
            "app/video_processing/scene_detector.py "
            "<video_path>"
        )
        sys.exit(1)

    video_file = sys.argv[1]

    detector = SceneDetector()

    scenes = detector.detect_scenes(
        video_file
    )

    print("\nScene Results:\n")

    for scene in scenes:

        print(
            f"{scene['scene_id']} | "
            f"frames "
            f"{scene['start_frame']}-"
            f"{scene['end_frame']} | "
            f"{scene['start_time']:.2f}s - "
            f"{scene['end_time']:.2f}s"
        )