import networkx as nx
from datetime import datetime


class KnowledgeGraphBuilder:


    def __init__(self):

        print("[KG] Knowledge Graph Builder initialized")

        self.graph = nx.DiGraph()



    # =====================================================
    # CREATE VIDEO NODE
    # =====================================================

    def add_video(self, video_id):

        if video_id not in self.graph:

            self.graph.add_node(
                video_id,
                type="VIDEO",
                created=datetime.now().isoformat()
            )



    # =====================================================
    # OBJECT NODE
    # =====================================================

    def add_object(
        self,
        object_id,
        class_name,
        timestamp
    ):


        if object_id not in self.graph:


            self.graph.add_node(

                object_id,

                type="OBJECT",

                class_name=class_name,

                first_seen=timestamp,

                last_seen=timestamp,

                event_count=0

            )


        else:


            self.graph.nodes[object_id]["last_seen"] = timestamp



    # =====================================================
    # EVENT NODE
    # =====================================================

    def add_event(
        self,
        event_id,
        event_type,
        description,
        timestamp,
        frame=""
    ):


        self.graph.add_node(

            event_id,

            type="EVENT",

            event_type=event_type,

            description=description,

            timestamp=timestamp,

            frame=frame

        )



    # =====================================================
    # ADD OBJECT EVENT RELATION
    # =====================================================

    def connect_object_event(

        self,

        object_id,

        event_id

    ):


        self.graph.add_edge(

            object_id,

            event_id,

            relation="PERFORMED"

        )



        self.graph.nodes[object_id]["event_count"] += 1



    # =====================================================
    # VIDEO OBJECT RELATION
    # =====================================================

    def connect_video_object(

        self,

        video_id,

        object_id

    ):


        self.graph.add_edge(

            video_id,

            object_id,

            relation="CONTAINS"

        )



    # =====================================================
    # TEMPORAL RELATIONS
    # =====================================================

    def add_temporal_relation(

        self,

        event1,

        event2

    ):


        t1=self.graph.nodes[event1].get(
            "timestamp",
            0
        )


        t2=self.graph.nodes[event2].get(
            "timestamp",
            0
        )


        if t1 < t2:


            self.graph.add_edge(

                event1,

                event2,

                relation="BEFORE"

            )


        elif t2 < t1:


            self.graph.add_edge(

                event2,

                event1,

                relation="BEFORE"

            )



    # =====================================================
    # BUILD GRAPH FROM MEMORIES
    # =====================================================

    def build(

        self,

        video_id,

        memories

    ):


        print("[KG] Building Knowledge Graph")


        self.add_video(video_id)



        previous_event=None



        for memory in memories:



            event_id = memory.get(
                "event_id"
            )


            if not event_id:

                continue



            timestamp = memory.get(

                "start_time",

                memory.get(

                    "timestamp",

                    0

                )

            )



            object_class = memory.get(

                "class_name",

                memory.get(

                    "object",

                    "unknown"

                )

            )


            track_id = memory.get(

                "track_id",

                "0"

            )



            object_id = (

                object_class.upper()

                +

                "_"

                +

                str(track_id)

            )



            # object

            self.add_object(

                object_id,

                object_class,

                timestamp

            )



            # event

            self.add_event(

                event_id,

                memory.get(
                    "event_type",
                    "UNKNOWN"
                ),

                memory.get(
                    "description",
                    ""
                ),

                timestamp,

                memory.get(
                    "start_frame",
                    ""
                )

            )



            # relations

            self.connect_video_object(

                video_id,

                object_id

            )



            self.connect_object_event(

                object_id,

                event_id

            )



            if previous_event:


                self.add_temporal_relation(

                    previous_event,

                    event_id

                )



            previous_event=event_id



        print(

            "[KG] Nodes:",

            self.graph.number_of_nodes()

        )


        print(

            "[KG] Edges:",

            self.graph.number_of_edges()

        )



        return self.graph



    # =====================================================
    # OBJECT SUMMARY
    # =====================================================

    def get_objects(self):


        objects=[]


        for node,data in self.graph.nodes(data=True):


            if data.get("type")=="OBJECT":


                objects.append(

                    {

                    "object_id":node,

                    "class":data.get(
                        "class_name"
                    ),

                    "first_seen":data.get(
                        "first_seen"
                    ),

                    "last_seen":data.get(
                        "last_seen"
                    ),

                    "events":data.get(
                        "event_count"
                    )

                    }

                )


        return objects