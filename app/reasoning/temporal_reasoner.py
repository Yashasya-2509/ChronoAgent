import json



class TemporalReasoner:


    def __init__(self):

        pass



    # ==========================================
    # SORT EVENTS BY TIME
    # ==========================================

    def sort_events_by_time(
        self,
        memories
    ):


        return sorted(

            memories,

            key=lambda x:

            x.get(
                "start_time",
                x.get(
                    "metadata",
                    {}
                ).get(
                    "start_time",
                    0
                )
            )

        )




    # ==========================================
    # NORMALIZE EVENT FORMAT
    # ==========================================

    def normalize_event(
        self,
        event
    ):


        if "description" in event:

            return event



        metadata = event.get(
            "metadata",
            {}
        )


        return {


            "memory_id":
            event.get(
                "memory_id"
            ),


            "event_id":
            metadata.get(
                "event_id"
            ),


            "event_type":
            metadata.get(
                "event_type"
            ),


            "class_name":
            metadata.get(
                "class_name"
            ),


            "track_id":
            metadata.get(
                "track_id"
            ),


            "description":

            event.get(
                "description",
                "Unknown event"
            ),


            "start_time":

            metadata.get(
                "start_time",
                0
            ),


            "start_frame":

            metadata.get(
                "start_frame",
                ""
            ),


            "confidence":

            1.0

        }




    # ==========================================
    # FIRST EVENT
    # ==========================================

    def find_first_event(
        self,
        memories,
        object_name=None
    ):


        events = [

            self.normalize_event(e)

            for e in memories

        ]


        events = self.sort_events_by_time(
            events
        )


        if object_name:


            events = [

                e

                for e in events

                if e.get(
                    "class_name"
                )
                ==
                object_name

            ]



        if not events:

            return None



        return events[0]





    # ==========================================
    # LAST EVENT
    # ==========================================

    def find_last_event(
        self,
        memories,
        object_name=None
    ):


        events = [

            self.normalize_event(e)

            for e in memories

        ]


        events = self.sort_events_by_time(
            events
        )


        if object_name:


            events = [

                e

                for e in events

                if e.get(
                    "class_name"
                )
                ==
                object_name

            ]



        if not events:

            return None



        return events[-1]





    # ==========================================
    # COUNT OBJECTS
    # ==========================================

    def count_objects(
        self,
        memories,
        object_name
    ):


        tracks=set()



        for event in memories:


            e = self.normalize_event(
                event
            )


            if (

                e.get(
                    "class_name"
                )
                ==
                object_name

            ):


                tracks.add(
                    e.get(
                        "track_id"
                    )
                )



        return len(tracks)




    # ==========================================
    # CREATE TIMELINE
    # ==========================================

    def create_timeline(
        self,
        memories
    ):


        timeline=[]


        events=[

            self.normalize_event(e)

            for e in memories

        ]


        events = self.sort_events_by_time(
            events
        )



        for event in events:


            timeline.append({


                "time":

                event.get(
                    "start_time",
                    0
                ),


                "event":

                event.get(
                    "description",
                    ""
                ),


                "frame":

                event.get(
                    "start_frame",
                    ""
                )


            })


        return timeline





    # ==========================================
    # GET TIMELINE
    # QueryEngine compatible
    # ==========================================

    def get_timeline(
        self,
        memories
    ):


        return self.create_timeline(
            memories
        )





    # ==========================================
    # BEFORE EVENT
    # ==========================================

    def find_before_event(
        self,
        memories,
        target_time
    ):


        events=[

            self.normalize_event(e)

            for e in memories

        ]


        events=self.sort_events_by_time(
            events
        )


        previous=[]


        for event in events:


            if (

                event["start_time"]

                <
                target_time

            ):

                previous.append(event)



        if previous:

            return previous[-1]


        return None





    # ==========================================
    # AFTER EVENT
    # ==========================================

    def find_after_event(
        self,
        memories,
        target_time
    ):


        events=[

            self.normalize_event(e)

            for e in memories

        ]


        events=self.sort_events_by_time(
            events
        )


        for event in events:


            if (

                event["start_time"]

                >
                target_time

            ):

                return event



        return None