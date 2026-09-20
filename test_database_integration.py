from app.database.chrono_database import ChronoDatabase


def main():

    video_id = "VID_TEST001"

    # =====================================================
    # SAMPLE VIDEO
    # =====================================================

    video = {
        "video_id": video_id,
        "filename": "test_video.mp4",
        "camera_id": "CAM_TEST001",
        "fps": 30.0,
        "duration": 30.0,
        "width": 768,
        "height": 432,
        "created_at": "2026-09-16T00:00:00"
    }

    # =====================================================
    # SAMPLE SCENE
    # =====================================================

    scene = {
        "scene_id": "S0001",
        "video_id": video_id,
        "start_frame": 0,
        "end_frame": 900,
        "start_time": 0.0,
        "end_time": 30.0
    }

    # =====================================================
    # SAMPLE FRAMES
    # =====================================================

    frames = [

        {
            "frame_id": "F00001",
            "video_id": video_id,
            "scene_id": "S0001",
            "frame_number": 0,
            "timestamp": 0.0,
            "path": "data/frames/VID_TEST001/F00001.jpg",
            "is_keyframe": True
        },

        {
            "frame_id": "F00031",
            "video_id": video_id,
            "scene_id": "S0001",
            "frame_number": 450,
            "timestamp": 15.0,
            "path": "data/frames/VID_TEST001/F00031.jpg",
            "is_keyframe": True
        },

        {
            "frame_id": "F00060",
            "video_id": video_id,
            "scene_id": "S0001",
            "frame_number": 885,
            "timestamp": 29.5,
            "path": "data/frames/VID_TEST001/F00060.jpg",
            "is_keyframe": True
        }
    ]

    # =====================================================
    # DATABASE
    # =====================================================

    db = ChronoDatabase()

    print("\n========== DATABASE INSERTION ==========\n")

    db.insert_video(video)

    print("VIDEO inserted.")

    db.insert_scene(scene)

    print("SCENE inserted.")

    for frame in frames:
        db.insert_frame(frame)

    print("FRAMES inserted.")

    # =====================================================
    # RETRIEVE
    # =====================================================

    stored_video = db.get_video(video_id)

    stored_scenes = db.get_scenes(video_id)

    stored_frames = db.get_frames(video_id)

    stored_keyframes = db.get_keyframes(video_id)

    statistics = db.get_statistics(video_id)

    # =====================================================
    # RESULTS
    # =====================================================

    print("\n========== DATABASE RESULTS ==========\n")

    print(
        "Video:",
        dict(stored_video)
    )

    print(
        "Scenes:",
        len(stored_scenes)
    )

    print(
        "Frames:",
        len(stored_frames)
    )

    print(
        "Keyframes:",
        len(stored_keyframes)
    )

    print(
        "\nStatistics:",
        statistics
    )

    db.close()

    print(
        "\nDatabase integration successful!"
    )


if __name__ == "__main__":
    main()