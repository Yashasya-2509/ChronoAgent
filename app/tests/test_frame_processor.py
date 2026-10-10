from pathlib import Path

from app.video_processing.frame_processor import FrameProcessor


VIDEO_PATH = Path(
    "data/videos/VID_0a2a093d.mov"
)

OUTPUT_DIR = Path(
    "data/frames/VID_0a2a093d"
)


def main():

    print()
    print("=" * 60)
    print("FRAME PROCESSOR TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # CHECK VIDEO
    # ---------------------------------------------------------

    if not VIDEO_PATH.exists():

        raise FileNotFoundError(
            f"Video not found: {VIDEO_PATH}"
        )

    # ---------------------------------------------------------
    # SCENE INFORMATION
    # ---------------------------------------------------------
    #
    # Your current scene detector found:
    #
    # S0001 = frames 0-1781
    #
    # We provide that scene directly for this test.
    # ---------------------------------------------------------

    scenes = [
        {
            "scene_id": "S0001",
            "video_id": "VID_0a2a093d",
            "start_frame": 0,
            "end_frame": 1781,
            "start_time": 0.0,
            "end_time": 71.24
        }
    ]

    # ---------------------------------------------------------
    # FRAME PROCESSOR
    # ---------------------------------------------------------

    processor = FrameProcessor(
        sample_fps=2.0,
        max_frames_per_scene=40,
        max_total_frames=40
    )

    # ---------------------------------------------------------
    # EXTRACT CONTROLLED FRAMES
    # ---------------------------------------------------------

    frames = processor.extract_frames(
        video_path=VIDEO_PATH,
        scenes=scenes,
        output_dir=OUTPUT_DIR
    )

    # ---------------------------------------------------------
    # RESULTS
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("FRAME EXTRACTION RESULTS")
    print("=" * 60)

    print(
        f"Total frames extracted : {len(frames)}"
    )

    print(
        f"Output directory       : {OUTPUT_DIR}"
    )

    if frames:

        print()
        print("First 5 frames:")

        for frame in frames[:5]:

            print(
                f"Frame {frame['frame_number']:4d} "
                f"| "
                f"{frame['timestamp']:7.3f}s "
                f"| "
                f"{frame['path']}"
            )

        print()
        print("Last 5 frames:")

        for frame in frames[-5:]:

            print(
                f"Frame {frame['frame_number']:4d} "
                f"| "
                f"{frame['timestamp']:7.3f}s "
                f"| "
                f"{frame['path']}"
            )

    print()
    print("=" * 60)
    print("FRAME PROCESSOR TEST SUCCESSFUL")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()