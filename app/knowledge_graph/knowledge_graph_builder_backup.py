import networkx as nx
import json

from pathlib import Path



class KnowledgeGraphBuilder:


    def __init__(self):

        self.graph = nx.DiGraph()



    # =====================================================
    # ADD SINGLE EVENT NODE
    # =====================================================

    def add_event(
        self,
        event
    ):

        event_id = event["event_id"]


        # -----------------------------
        # Event Node
        # -----------------------------

        self.graph.add_node(

            event_id,

            type="EVENT",

            event_type=
                event.get("event_type"),

            class_name=
                event.get("class_name"),

            track_id=
                event.get("track_id"),

            timestamp=
                event.get("start_time"),

            description=
                event.get("description")

        )



        # -----------------------------
        # Object Node
        # -----------------------------

        if event.get("track_id") is not None:


            object_id = (
                f"OBJECT_{event['track_id']}"
            )


            self.graph.add_node(

                object_id,

                type="OBJECT",

                class_name=
                    event.get("class_name")

            )



            self.graph.add_edge(

                object_id,

                event_id,

                relation="PERFORMS"

            )





    # =====================================================
    # TEMPORAL RELATIONSHIPS
    # =====================================================

    def add_temporal_edges(self):


        event_nodes = []


        for node, data in self.graph.nodes(
            data=True
        ):


            if data.get("type") == "EVENT":


                event_nodes.append(

                    (
                        node,

                        data.get(
                            "timestamp",
                            0
                        )

                    )

                )



        event_nodes.sort(
            key=lambda x:x[1]
        )



        for i in range(
            len(event_nodes)-1
        ):


            current_event = (
                event_nodes[i][0]
            )


            next_event = (
                event_nodes[i+1][0]
            )



            self.graph.add_edge(

                current_event,

                next_event,

                relation="BEFORE"

            )





    # =====================================================
    # BUILD GRAPH (PIPELINE FUNCTION)
    # =====================================================

    def build_graph(
        self,
        events,
        output_path
    ):

        """
        Pipeline compatible function.

        Input:
            events -> list of detected events

        Output:
            JSON knowledge graph
        """



        # reset graph for new video

        self.graph = nx.DiGraph()



        print(
            "[GRAPH] Creating knowledge graph..."
        )



        # Add event nodes

        for event in events:

            self.add_event(
                event
            )



        # Add temporal edges

        self.add_temporal_edges()



        # Save graph

        self.save(
            output_path
        )


        print(
            "[GRAPH] Nodes:",
            self.graph.number_of_nodes()
        )


        print(
            "[GRAPH] Edges:",
            self.graph.number_of_edges()
        )


        return output_path





    # =====================================================
    # SAVE GRAPH
    # =====================================================

    def save(
        self,
        path
    ):


        path = Path(
            path
        )


        path.parent.mkdir(

            parents=True,

            exist_ok=True

        )



        graph_data = {


            "nodes":

            [

                {

                    "id": node,

                    **data

                }

                for node,data
                in self.graph.nodes(data=True)

            ],



            "edges":

            [

                {

                    "source": source,

                    "target": target,

                    **data

                }

                for source,target,data
                in self.graph.edges(data=True)

            ]

        }




        with open(
            path,
            "w"
        ) as file:


            json.dump(

                graph_data,

                file,

                indent=2

            )



        return str(path)