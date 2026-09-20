from pathlib import Path
import chromadb


class VectorStore:

    def __init__(
        self,
        persist_directory="data/vector_store",
        collection_name="chronoagent_events",
        batch_size=5000
    ):

        self.persist_directory = Path(
            persist_directory
        )

        self.persist_directory.mkdir(
            parents=True,
            exist_ok=True
        )


        self.batch_size = batch_size


        print(
            f"[VECTOR] Database: {self.persist_directory}"
        )


        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )


        self.collection = (
            self.client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "description":
                    "ChronoAgent event semantic memory"
                }
            )
        )


        print(
            "[VECTOR] Collection ready."
        )



    # =====================================================
    # SINGLE MEMORY
    # =====================================================

    def add_memory(
        self,
        memory,
        embedding
    ):


        self.collection.upsert(

            ids=[
                memory["memory_id"]
            ],

            embeddings=[
                embedding.tolist()
            ],

            documents=[
                memory["description"]
            ],

            metadatas=[
                self.create_metadata(memory)
            ]

        )



    # =====================================================
    # CREATE METADATA
    # =====================================================

    def create_metadata(
        self,
        memory
    ):


        return {

            "video_id":
                memory["video_id"],

            "event_id":
                memory["event_id"],

            "event_type":
                memory["event_type"],

            "track_id":
                str(memory["track_id"]),

            "class_name":
                str(memory["class_name"]),

            "start_time":
                float(memory["start_time"]),

            "end_time":
                float(memory["end_time"]),

            "start_frame":
                str(memory["start_frame"]),

            "end_frame":
                str(memory["end_frame"])

        }



    # =====================================================
    # MULTIPLE MEMORY WITH CHUNKING
    # =====================================================

    def add_memories(
        self,
        memories,
        embeddings
    ):


        total = len(memories)


        print(
            f"[VECTOR] Adding {total} memories"
        )



        inserted = 0



        for start in range(
            0,
            total,
            self.batch_size
        ):


            end = min(
                start + self.batch_size,
                total
            )


            batch_memories = memories[start:end]


            batch_embeddings = embeddings[start:end]



            ids = []
            documents = []
            metadatas = []
            vectors = []



            for memory, embedding in zip(
                batch_memories,
                batch_embeddings
            ):


                ids.append(
                    memory["memory_id"]
                )


                documents.append(
                    memory["description"]
                )


                metadatas.append(
                    self.create_metadata(memory)
                )


                vectors.append(
                    embedding.tolist()
                )




            self.collection.upsert(

                ids=ids,

                embeddings=vectors,

                documents=documents,

                metadatas=metadatas

            )



            inserted += len(ids)


            print(
                f"[VECTOR] Inserted {inserted}/{total}"
            )



        return inserted




    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        query_embedding,
        top_k=5
    ):


        results = self.collection.query(

            query_embeddings=[
                query_embedding.tolist()
            ],

            n_results=top_k

        )


        return results




    # =====================================================
    # COUNT
    # =====================================================

    def count(self):

        return self.collection.count()