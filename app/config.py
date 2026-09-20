from pathlib import Path
import os

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ============================================================
# DATA DIRECTORIES
# ============================================================

DATA_DIR = PROJECT_ROOT / "data"

UPLOAD_FOLDER = DATA_DIR / "uploaded_videos"
VIDEO_FOLDER = DATA_DIR / "videos"
METADATA_FOLDER = DATA_DIR / "metadata"
FRAME_FOLDER = DATA_DIR / "frames"
SCENE_FOLDER = DATA_DIR / "scenes"
MANIFEST_FOLDER = DATA_DIR / "manifests"
DATABASE_FOLDER = DATA_DIR / "database"

DATABASE_PATH = DATABASE_FOLDER / "chrono.db"

# ============================================================
# VIDEO PROCESSING SETTINGS
# ============================================================

VIDEO_SAMPLE_FPS = float(
    os.getenv("VIDEO_SAMPLE_FPS", "2.0")
)

SCENE_THRESHOLD = float(
    os.getenv("SCENE_THRESHOLD", "27.0")
)

MIN_SCENE_LENGTH = int(
    os.getenv("MIN_SCENE_LENGTH", "15")
)

# ============================================================
# SUPPORTED VIDEO FORMATS
# ============================================================

SUPPORTED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".webm",
}

# ============================================================
# CREATE REQUIRED DIRECTORIES
# ============================================================

for directory in [
    UPLOAD_FOLDER,
    VIDEO_FOLDER,
    METADATA_FOLDER,
    FRAME_FOLDER,
    SCENE_FOLDER,
    MANIFEST_FOLDER,
    DATABASE_FOLDER,
]:
    directory.mkdir(parents=True, exist_ok=True)