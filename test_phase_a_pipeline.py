from pathlib import Path

from app.video_processing.video_ingestion import VideoIngestion
from app.video_processing.frame_processor import FrameProcessor
from app.video_processing.keyframe_selector import KeyframeSelector
from app.video_processing.manifest_manager import ManifestManager
from app.database.chrono_database import ChronoDatabase

from app.config import (
    FRAME_FOLDER,
    MANIFEST_FOLDER,
)


# =========================================================
# CHANGE ONLY THIS PATH FOR NEW VIDEOS
# =========================================================
VIDEO_PATH = "data/videos/converted/crosswalk.mp4"



def main():

    print("\n")
    print("=" * 60)
    print("        CHRONOAGENT - PHASE A PIPELINE")
    print("=" * 60)


    # =====================================================
    # STEP 1 : VIDEO INGESTION
    # =====================================================

    print("\n[1] VIDEO INGESTION")


    ingestion = VideoIngestion()


    # Dynamic ingestion
    metadata = ingestion.ingest(
        VIDEO_PATH
    )


    VIDEO_ID = metadata["video_id"]


    print(
        f"Video ID: {VIDEO_ID}"
    )

    print(
        f"Duration: {metadata['duration']:.2f}s"
    )

    print(
        f"FPS: {metadata['fps']:.2f}"
    )

    print(
        f"Resolution: {metadata['resolution']}"
    )



    # =====================================================
    # STEP 2 : FRAME PROCESSING
    # =====================================================

    print("\n[2] FRAME PROCESSING")


    processor = FrameProcessor(
        sample_fps=2.0,
        scene_threshold=27.0,
        min_scene_len=15
    )


    frame_output_dir = (
        FRAME_FOLDER / VIDEO_ID
    )


    frames = processor.extract_frames(
        metadata["path"],
        frame_output_dir,
        VIDEO_ID
    )


    print(
        f"Extracted Frames: {len(frames)}"
    )



    # =====================================================
    # STEP 3 : SCENE DETECTION
    # =====================================================

    print("\n[3] SCENE DETECTION")


    scenes = processor.detect_scenes(
        metadata["path"]
    )


    print(
        f"Detected Scenes: {len(scenes)}"
    )


    for scene in scenes:

        scene["video_id"] = VIDEO_ID


        print(
            f"{scene['scene_id']} | "
            f"{scene['start_time']:.2f}s - "
            f"{scene['end_time']:.2f}s"
        )



    # =====================================================
    # STEP 4 : KEYFRAME SELECTION
    # =====================================================

    print("\n[4] KEYFRAME SELECTION")


    selector = KeyframeSelector(
        max_keyframes_per_scene=3
    )


    keyframes = selector.select_keyframes(
        frames,
        scenes
    )


    print(
        f"Selected Keyframes: {len(keyframes)}"
    )


    for frame in keyframes:

        print(
            f"{frame['frame_id']} | "
            f"{frame['timestamp']:.2f}s | "
            f"{frame['scene_id']}"
        )



    # =====================================================
    # STEP 5 : MANIFEST CREATION
    # =====================================================

    print("\n[5] MANIFEST CREATION")


    manifest_manager = ManifestManager(
        MANIFEST_FOLDER
    )


    frame_manifest = (
        manifest_manager.save_frames(
            VIDEO_ID,
            frames
        )
    )


    scene_manifest = (
        manifest_manager.save_scenes(
            VIDEO_ID,
            scenes
        )
    )


    keyframe_manifest = (
        manifest_manager.save_keyframes(
            VIDEO_ID,
            keyframes
        )
    )


    print(
        f"Frame Manifest: {frame_manifest}"
    )

    print(
        f"Scene Manifest: {scene_manifest}"
    )

    print(
        f"Keyframe Manifest: {keyframe_manifest}"
    )



    # =====================================================
    # STEP 6 : DATABASE STORAGE
    # =====================================================

    print("\n[6] DATABASE STORAGE")


    db = ChronoDatabase()


    metadata["camera_id"] = "CAM_DYNAMIC"


    db.insert_video(
        metadata
    )


    for scene in scenes:

        db.insert_scene(
            scene
        )


    for frame in frames:

        db.insert_frame(
            frame
        )


    print("Video stored.")

    print(
        f"Scenes stored: {len(scenes)}"
    )

    print(
        f"Frames stored: {len(frames)}"
    )

    print(
        f"Keyframes stored: {len(keyframes)}"
    )



    # =====================================================
    # STEP 7 : DATABASE VERIFICATION
    # =====================================================

    print("\n[7] DATABASE VERIFICATION")


    statistics = db.get_statistics(
        VIDEO_ID
    )


    print(
        f"Database statistics: {statistics}"
    )


    db.close()



    # =====================================================
    # FINAL
    # =====================================================


    print("\n")
    print("=" * 60)
    print("        PHASE A PIPELINE SUCCESSFUL")
    print("=" * 60)


    print(
        """
ChronoAgent Phase A completed:

✓ Dynamic video ingestion
✓ Automatic Video ID generation
✓ Video metadata extraction
✓ Frame extraction
✓ Scene detection
✓ Keyframe selection
✓ Manifest generation
✓ SQLite storage
✓ Database verification
"""
    )



if __name__ == "__main__":
    main()