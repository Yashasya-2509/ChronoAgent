from pathlib import Path


class UCFLoader:


    def __init__(self, dataset_path):

        self.dataset_path = Path(dataset_path)



    def get_videos(self):

        videos=[]


        for video in self.dataset_path.rglob("*.mp4"):


            category = video.parent.name


            videos.append({

                "name":
                    video.name,


                "path":
                    str(video),


                "category":
                    category

            })


        return videos