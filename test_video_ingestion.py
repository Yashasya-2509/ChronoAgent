
import sys
from pathlib import Path

from app.video_processing.video_ingestion import VideoIngestion
from app.database.chrono_database import ChronoDatabase


def main():

    # =========================================================
    # GET VIDEO PATH
    # =========================================================

    if len(sys.argv) < 2:

        print()
        print("=" * 60)
        print("VIDEO INGESTION TEST")
        print("=" * 60)
        print()

        print("Usage:")
        print(
            "python -m app.tests.test_video_ingestion "
            "<video_path>"
        )

        print()

        print("Example:")
        print(
            "python -m app.tests.test_video_ingestion "
            "data/videos/uploads/4917-3_70.mov"
        )

        print()

        sys.exit(1)

    video_path = Path(sys.argv[1])

    # =========================================================
    # CHECK VIDEO
    # =========================================================

    if not video_path.exists():

        print()
        print("=" * 60)
        print("ERROR")
        print("=" * 60)
        print()

        print(
            f"Video not found: {video_path}"
        )

        print()

        sys.exit(1)

    # =========================================================
    # VIDEO INGESTION
    # =========================================================

    ingestion = VideoIngestion()

    try:

        metadata = ingestion.ingest(
            str(video_path)
        )

    except Exception as e:

        print()
        print("=" * 60)
        print("INGESTION FAILED")
        print("=" * 60)
        print()

        print(
            f"Error: {e}"
        )

        print()

        sys.exit(1)

    # =========================================================
    # DATABASE
    # =========================================================

    database = ChronoDatabase()

    try:

        stored_path = (
            f"data/videos/"
            f"{metadata.video_id}."
            f"{metadata.format}"
        )

        database.insert_video(
            metadata,
            stored_path=stored_path
        )

        print()
        print(
            "[DATABASE] Video metadata stored successfully."
        )

    except Exception as e:

        print()
        print("=" * 60)
        print("DATABASE INSERT FAILED")
        print("=" * 60)
        print()

        print(
            f"Error: {e}"
        )

        print()

        database.close()

        sys.exit(1)

    # =========================================================
    # VERIFY DATABASE RECORD
    # =========================================================

    stored_video = database.get_video(
        metadata.video_id
    )

    print()
    print("=" * 60)
    print("DATABASE RECORD")
    print("=" * 60)

    if stored_video:

        print(
            f"Video ID     : "
            f"{stored_video['video_id']}"
        )

        print(
            f"Filename     : "
            f"{stored_video['filename']}"
        )

        print(
            f"Format       : "
            f"{stored_video['format']}"
        )

        print(
            f"Stored Path  : "
            f"{stored_video['stored_path']}"
        )

        print(
            f"FPS          : "
            f"{stored_video['fps']}"
        )

        print(
            f"Frames       : "
            f"{stored_video['frame_count']}"
        )

        print(
            f"Duration     : "
            f"{stored_video['duration']:.2f}s"
        )

        print(
            f"Resolution   : "
            f"{stored_video['width']}x"
            f"{stored_video['height']}"
        )

        print(
            f"Camera ID    : "
            f"{stored_video['camera_id']}"
        )

        print(
            f"Created At   : "
            f"{stored_video['created_at']}"
        )

    else:

        print(
            "ERROR: Video was not found in database."
        )

        database.close()

        sys.exit(1)

    # =========================================================
    # CLOSE DATABASE
    # =========================================================

    database.close()

    print()
    print("=" * 60)
    print("INGESTION + DATABASE SUCCESSFUL")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
