from pathlib import Path
import cv2
import json
import shutil
import uuid
from datetime import datetime

from app.config import (
    VIDEO_FOLDER,
    METADATA_FOLDER,
    SUPPORTED_VIDEO_EXTENSIONS,
)


class VideoIngestion:

    def __init__(self):
        VIDEO_FOLDER.mkdir(parents=True, exist_ok=True)
        METADATA_FOLDER.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # Generate unique video ID
    # ---------------------------------------------------------

    def generate_video_id(self):
        return f"VID_{uuid.uuid4().hex[:8]}"

    # ---------------------------------------------------------
    # Validate video
    # ---------------------------------------------------------

    def validate_video(self, video_path):

        video_path = Path(video_path)

        if not video_path.exists():
            raise FileNotFoundError(
                f"Video not found: {video_path}"
            )

        if video_path.suffix.lower() not in SUPPORTED_VIDEO_EXTENSIONS:
            raise ValueError(
                f"Unsupported video format: {video_path.suffix}"
            )

        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise ValueError(
                f"Could not open video: {video_path}"
            )

        cap.release()

        return True

    # ---------------------------------------------------------
    # Extract video metadata
    # ---------------------------------------------------------

    def extract_metadata(self, video_path, video_id):

        video_path = Path(video_path)

        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise ValueError(
                f"Could not open video: {video_path}"
            )

        fps = cap.get(cv2.CAP_PROP_FPS)

        frame_count = int(
            cap.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        width = int(
            cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        )

        height = int(
            cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

        cap.release()

        if fps <= 0:
            raise ValueError("Invalid video FPS.")

        duration = frame_count / fps

        metadata = {
            "video_id": video_id,
            "filename": video_path.name,
            "path": None,
            "fps": fps,
            "frame_count": frame_count,
            "duration": duration,
            "width": width,
            "height": height,
            "resolution": f"{width}x{height}",
            "created_at": datetime.now().isoformat(),
        }

        return metadata

    # ---------------------------------------------------------
    # Main ingestion function
    # ---------------------------------------------------------

    def ingest(self, source_path):

        source_path = Path(source_path)

        print(
            f"[VIDEO] Ingesting: {source_path.name}"
        )

        # 1. Validate
        self.validate_video(source_path)

        # 2. Generate unique ID
        video_id = self.generate_video_id()

        # 3. Destination path
        destination = (
            VIDEO_FOLDER
            / f"{video_id}{source_path.suffix.lower()}"
        )

        # 4. Copy video
        shutil.copy2(
            source_path,
            destination
        )

        # 5. Extract metadata
        metadata = self.extract_metadata(
            destination,
            video_id
        )

        # 6. Store final path
        metadata["path"] = str(destination)

        # 7. Save metadata JSON
        metadata_path = (
            METADATA_FOLDER
            / f"{video_id}.json"
        )

        with open(
            metadata_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                metadata,
                file,
                indent=2
            )

        # 8. Print summary
        print(
            f"[VIDEO] Created: {video_id}"
        )

        print(
            f"[VIDEO] Duration: "
            f"{metadata['duration']:.2f} sec"
        )

        print(
            f"[VIDEO] FPS: "
            f"{metadata['fps']:.2f}"
        )

        print(
            f"[VIDEO] Resolution: "
            f"{metadata['resolution']}"
        )

        return metadata