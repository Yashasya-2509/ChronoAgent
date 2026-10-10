from pathlib import Path
import json
from datetime import datetime


class EventMemory:


    def __init__(self):

        self.memory = []

        print("[MEMORY] Event Memory initialized")



    # =====================================================
    # GENERATE MEMORY ID
    # =====================================================

    def _generate_memory_id(self):

        return f"M{len(self.memory)+1:05d}"



    # =====================================================
    # OBJECT ID
    # =====================================================

    def _create_object_id(self, event):

        cls = event.get(
            "class_name",
            "unknown"
        )

        track = event.get(
            "track_id",
            "0"
        )

        return f"{cls}_{track}"



    # =====================================================
    # FRAME PATH
    # =====================================================

    def _frame_path(self, video_id, frame):

        if frame is None:
            return None

        return str(
            Path("data/frames")
            /
            str(video_id)
            /
            f"{frame}.jpg"
        )



    # =====================================================
    # ADD EVENT
    # =====================================================

    def add_event(self, event):

        video_id = event.get("video_id")

        start_time = float(
            event.get(
                "start_time",
                0
            )
        )

        end_time = float(
            event.get(
                "end_time",
                start_time
            )
        )


        memory_item = {

            "memory_id":
                self._generate_memory_id(),

            "video_id":
                video_id,


            "event_id":
                event.get(
                    "event_id"
                ),


            "event_type":
                event.get(
                    "event_type",
                    "UNKNOWN"
                ),



            "object_id":
                self._create_object_id(
                    event
                ),


            "track_id":
                event.get(
                    "track_id"
                ),


            "class_name":
                event.get(
                    "class_name"
                ),



            "start_time":
                start_time,


            "end_time":
                end_time,


            "duration":
                end_time-start_time,



            "start_frame":
                event.get(
                    "start_frame"
                ),


            "end_frame":
                event.get(
                    "end_frame"
                ),



            "evidence":{


                "start_frame_path":
                    self._frame_path(
                        video_id,
                        event.get(
                            "start_frame"
                        )
                    ),


                "end_frame_path":
                    self._frame_path(
                        video_id,
                        event.get(
                            "end_frame"
                        )
                    )

            },


            "description":
                event.get(
                    "description",
                    ""
                ),



            "confidence":
                float(
                    event.get(
                        "confidence",
                        0.0
                    )
                ),



            "relations":{

                "before":[],
                "after":[],
                "overlaps":[]

            },


            "created_at":
                datetime.now().isoformat()

        }



        self.memory.append(
            memory_item
        )


        return memory_item




    # =====================================================
    # ADD MULTIPLE EVENTS
    # =====================================================

    def add_events(self, events):

        results=[]

        for event in events:

            results.append(
                self.add_event(event)
            )


        self.build_temporal_relations()


        return results




    # =====================================================
    # BUILD TEMPORAL RELATIONS
    # =====================================================

    def build_temporal_relations(self):


        events = self.get_sorted_memory()


        for event1 in events:

            for event2 in events:


                if event1 == event2:
                    continue



                if event1["end_time"] < event2["start_time"]:


                    if event2["event_id"] not in event1["relations"]["before"]:

                        event1["relations"]["before"].append(
                            event2["event_id"]
                        )


                    if event1["event_id"] not in event2["relations"]["after"]:

                        event2["relations"]["after"].append(
                            event1["event_id"]
                        )



                elif (

                    event1["start_time"] <= event2["end_time"]

                    and

                    event2["start_time"] <= event1["end_time"]

                ):


                    if event2["event_id"] not in event1["relations"]["overlaps"]:

                        event1["relations"]["overlaps"].append(
                            event2["event_id"]
                        )



    # =====================================================
    # SORT EVENTS
    # =====================================================

    def get_sorted_memory(self):

        return sorted(
            self.memory,
            key=lambda x:
            (
                x.get(
                    "start_time",
                    0
                ),

                x.get(
                    "event_id",
                    ""
                )
            )
        )



    # =====================================================
    # GET ALL EVENTS FOR AGENT
    # =====================================================

    def get_all_events(self, video_id=None):


        if video_id is None:

            return self.memory



        return [

            event

            for event in self.memory

            if event.get("video_id") == video_id

        ]



    # =====================================================
    # OBJECT EVENTS
    # =====================================================

    def get_object_events(self, object_name):


        return [

            event

            for event in self.memory

            if event.get("class_name") == object_name

        ]



    # =====================================================
    # FIND OBJECT EVENTS
    # =====================================================

    def find_events_by_object(self, object_name):

        return self.get_object_events(
            object_name
        )



    # =====================================================
    # EVENT TYPE
    # =====================================================

    def get_event_type(self,event_type):


        return [

            event

            for event in self.memory

            if event.get("event_type") == event_type

        ]



    # =====================================================
    # FIRST EVENT
    # =====================================================

    def get_first_event(self):

        events = self.get_sorted_memory()

        if not events:
            return None

        return events[0]



    # =====================================================
    # COUNT OBJECTS
    # =====================================================

    def count_objects(self, object_name):


        tracks=set()


        for event in self.memory:


            if event.get("class_name") == object_name:

                tracks.add(
                    event.get("track_id")
                )


        return len(tracks)



    # =====================================================
    # SAVE
    # =====================================================

    def save(self, output_path):


        output_path = Path(
            output_path
        )


        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        data={

            "total_memories":
                len(self.memory),

            "created":
                datetime.now().isoformat(),

            "memories":
                self.memory

        }



        with open(
            output_path,
            "w"
        ) as f:


            json.dump(
                data,
                f,
                indent=4
            )


        print(
            "[MEMORY] Saved:",
            output_path
        )


        return output_path




    # =====================================================
    # LOAD
    # =====================================================

    def load(self,input_path):


        input_path=Path(
            input_path
        )


        with open(
            input_path,
            "r"
        ) as f:

            data=json.load(f)


        self.memory=data.get(
            "memories",
            []
        )


        print(
            "[MEMORY] Loaded",
            len(self.memory),
            "events"
        )


        return self.memory



    # =====================================================
    # GET ALL
    # =====================================================

    def get_all(self):

        return self.memory