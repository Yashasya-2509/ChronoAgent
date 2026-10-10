import json
from pathlib import Path

from app.vector_memory.vector_store import VectorStore



class HybridRetriever:



    def __init__(
        self,
        graph_path,
        video_id
    ):


        self.graph_path = Path(
            graph_path
        )


        self.video_id = video_id



        if not self.graph_path.exists():

            raise FileNotFoundError(

                f"Knowledge graph not found: {self.graph_path}"

            )



        with open(
            self.graph_path,
            "r"
        ) as file:

            self.graph_data = json.load(file)



        # ===========================
        # CHROMA VECTOR STORE
        # ===========================

        self.vector_store = VectorStore()



        print(
            "[RETRIEVAL] Hybrid retriever initialized."
        )







    # ==================================================
    # VECTOR SEARCH (CHROMA)
    # ==================================================


    def vector_search(

        self,

        query,

        video_id,

        top_k=5

    ):



        results = self.vector_store.search(

            query,

            top_k=top_k

        )



        retrieved=[]



        for r in results:



            metadata = r.get(

                "metadata",

                {}

            )



            # ----------------------------
            # VIDEO FILTER
            # ----------------------------

            stored_video = metadata.get(

                "video_id"

            )



            # Some old memories don't have video_id
            # allow them


            if (

                stored_video is not None

                and

                stored_video != video_id

            ):

                continue





            retrieved.append({



                "memory_id":

                    metadata.get(

                        "event_id"

                    ),



                "description":

                    r.get(

                        "content"

                    ),



                "metadata":

                    metadata,



                "score":

                    r.get(

                        "score"

                    )

            })



            if len(retrieved) >= top_k:

                break



        return retrieved







    # ==================================================
    # GRAPH SEARCH
    # ==================================================


    def graph_search(

        self,

        vector_results,

        top_k=20

    ):



        results=[]


        event_ids=set()



        for item in vector_results:



            eid=item["metadata"].get(

                "event_id"

            )


            if eid:

                event_ids.add(eid)





        related_ids=set(event_ids)



        matching_edges=[]




        # -----------------------------
        # CONNECTED EVENTS
        # -----------------------------


        for edge in self.graph_data.get(

            "edges",

            []

        ):



            if (

                edge.get("source") in event_ids

                or

                edge.get("target") in event_ids

            ):



                matching_edges.append(edge)



                related_ids.add(

                    edge.get("source")

                )


                related_ids.add(

                    edge.get("target")

                )







        # -----------------------------
        # GRAPH NODES
        # -----------------------------


        for node in self.graph_data.get(

            "nodes",

            []

        ):



            if node.get("id") in related_ids:



                results.append({



                    "event_id":

                    node.get("id"),



                    "event_type":

                    node.get(
                        "event_type"
                    ),



                    "timestamp":

                    node.get(
                        "timestamp"
                    ),



                    "description":

                    node.get(
                        "description"
                    )

                })






        # -----------------------------
        # GRAPH EDGES
        # -----------------------------


        for edge in matching_edges:



            results.append({


                "source":

                edge.get(
                    "source"
                ),



                "target":

                edge.get(
                    "target"
                ),



                "relation":

                edge.get(
                    "relation"
                )

            })



        return results[:top_k]









    # ==================================================
    # HYBRID RETRIEVAL
    # ==================================================


    def retrieve(

        self,

        query,

        video_id,

        top_k=5,

        vector_top_k=None,

        graph_top_k=20

    ):



        print(

            "\n[RETRIEVAL] Query:"

        )

        print(query)





        vector_limit = (

            vector_top_k

            if vector_top_k is not None

            else top_k

        )





        vector_results=self.vector_search(

            query,

            video_id,

            vector_limit

        )





        graph_results=self.graph_search(

            vector_results,

            graph_top_k

        )





        print(

            f"[VECTOR] Results: {len(vector_results)}"

        )


        print(

            f"[GRAPH] Results: {len(graph_results)}"

        )





        return {



            "query":

                query,



            "video_id":

                video_id,



            "vector_results":

                vector_results,



            "graph_results":

                graph_results

        }