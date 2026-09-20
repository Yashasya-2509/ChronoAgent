from app.video_processing.frame_processor import FrameProcessor
from app.video_processing.keyframe_selector import KeyframeSelector
from app.video_processing.manifest_manager import ManifestManager


VIDEO_PATH = "data/videos/test_video.mp4"

VIDEO_ID = "VID_TEST001"

FRAME_OUTPUT = "data/frames"

MANIFEST_OUTPUT = "data/manifests"


def main():

    print("\n========== PHASE A FRAME PROCESSING ==========\n")

    # =====================================================
    # 1. CREATE FRAME PROCESSOR
    # =====================================================

    processor = FrameProcessor(
        sample_fps=2.0,
        scene_threshold=27.0,
        min_scene_len=15
    )

    # =====================================================
    # 2. EXTRACT FRAMES
    # =====================================================

    frames = processor.extract_frames(
        VIDEO_PATH,
        FRAME_OUTPUT,
        VIDEO_ID
    )

    print(
        f"Extracted Frames: {len(frames)}"
    )

    # =====================================================
    # 3. DETECT SCENES
    # =====================================================

    scenes = processor.detect_scenes(
        VIDEO_PATH
    )

    print(
        f"Detected Scenes: {len(scenes)}"
    )

    # Add video_id to every scene
    for scene in scenes:
        scene["video_id"] = VIDEO_ID

    # =====================================================
    # 4. SELECT KEYFRAMES
    # =====================================================

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

    # =====================================================
    # 5. SAVE MANIFESTS
    # =====================================================

    manager = ManifestManager(
        MANIFEST_OUTPUT
    )

    frame_manifest = manager.save_frames(
        VIDEO_ID,
        frames
    )

    scene_manifest = manager.save_scenes(
        VIDEO_ID,
        scenes
    )

    keyframe_manifest = manager.save_keyframes(
        VIDEO_ID,
        keyframes
    )

    # =====================================================
    # 6. RESULTS
    # =====================================================

    print("\n========== MANIFEST FILES ==========")

    print(
        f"Frame Manifest: {frame_manifest}"
    )

    print(
        f"Scene Manifest: {scene_manifest}"
    )

    print(
        f"Keyframe Manifest: {keyframe_manifest}"
    )

    print(
        "\nPhase A frame processing successful!"
    )


if __name__ == "__main__":
    main()