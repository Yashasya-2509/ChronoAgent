import json
from pathlib import Path

from app.vector_memory.embedding_manager import EmbeddingManager
from app.vector_memory.vector_store import VectorStore


class HybridRetriever:


    def __init__(
        self,
        graph_path
    ):

        self.graph_path = Path(
            graph_path
        )


        if not self.graph_path.exists():

            raise FileNotFoundError(
                f"Knowledge graph not found: {self.graph_path}"
            )


        with open(
            self.graph_path,
            "r"
        ) as file:

            self.graph_data = json.load(file)



        self.embedding_manager = EmbeddingManager()

        self.vector_store = VectorStore()


        print(
            "[RETRIEVAL] Hybrid retriever initialized."
        )



    # ==================================================
    # VECTOR SEARCH
    # ==================================================

    def vector_search(
        self,
        query,
        top_k=5
    ):


        query_embedding = (
            self.embedding_manager.encode(
                query
            )
        )


        results = self.vector_store.search(
            query_embedding,
            top_k=top_k
        )


        retrieved=[]


        ids = results.get(
            "ids",
            [[]]
        )[0]


        documents = results.get(
            "documents",
            [[]]
        )[0]


        metadatas = results.get(
            "metadatas",
            [[]]
        )[0]


        distances = results.get(
            "distances",
            [[]]
        )[0]



        for i in range(len(ids)):

            retrieved.append({

                "memory_id":
                    ids[i],


                "description":
                    documents[i],


                "metadata":
                    metadatas[i],


                "distance":
                    distances[i]

            })


        return retrieved



    # ==================================================
    # GRAPH SEARCH
    # ==================================================

    def graph_search(
        self,
        vector_results
    ):


        results=[]


        event_ids=set()



        # -----------------------------------
        # Extract event ids from metadata
        # -----------------------------------

        for result in vector_results:


            metadata = result.get(
                "metadata",
                {}
            )


            event_id = metadata.get(
                "event_id"
            )


            if event_id:

                event_ids.add(
                    event_id
                )



        # -----------------------------------
        # Search connected graph edges
        # -----------------------------------

        for edge in self.graph_data["edges"]:


            if (
                edge["source"] in event_ids
                or
                edge["target"] in event_ids
            ):


                results.append({

                    "source":
                        edge["source"],


                    "target":
                        edge["target"],


                    "relation":
                        edge.get(
                            "relation"
                        )

                })



        # -----------------------------------
        # Also return event information
        # -----------------------------------

        for node in self.graph_data["nodes"]:


            if node["id"] in event_ids:


                results.append({

                    "event_id":
                        node["id"],


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



        return results



    # ==================================================
    # HYBRID RETRIEVAL
    # ==================================================

    def retrieve(
        self,
        query,
        top_k=5
    ):


        print(
            "\n[RETRIEVAL] Query:"
        )

        print(query)



        vector_results = (
            self.vector_search(
                query,
                top_k
            )
        )



        graph_results = (
            self.graph_search(
                vector_results
            )
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


            "vector_results":
                vector_results,


            "graph_results":
                graph_results

        }