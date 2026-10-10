
from pathlib import Path
from datetime import datetime
import hashlib
import shutil

import cv2

from app.video_processing.video_metadata import VideoMetadata


class VideoIngestion:

    # Supported CCTV video formats
    SUPPORTED_EXTENSIONS = {
        ".mp4",
        ".avi",
        ".mov"
    }

    def __init__(self, video_dir="data/videos"):

        self.video_dir = Path(video_dir)

        self.video_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    # =========================================================
    # FORMAT VALIDATION
    # =========================================================

    def validate_format(self, video_path):

        video_path = Path(video_path)

        if not video_path.exists():
            raise FileNotFoundError(
                f"Video not found: {video_path}"
            )

        if not video_path.is_file():
            raise ValueError(
                f"Path is not a file: {video_path}"
            )

        extension = video_path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported video format: {extension}. "
                f"Supported formats: "
                f"{sorted(self.SUPPORTED_EXTENSIONS)}"
            )

        return True

    # =========================================================
    # VIDEO ID GENERATION
    # =========================================================

    def generate_video_id(self, video_path):

        video_path = Path(video_path)

        hasher = hashlib.sha256()

        with open(video_path, "rb") as video_file:

            while True:

                chunk = video_file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                hasher.update(chunk)

        # First 8 characters are sufficient for the prototype
        return f"VID_{hasher.hexdigest()[:8]}"

    # =========================================================
    # VIDEO METADATA EXTRACTION
    # =========================================================

    def extract_metadata(
        self,
        video_path,
        video_id=None,
        original_filename=None,
        camera_id=None
    ):

        video_path = Path(video_path)

        self.validate_format(
            video_path
        )

        # Generate ID if one was not supplied
        if video_id is None:

            video_id = self.generate_video_id(
                video_path
            )

        # -----------------------------------------------------
        # Open video
        # -----------------------------------------------------

        capture = cv2.VideoCapture(
            str(video_path)
        )

        if not capture.isOpened():

            raise RuntimeError(
                f"Could not open video: {video_path}"
            )

        # -----------------------------------------------------
        # Extract video properties
        # -----------------------------------------------------

        fps = capture.get(
            cv2.CAP_PROP_FPS
        )

        frame_count = int(
            capture.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        width = int(
            capture.get(
                cv2.CAP_PROP_FRAME_WIDTH
            )
        )

        height = int(
            capture.get(
                cv2.CAP_PROP_FRAME_HEIGHT
            )
        )

        capture.release()

        # -----------------------------------------------------
        # Validate extracted properties
        # -----------------------------------------------------

        if fps <= 0:

            raise ValueError(
                f"Invalid FPS detected for: {video_path}"
            )

        if frame_count <= 0:

            raise ValueError(
                f"Invalid frame count detected for: "
                f"{video_path}"
            )

        if width <= 0 or height <= 0:

            raise ValueError(
                f"Invalid video resolution detected for: "
                f"{video_path}"
            )

        # -----------------------------------------------------
        # Calculate duration
        # -----------------------------------------------------

        duration = frame_count / fps

        # -----------------------------------------------------
        # Preserve original filename
        # -----------------------------------------------------

        if original_filename is None:

            original_filename = video_path.name

        # -----------------------------------------------------
        # Create metadata object
        # -----------------------------------------------------

        metadata = VideoMetadata(

            video_id=video_id,

            filename=original_filename,

            format=(
                video_path.suffix
                .lower()
                .replace(".", "")
            ),

            fps=fps,

            frame_count=frame_count,

            duration=duration,

            width=width,

            height=height,

            camera_id=camera_id,

            created_at=datetime.now()
                .isoformat()
        )

        return metadata

    # =========================================================
    # VIDEO INGESTION
    # =========================================================

    def ingest(
        self,
        video_path,
        camera_id=None
    ):

        video_path = Path(video_path)

        print("=" * 60)
        print("VIDEO INGESTION")
        print("=" * 60)

        # -----------------------------------------------------
        # Step 1: Validate input
        # -----------------------------------------------------

        self.validate_format(
            video_path
        )

        # -----------------------------------------------------
        # Step 2: Preserve original filename
        # -----------------------------------------------------

        original_filename = video_path.name

        print(
            f"[VIDEO] Input: {original_filename}"
        )

        # -----------------------------------------------------
        # Step 3: Generate deterministic Video ID
        # -----------------------------------------------------

        video_id = self.generate_video_id(
            video_path
        )

        print(
            f"[VIDEO] ID: {video_id}"
        )

        # -----------------------------------------------------
        # Step 4: Determine canonical storage path
        # -----------------------------------------------------

        extension = (
            video_path.suffix.lower()
        )

        destination = (
            self.video_dir /
            f"{video_id}{extension}"
        )

        # -----------------------------------------------------
        # Step 5: Store one canonical copy
        # -----------------------------------------------------

        if video_path.resolve() == destination.resolve():

            print(
                "[VIDEO] Source is already "
                "the canonical stored video."
            )

        elif destination.exists():

            print(
                f"[VIDEO] Canonical video already exists: "
                f"{destination}"
            )

        else:

            shutil.copy2(
                video_path,
                destination
            )

            print(
                f"[VIDEO] Stored: {destination}"
            )

        # -----------------------------------------------------
        # Step 6: Verify canonical video
        # -----------------------------------------------------

        if not destination.exists():

            raise RuntimeError(
                f"Canonical video was not created: "
                f"{destination}"
            )

        # -----------------------------------------------------
        # Step 7: Extract metadata
        #
        # IMPORTANT:
        # Read the canonical video but preserve the
        # original uploaded filename.
        # -----------------------------------------------------

        metadata = self.extract_metadata(

            video_path=destination,

            video_id=video_id,

            original_filename=original_filename,

            camera_id=camera_id
        )

        # -----------------------------------------------------
        # Step 8: Display metadata
        # -----------------------------------------------------

        print(
            f"[VIDEO] FPS: "
            f"{metadata.fps:.2f}"
        )

        print(
            f"[VIDEO] Frames: "
            f"{metadata.frame_count}"
        )

        print(
            f"[VIDEO] Duration: "
            f"{metadata.duration:.2f}s"
        )

        print(
            f"[VIDEO] Resolution: "
            f"{metadata.resolution}"
        )

        print(
            f"[VIDEO] Format: "
            f"{metadata.format}"
        )

        print(
            f"[VIDEO] Original filename: "
            f"{metadata.filename}"
        )

        print(
            f"[VIDEO] Camera ID: "
            f"{metadata.camera_id}"
        )

        print(
            f"[VIDEO] Stored path: "
            f"{destination}"
        )

        print(
            "=" * 60
        )

        return metadata

