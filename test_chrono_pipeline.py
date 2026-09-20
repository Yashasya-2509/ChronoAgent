from pathlib import Path

from app.pipeline.chrono_pipeline import ChronoPipeline


def main():

    print("\n")
    print("="*60)
    print(" CHRONOAGENT DYNAMIC PIPELINE TEST ")
    print("="*60)


    # ----------------------------------
    # USER INPUT VIDEO
    # ----------------------------------

    video_path = input(
        "\nEnter CCTV video path: "
    )


    video_path = Path(video_path)


    if not video_path.exists():

        print(
            "\nERROR: Video file does not exist"
        )

        return


    print(
        "\nSelected Video:",
        video_path
    )


    # ----------------------------------
    # RUN PIPELINE
    # ----------------------------------

    pipeline = ChronoPipeline()


    video_id = pipeline.run(
        str(video_path)
    )


    print("\n")
    print("="*60)
    print(" PIPELINE COMPLETE ")
    print("="*60)


    print(
        "Video ID:",
        video_id
    )


if __name__ == "__main__":
    main()