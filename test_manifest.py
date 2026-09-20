from app.video_processing.manifest_manager import ManifestManager
from app.config import MANIFEST_FOLDER


def main():

    manager = ManifestManager(
        MANIFEST_FOLDER
    )

    video_id = "VID_TEST001"

    frames = [
        {
            "frame_id": "F00001",
            "video_id": video_id,
            "frame_number": 0,
            "timestamp": 0.0,
            "path": "data/frames/VID_TEST001/F00001.jpg",
            "is_keyframe": False
        },
        {
            "frame_id": "F00002",
            "video_id": video_id,
            "frame_number": 6,
            "timestamp": 0.5,
            "path": "data/frames/VID_TEST001/F00002.jpg",
            "is_keyframe": False
        }
    ]

    scenes = [
        {
            "scene_id": "S0001",
            "video_id": video_id,
            "start_frame": 0,
            "end_frame": 60,
            "start_time": 0.0,
            "end_time": 5.0
        }
    ]

    keyframes = [
        {
            "frame_id": "F00002",
            "video_id": video_id,
            "scene_id": "S0001",
            "frame_number": 6,
            "timestamp": 0.5,
            "path": "data/frames/VID_TEST001/F00002.jpg",
            "is_keyframe": True
        }
    ]

    frame_file = manager.save_frames(
        video_id,
        frames
    )

    scene_file = manager.save_scenes(
        video_id,
        scenes
    )

    keyframe_file = manager.save_keyframes(
        video_id,
        keyframes
    )

    print("Frame manifest:", frame_file)
    print("Scene manifest:", scene_file)
    print("Keyframe manifest:", keyframe_file)

    print("\nManifest system working successfully!")


if __name__ == "__main__":
    main()