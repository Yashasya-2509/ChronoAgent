from pathlib import Path
import cv2


class FrameProcessor:

    def __init__(
        self,
        sample_fps=2.0,
        scene_threshold=27.0,
        min_scene_len=15
    ):

        self.sample_fps = sample_fps
        self.scene_threshold = scene_threshold
        self.min_scene_len = min_scene_len


    # =========================================================
    # FRAME EXTRACTION
    # =========================================================

    def extract_frames(
        self,
        video_path,
        output_dir,
        video_id
    ):

        video_path = Path(video_path)
        output_dir = Path(output_dir)

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )


        cap = cv2.VideoCapture(
            str(video_path)
        )


        if not cap.isOpened():

            raise ValueError(
                f"Could not open video: {video_path}"
            )


        fps = cap.get(
            cv2.CAP_PROP_FPS
        )


        if fps <= 0:

            raise ValueError(
                "Invalid video FPS."
            )


        frame_interval = max(
            1,
            int(round(
                fps / self.sample_fps
            ))
        )


        frames = []

        frame_index = 0
        saved_index = 0


        while True:


            ret, frame = cap.read()


            if not ret:
                break



            if frame_index % frame_interval == 0:


                timestamp = (
                    frame_index / fps
                )


                frame_id = (
                    f"F{saved_index + 1:05d}"
                )


                frame_path = (
                    output_dir /
                    f"{frame_id}.jpg"
                )



                success = cv2.imwrite(
                    str(frame_path),
                    frame
                )


                if success:


                    frames.append({

                        "frame_id":
                            frame_id,


                        "video_id":
                            video_id,


                        "frame_number":
                            frame_index,


                        "timestamp":
                            timestamp,


                        # CHANGED KEY
                        "frame_path":
                            str(frame_path),


                        "is_keyframe":
                            False

                    })


                    saved_index += 1



            frame_index += 1



        cap.release()


        print(
            f"Frames extracted: {len(frames)}"
        )


        return frames



    # =========================================================
    # SCENE DETECTION
    # =========================================================

    def detect_scenes(
        self,
        video_path
    ):


        video_path = Path(video_path)


        if not video_path.exists():

            raise FileNotFoundError(
                f"Video not found: {video_path}"
            )


        cap = cv2.VideoCapture(
            str(video_path)
        )


        if not cap.isOpened():

            raise RuntimeError(
                f"Could not open video: {video_path}"
            )



        fps = cap.get(
            cv2.CAP_PROP_FPS
        )


        frame_count = int(
            cap.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )


        duration = (
            frame_count / fps
        )



        print(
            f"Video FPS: {fps}"
        )

        print(
            f"Video frames: {frame_count}"
        )

        print(
            f"Video duration: {duration:.2f}s"
        )



        scenes = []

        scene_start = 0

        previous_gray = None

        last_scene_boundary = 0

        frame_index = 0



        while True:


            success, frame = cap.read()


            if not success:
                break



            small_frame = cv2.resize(
                frame,
                (320,180)
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
                    score >= self.scene_threshold
                    and
                    frames_since_boundary >= self.min_scene_len
                ):


                    scenes.append({

                        "scene_id":
                            f"S{len(scenes)+1:04d}",


                        "start_frame":
                            scene_start,


                        "end_frame":
                            frame_index,


                        "start_time":
                            scene_start / fps,


                        "end_time":
                            frame_index / fps

                    })


                    scene_start = frame_index

                    last_scene_boundary = frame_index



            previous_gray = gray

            frame_index += 1



        cap.release()



        if scene_start < frame_index:


            scenes.append({

                "scene_id":
                    f"S{len(scenes)+1:04d}",


                "start_frame":
                    scene_start,


                "end_frame":
                    frame_index,


                "start_time":
                    scene_start / fps,


                "end_time":
                    frame_index / fps

            })



        print(
            f"\nDetected {len(scenes)} scene(s)."
        )


        return scenes