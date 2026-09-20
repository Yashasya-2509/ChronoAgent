from app.video_processing.video_ingestion import VideoIngestion


def main():

    ingestion = VideoIngestion()
    metadata = ingestion.ingest(
    "data/videos/converted/crosswalk.mp4"
)
    

    print("\n========== VIDEO METADATA ==========")

    for key, value in metadata.items():
        print(f"{key}: {value}")

    print("\nVideo ingestion successful!")


if __name__ == "__main__":
    main()