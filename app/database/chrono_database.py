
import sqlite3
from pathlib import Path

from app.config import DATABASE_PATH


class ChronoDatabase:

    def __init__(self, db_path=DATABASE_PATH):

        self.db_path = Path(db_path)

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.connection = sqlite3.connect(
            str(self.db_path)
        )

        self.connection.row_factory = sqlite3.Row

        # Enable foreign keys
        self.connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        self.create_tables()

        self.migrate_tables()

    # =========================================================
    # CREATE TABLES
    # =========================================================

    def create_tables(self):

        cursor = self.connection.cursor()

        # -----------------------------------------------------
        # VIDEO
        # -----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS VIDEO (
                video_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                format TEXT,
                stored_path TEXT,
                camera_id TEXT,
                fps REAL,
                frame_count INTEGER,
                duration REAL,
                width INTEGER,
                height INTEGER,
                created_at TEXT
            )
        """)

        # -----------------------------------------------------
        # SCENE
        # -----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS SCENE (
                scene_id TEXT PRIMARY KEY,
                video_id TEXT NOT NULL,
                start_frame INTEGER,
                end_frame INTEGER,
                start_time REAL,
                end_time REAL,

                FOREIGN KEY(video_id)
                    REFERENCES VIDEO(video_id)
                    ON DELETE CASCADE
            )
        """)

        # -----------------------------------------------------
        # FRAME
        # -----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS FRAME (
                frame_id TEXT PRIMARY KEY,
                video_id TEXT NOT NULL,
                scene_id TEXT,
                frame_number INTEGER,
                timestamp REAL,
                path TEXT,
                is_keyframe INTEGER DEFAULT 0,

                FOREIGN KEY(video_id)
                    REFERENCES VIDEO(video_id)
                    ON DELETE CASCADE,

                FOREIGN KEY(scene_id)
                    REFERENCES SCENE(scene_id)
                    ON DELETE SET NULL
            )
        """)

        self.connection.commit()

    # =========================================================
    # DATABASE MIGRATION
    # =========================================================

    def migrate_tables(self):

        """
        Safely upgrade an existing ChronoAgent database.

        This is important because your chrono.db may already
        contain the old VIDEO table structure.
        """

        cursor = self.connection.cursor()

        cursor.execute("""
            PRAGMA table_info(VIDEO)
        """)

        existing_columns = {
            row["name"]
            for row in cursor.fetchall()
        }

        # -----------------------------------------------------
        # Add FORMAT
        # -----------------------------------------------------

        if "format" not in existing_columns:

            cursor.execute("""
                ALTER TABLE VIDEO
                ADD COLUMN format TEXT
            """)

        # -----------------------------------------------------
        # Add STORED PATH
        # -----------------------------------------------------

        if "stored_path" not in existing_columns:

            cursor.execute("""
                ALTER TABLE VIDEO
                ADD COLUMN stored_path TEXT
            """)

        # -----------------------------------------------------
        # Add FRAME COUNT
        # -----------------------------------------------------

        if "frame_count" not in existing_columns:

            cursor.execute("""
                ALTER TABLE VIDEO
                ADD COLUMN frame_count INTEGER
            """)

        self.connection.commit()

    # =========================================================
    # INSERT VIDEO
    # =========================================================

    def insert_video(
        self,
        metadata,
        stored_path=None
    ):

        """
        Insert or update a video metadata record.

        Supports:
            - dictionary
            - VideoMetadata dataclass
        """

        # -----------------------------------------------------
        # Convert VideoMetadata object to dictionary
        # -----------------------------------------------------

        if hasattr(metadata, "to_dict"):

            metadata = metadata.to_dict()

        elif hasattr(metadata, "__dict__"):

            metadata = vars(metadata)

        # -----------------------------------------------------
        # Extract values
        # -----------------------------------------------------

        video_id = metadata["video_id"]

        filename = metadata["filename"]

        video_format = metadata.get(
            "format"
        )

        camera_id = metadata.get(
            "camera_id"
        )

        fps = metadata.get(
            "fps"
        )

        frame_count = metadata.get(
            "frame_count"
        )

        duration = metadata.get(
            "duration"
        )

        width = metadata.get(
            "width"
        )

        height = metadata.get(
            "height"
        )

        created_at = metadata.get(
            "created_at"
        )

        # -----------------------------------------------------
        # Insert / update
        # -----------------------------------------------------

        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO VIDEO (
                video_id,
                filename,
                format,
                stored_path,
                camera_id,
                fps,
                frame_count,
                duration,
                width,
                height,
                created_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            video_id,
            filename,
            video_format,
            stored_path,
            camera_id,
            fps,
            frame_count,
            duration,
            width,
            height,
            created_at
        ))

        self.connection.commit()

    # =========================================================
    # INSERT SCENE
    # =========================================================

    def insert_scene(self, scene):

        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO SCENE (
                scene_id,
                video_id,
                start_frame,
                end_frame,
                start_time,
                end_time
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            scene["scene_id"],
            scene["video_id"],
            scene["start_frame"],
            scene["end_frame"],
            scene["start_time"],
            scene["end_time"]
        ))

        self.connection.commit()

    # =========================================================
    # INSERT FRAME
    # =========================================================

    def insert_frame(self, frame):

        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO FRAME (
                frame_id,
                video_id,
                scene_id,
                frame_number,
                timestamp,
                path,
                is_keyframe
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            frame["frame_id"],
            frame["video_id"],
            frame.get("scene_id"),
            frame["frame_number"],
            frame["timestamp"],
            frame["path"],
            int(
                frame.get(
                    "is_keyframe",
                    False
                )
            )
        ))

        self.connection.commit()

    # =========================================================
    # GET VIDEO
    # =========================================================

    def get_video(self, video_id):

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT *
            FROM VIDEO
            WHERE video_id = ?
        """, (video_id,))

        return cursor.fetchone()

    # =========================================================
    # GET ALL VIDEOS
    # =========================================================

    def get_all_videos(self):

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT *
            FROM VIDEO
            ORDER BY created_at DESC
        """)

        return cursor.fetchall()

    # =========================================================
    # GET SCENES
    # =========================================================

    def get_scenes(self, video_id):

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT *
            FROM SCENE
            WHERE video_id = ?
            ORDER BY start_time
        """, (video_id,))

        return cursor.fetchall()

    # =========================================================
    # GET FRAMES
    # =========================================================

    def get_frames(self, video_id):

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT *
            FROM FRAME
            WHERE video_id = ?
            ORDER BY timestamp
        """, (video_id,))

        return cursor.fetchall()

    # =========================================================
    # GET KEYFRAMES
    # =========================================================

    def get_keyframes(self, video_id):

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT *
            FROM FRAME
            WHERE video_id = ?
              AND is_keyframe = 1
            ORDER BY timestamp
        """, (video_id,))

        return cursor.fetchall()

    # =========================================================
    # DATABASE STATISTICS
    # =========================================================

    def get_statistics(self, video_id):

        cursor = self.connection.cursor()

        # -----------------------------------------------------
        # Scene count
        # -----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM SCENE
            WHERE video_id = ?
        """, (video_id,))

        scene_count = cursor.fetchone()["count"]

        # -----------------------------------------------------
        # Frame count
        # -----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM FRAME
            WHERE video_id = ?
        """, (video_id,))

        frame_count = cursor.fetchone()["count"]

        # -----------------------------------------------------
        # Keyframe count
        # -----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM FRAME
            WHERE video_id = ?
              AND is_keyframe = 1
        """, (video_id,))

        keyframe_count = cursor.fetchone()["count"]

        return {
            "scene_count": scene_count,
            "frame_count": frame_count,
            "keyframe_count": keyframe_count
        }

    # =========================================================
    # DELETE VIDEO
    # =========================================================

    def delete_video(self, video_id):

        cursor = self.connection.cursor()

        cursor.execute("""
            DELETE FROM VIDEO
            WHERE video_id = ?
        """, (video_id,))

        self.connection.commit()

    # =========================================================
    # CLOSE
    # =========================================================

    def close(self):

        if self.connection:

            self.connection.close()
