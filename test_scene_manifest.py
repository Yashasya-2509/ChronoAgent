from app.video_processing.scene_detector import SceneDetector
from app.video_processing.manifest_manager import ManifestManager


VIDEO_PATH = "data/videos/test_video.mp4"
VIDEO_ID = "VID_TEST001"
MANIFEST_DIR = "data/manifests"


print("=" * 60)
print("MINPRO SCENE DETECTION + MANIFEST TEST")
print("=" * 60)


# ---------------------------------------------------------
# 1. Detect scenes
# ---------------------------------------------------------

print("\n[1] Running scene detection...")

detector = SceneDetector()

scenes = detector.detect_scenes(VIDEO_PATH)

print(f"\nDetected scenes: {len(scenes)}")

for scene in scenes:
    print(
        f"{scene['scene_id']} | "
        f"frames {scene['start_frame']}-"
        f"{scene['end_frame']} | "
        f"{scene['start_time']:.2f}s - "
        f"{scene['end_time']:.2f}s"
    )


# ---------------------------------------------------------
# 2. Save scene manifest
# ---------------------------------------------------------

print("\n[2] Saving scene manifest...")

manager = ManifestManager(MANIFEST_DIR)

output_file = manager.save_scenes(
    VIDEO_ID,
    scenes
)

print(f"Scene manifest saved to:")
print(output_file)


# ---------------------------------------------------------
# 3. Verify file
# ---------------------------------------------------------

print("\n[3] Verifying manifest...")

if output_file.exists():

    print("SUCCESS: Scene manifest exists.")

else:

    print("ERROR: Scene manifest was not created.")


print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)