from pathlib import Path

from app.database.chrono_database import ChronoDatabase
from app.video_processing.frame_processor import FrameProcessor


VIDEO_ID = "VID_0a2a093d"

VIDEO_PATH = Path(
    "data/videos/VID_0a2a093d.mov"
)

FRAME_OUTPUT_DIR = Path(
    "data/frames/VID_0a2a093d"
)


def main():

    print()
    print("=" * 60)
    print("SCENE + FRAME DATABASE TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. CHECK VIDEO
    # ---------------------------------------------------------

    if not VIDEO_PATH.exists():

        raise FileNotFoundError(
            f"Video not found: {VIDEO_PATH}"
        )

    # ---------------------------------------------------------
    # 2. DEFINE DETECTED SCENES
    # ---------------------------------------------------------

    scenes = [
        {
            "scene_id": "S0001",
            "video_id": VIDEO_ID,
            "start_frame": 0,
            "end_frame": 1781,
            "start_time": 0.0,
            "end_time": 71.24
        }
    ]

    # ---------------------------------------------------------
    # 3. EXTRACT CONTROLLED FRAMES
    # ---------------------------------------------------------

    processor = FrameProcessor(
        sample_fps=2.0,
        max_frames_per_scene=40,
        max_total_frames=40
    )

    frames = processor.extract_frames(
        video_path=VIDEO_PATH,
        scenes=scenes,
        output_dir=FRAME_OUTPUT_DIR
    )

    print()
    print(
        f"[FRAME] Extracted {len(frames)} frames."
    )

    # ---------------------------------------------------------
    # 4. OPEN DATABASE
    # ---------------------------------------------------------

    database = ChronoDatabase()

    try:

        # -----------------------------------------------------
        # 5. INSERT SCENE
        # -----------------------------------------------------

        for scene in scenes:

            database.insert_scene(
                scene
            )

        print(
            "[DATABASE] Scene inserted successfully."
        )

        # -----------------------------------------------------
        # 6. INSERT FRAMES
        # -----------------------------------------------------

        for index, frame in enumerate(frames):

            frame_record = {

                "frame_id":
                (
                    f"{VIDEO_ID}_"
                    f"{frame['frame_number']:06d}"
                ),

                "video_id":
                VIDEO_ID,

                "scene_id":
                frame["scene_id"],

                "frame_number":
                frame["frame_number"],

                "timestamp":
                frame["timestamp"],

                "path":
                frame["path"],

                "is_keyframe":
                1
            }

            database.insert_frame(
                frame_record
            )

        print(
            "[DATABASE] Frames inserted successfully."
        )

        # -----------------------------------------------------
        # 7. READ SCENES
        # -----------------------------------------------------

        stored_scenes = database.get_scenes(
            VIDEO_ID
        )

        print()
        print("=" * 60)
        print("STORED SCENES")
        print("=" * 60)

        for scene in stored_scenes:

            print(
                f"{scene['scene_id']} | "
                f"{scene['start_time']:.2f}s - "
                f"{scene['end_time']:.2f}s | "
                f"frames "
                f"{scene['start_frame']}-"
                f"{scene['end_frame']}"
            )

        # -----------------------------------------------------
        # 8. READ KEYFRAMES
        # -----------------------------------------------------

        stored_frames = database.get_keyframes(
            VIDEO_ID
        )

        print()
        print("=" * 60)
        print("STORED KEYFRAMES")
        print("=" * 60)

        print(
            f"Total stored keyframes: "
            f"{len(stored_frames)}"
        )

        print()
        print("First 5:")

        for frame in stored_frames[:5]:

            print(
                f"{frame['frame_id']} | "
                f"{frame['timestamp']:.3f}s | "
                f"{frame['path']}"
            )

        print()
        print("Last 5:")

        for frame in stored_frames[-5:]:

            print(
                f"{frame['frame_id']} | "
                f"{frame['timestamp']:.3f}s | "
                f"{frame['path']}"
            )

        # -----------------------------------------------------
        # 9. DATABASE STATISTICS
        # -----------------------------------------------------

        statistics = database.get_statistics(
            VIDEO_ID
        )

        print()
        print("=" * 60)
        print("DATABASE STATISTICS")
        print("=" * 60)

        print(
            f"Scenes       : "
            f"{statistics['scene_count']}"
        )

        print(
            f"Frames       : "
            f"{statistics['frame_count']}"
        )

        print(
            f"Keyframes    : "
            f"{statistics['keyframe_count']}"
        )

    finally:

        database.close()

    # ---------------------------------------------------------
    # 10. SUCCESS
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("SCENE + FRAME DATABASE TEST SUCCESSFUL")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()