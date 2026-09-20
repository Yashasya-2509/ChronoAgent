from app.video_processing.keyframe_selector import KeyframeSelector


def main():

    video_id = "VID_TEST001"

    # Simulated sampled frames
    frames = []

    for i in range(60):

        frames.append({
            "frame_id": f"F{i + 1:05d}",
            "video_id": video_id,
            "frame_number": i * 15,
            "timestamp": i * 0.5,
            "path": (
                f"data/frames/{video_id}/"
                f"F{i + 1:05d}.jpg"
            ),
            "is_keyframe": False
        })

    # Simulated scene
    scenes = [
        {
            "scene_id": "S0001",
            "video_id": video_id,
            "start_frame": 0,
            "end_frame": 900,
            "start_time": 0.0,
            "end_time": 30.0
        }
    ]

    # Create selector
    selector = KeyframeSelector(
        max_keyframes_per_scene=3
    )

    # Select keyframes
    keyframes = selector.select_keyframes(
        frames,
        scenes
    )

    print("\n========== KEYFRAME RESULTS ==========")

    print(
        f"Total frames: {len(frames)}"
    )

    print(
        f"Selected keyframes: {len(keyframes)}"
    )

    print("\nSelected keyframes:")

    for frame in keyframes:

        print(
            f"{frame['frame_id']} | "
            f"{frame['timestamp']:.2f}s | "
            f"{frame['scene_id']} | "
            f"Keyframe: {frame['is_keyframe']}"
        )

    print(
        "\nKeyframe selection successful!"
    )


if __name__ == "__main__":
    main()