import cv2
from pathlib import Path


class FrameProcessor:

    def __init__(
        self,
        sample_fps=2.0,
        max_frames_per_scene=40,
        max_total_frames=120
    ):
        """
        Controlled temporal frame sampling.

        The processor samples frames across the complete duration
        of each scene instead of stopping at the beginning when
        a maximum frame limit is reached.
        """

        self.sample_fps = float(sample_fps)

        self.max_frames_per_scene = int(
            max_frames_per_scene
        )

        self.max_total_frames = int(
            max_total_frames
        )

    # ---------------------------------------------------------
    # EXTRACT FRAMES
    # ---------------------------------------------------------

    def extract_frames(
        self,
        video_path,
        scenes,
        output_dir,
        max_frames_per_scene=None,
        max_total_frames=None
    ):

        video_path = str(video_path)

        output_dir = Path(output_dir)

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        if max_frames_per_scene is None:
            max_frames_per_scene = (
                self.max_frames_per_scene
            )

        if max_total_frames is None:
            max_total_frames = (
                self.max_total_frames
            )

        if self.sample_fps <= 0:
            raise ValueError(
                "sample_fps must be greater than 0"
            )

        cap = cv2.VideoCapture(
            video_path
        )

        if not cap.isOpened():
            raise RuntimeError(
                f"Cannot open video: {video_path}"
            )

        fps = cap.get(
            cv2.CAP_PROP_FPS
        )

        if fps <= 0:
            raise RuntimeError(
                "Unable to determine video FPS."
            )

        total_video_frames = int(
            cap.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        duration = (
            total_video_frames / fps
        )

        print()
        print("=" * 60)
        print("FRAME PROCESSING")
        print("=" * 60)
        print(
            f"Video FPS          : {fps:.2f}"
        )
        print(
            f"Video Frames       : {total_video_frames}"
        )
        print(
            f"Video Duration     : {duration:.2f}s"
        )
        print(
            f"Sampling FPS       : {self.sample_fps:.2f}"
        )
        print(
            f"Max/Scene          : {max_frames_per_scene}"
        )
        print(
            f"Max Total          : {max_total_frames}"
        )

        extracted_frames = []

        total_saved = 0

        # -----------------------------------------------------
        # PROCESS EACH SCENE
        # -----------------------------------------------------

        for scene in scenes:

            if total_saved >= max_total_frames:
                break

            scene_id = scene.get(
                "scene_id"
            )

            start_frame = int(
                scene.get(
                    "start_frame",
                    0
                )
            )

            end_frame = int(
                scene.get(
                    "end_frame",
                    total_video_frames
                )
            )

            if end_frame <= start_frame:
                continue

            scene_frame_count = (
                end_frame - start_frame
            )

            # -------------------------------------------------
            # Determine number of samples
            # -------------------------------------------------

            duration_frames = (
                scene_frame_count / fps
            )

            desired_samples = int(
                duration_frames *
                self.sample_fps
            )

            desired_samples = max(
                1,
                desired_samples
            )

            desired_samples = min(
                desired_samples,
                max_frames_per_scene
            )

            remaining_global = (
                max_total_frames -
                total_saved
            )

            desired_samples = min(
                desired_samples,
                remaining_global
            )

            if desired_samples <= 0:
                break

            # -------------------------------------------------
            # Generate evenly distributed frame positions
            # -------------------------------------------------

            if desired_samples == 1:

                frame_positions = [
                    start_frame
                ]

            else:

                step = (
                    (scene_frame_count - 1)
                    /
                    (desired_samples - 1)
                )

                frame_positions = [
                    int(
                        round(
                            start_frame +
                            i * step
                        )
                    )
                    for i in range(
                        desired_samples
                    )
                ]

            print()
            print(
                f"[SCENE] {scene_id}"
            )

            print(
                f"        Frames: "
                f"{start_frame}-{end_frame}"
            )

            print(
                f"        Duration: "
                f"{duration_frames:.2f}s"
            )

            print(
                f"        Samples: "
                f"{len(frame_positions)}"
            )

            # -------------------------------------------------
            # Extract selected frames
            # -------------------------------------------------

            for frame_id in frame_positions:

                if total_saved >= max_total_frames:
                    break

                cap.set(
                    cv2.CAP_PROP_POS_FRAMES,
                    frame_id
                )

                ret, frame = cap.read()

                if not ret:
                    continue

                filename = (
                    f"frame_{total_saved:05d}.jpg"
                )

                frame_path = (
                    output_dir /
                    filename
                )

                success = cv2.imwrite(
                    str(frame_path),
                    frame
                )

                if not success:
                    continue

                timestamp = (
                    frame_id / fps
                )

                frame_info = {

                    "frame_path":
                    str(frame_path),

                    "path":
                    str(frame_path),

                    "frame_id":
                    frame_id,

                    "frame_number":
                    frame_id,

                    "timestamp":
                    round(
                        timestamp,
                        3
                    ),

                    "scene_id":
                    scene_id
                }

                extracted_frames.append(
                    frame_info
                )

                total_saved += 1

        cap.release()

        print()
        print(
            f"Candidate frames extracted : "
            f"{len(extracted_frames)}"
        )

        print(
            f"Maximum allowed            : "
            f"{max_total_frames}"
        )

        print("=" * 60)

        return extracted_frames