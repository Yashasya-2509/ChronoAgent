from app.dataset.ucf_loader import UCFLoader
from app.pipeline.chrono_pipeline import ChronoPipeline



def main():


    loader = UCFLoader(
        "data/dataset/UCF-Crime"
    )


    videos = loader.get_videos()


    # FIRST TEST ONLY ONE VIDEO

    videos = videos[:1]


    pipeline = ChronoPipeline()



    for video in videos:


        print("\nPROCESSING:")
        print(video["name"])


        result = pipeline.run(
            video["path"]
        )


        print(result)



if __name__=="__main__":

    main()