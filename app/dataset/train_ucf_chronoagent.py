import time
import json
import shutil
from pathlib import Path


from app.pipeline.chrono_pipeline import ChronoPipeline
from app.dataset.ucf_loader import UCFLoader



# ==================================================
# PATHS
# ==================================================

DATASET_PATH = "data/dataset/UCF-Crime"


RESULT_PATH = (
    Path("data/results")
    /
    "ucf_results.json"
)



# ==================================================
# TEMPORARY DATA CLEANUP
# DO NOT DELETE MEMORY OR GRAPH
# ==================================================

CLEANUP_DIRS = [

    "data/videos",
    "data/frames",
    "data/tracks",
    "data/detections"

]



# ==================================================
# CLEAN TEMPORARY STORAGE
# ==================================================

def cleanup_storage():

    print("\n[CLEANUP] Removing temporary files...")


    for folder in CLEANUP_DIRS:


        path = Path(folder)


        if not path.exists():

            continue



        for item in path.iterdir():

            try:


                if item.is_file():

                    item.unlink()


                elif item.is_dir():

                    shutil.rmtree(item)



            except Exception as e:


                print(
                    "[CLEANUP ERROR]",
                    item,
                    e
                )


    print("[CLEANUP] Temporary files removed")





# ==================================================
# MAIN
# ==================================================

def main():


    print("="*60)

    print(
        " CHRONOAGENT UCF DATASET PROCESSING "
    )

    print("="*60)



    dataset = Path(
        DATASET_PATH
    )


    if not dataset.exists():

        raise FileNotFoundError(
            f"Dataset missing: {DATASET_PATH}"
        )



    # -----------------------------
    # LOAD DATASET
    # -----------------------------


    loader = UCFLoader(
        DATASET_PATH
    )


    videos = loader.get_videos()



    print()

    print(
        "TOTAL VIDEOS:",
        len(videos)
    )



    # -----------------------------
    # INITIALIZE PIPELINE
    # -----------------------------


    print(
        "\nInitializing ChronoAgent..."
    )


    pipeline = ChronoPipeline()



    results = []

    success = 0

    failed = 0



    # -----------------------------
    # PROCESS VIDEOS
    # -----------------------------


    for i, video in enumerate(videos):


        print("\n")

        print("="*60)

        print(
            f"PROCESSING VIDEO {i+1}/{len(videos)}"
        )


        print(
            video["name"]
        )

        print("="*60)



        start = time.time()



        try:


            output = pipeline.run(
                video["path"]
            )



            output.update({

                "video_name":
                    video["name"],


                "category":
                    video["category"],


                "processing_time":
                    round(
                        time.time()-start,
                        3
                    )

            })



            results.append(
                output
            )


            success += 1



            print(
                "\nSUCCESS"
            )



        except Exception as e:


            failed += 1


            print(
                "\nFAILED:",
                e
            )



        # -----------------------------
        # SAVE PROGRESS
        # -----------------------------


        RESULT_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        with open(
            RESULT_PATH,
            "w"
        ) as f:


            json.dump(
                results,
                f,
                indent=4
            )



        print(
            f"\nProgress: {i+1}/{len(videos)}"
        )



        # -----------------------------
        # FREE DISK SPACE
        # -----------------------------


        cleanup_storage()



    # -----------------------------
    # FINAL REPORT
    # -----------------------------


    print("\n")

    print("="*60)

    print(
        " DATASET PROCESSING COMPLETE "
    )

    print("="*60)



    print(
        "Total videos:",
        len(videos)
    )


    print(
        "Successful:",
        success
    )


    print(
        "Failed:",
        failed
    )


    print(
        "Results saved:",
        RESULT_PATH
    )


    print("\nIMPORTANT DATA KEPT:")

    print(
        "✓ data/memory"
    )

    print(
        "✓ data/graphs"
    )

    print(
        "✓ data/vector_store"
    )

    print(
        "✓ data/results"
    )





if __name__ == "__main__":

    main()