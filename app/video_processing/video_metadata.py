from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json


@dataclass
class VideoMetadata:

    video_id: str
    filename: str
    format: str

    fps: float
    frame_count: int
    duration: float

    width: int
    height: int

    camera_id: str | None = None
    created_at: str | None = None

    @property
    def resolution(self):
        return f"{self.width}x{self.height}"

    def to_dict(self):
        data = asdict(self)
        data["resolution"] = self.resolution
        return data

    def save_json(self, output_path):

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(
                self.to_dict(),
                f,
                indent=4
            )