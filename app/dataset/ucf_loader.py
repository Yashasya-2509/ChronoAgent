from pathlib import Path


class UCFLoader:


    def __init__(self, dataset_path):

        self.dataset_path = Path(dataset_path)



    def get_videos(self):

        videos = []


        for video in self.dataset_path.rglob("*.mp4"):

            videos.append({

                "path": str(video),

                "name": video.name,

                "category": video.parent.name

            })


        return videos




if __name__ == "__main__":


    loader = UCFLoader(
        "data/dataset/UCF-Crime"
    )


    videos = loader.get_videos()


    print("="*60)

    print(
        "TOTAL VIDEOS:",
        len(videos)
    )

    print("="*60)


    for video in videos[:10]:

        print(video)