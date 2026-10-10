from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings





class VectorStore:



    def __init__(self):


        print("[VECTOR] Initializing Chroma RAG store")



        self.persist_directory = Path(
            "data/chroma_db"
        )


        self.persist_directory.mkdir(
            parents=True,
            exist_ok=True
        )



        # ============================
        # EMBEDDING MODEL
        # ============================


        self.embedding_model = HuggingFaceEmbeddings(

            model_name=
            "sentence-transformers/all-MiniLM-L6-v2"

        )



        # ============================
        # CHROMA DATABASE
        # ============================


        self.db = Chroma(

            persist_directory=
            str(self.persist_directory),


            embedding_function=
            self.embedding_model,


            collection_name=
            "chronoagent_memory"

        )



        print(
            "[VECTOR] Chroma database ready"
        )







    # =====================================================
    # ADD MEMORIES
    # =====================================================


    def add_memories(
        self,
        memories,
        embeddings=None
    ):



        if not memories:

            return



        texts=[]

        metadatas=[]



        for memory in memories:



            description = memory.get(

                "description",

                ""

            )



            if not description:

                continue



            texts.append(
                description
            )



            metadatas.append({



                "event_id":

                str(
                    memory.get(
                        "event_id",
                        ""
                    )
                ),



                "event_type":

                str(
                    memory.get(
                        "event_type",
                        ""
                    )
                ),



                "object":

                str(
                    memory.get(
                        "class_name",
                        ""
                    )
                ),



                "track_id":

                str(
                    memory.get(
                        "track_id",
                        ""
                    )
                ),



                "timestamp":

                float(
                    memory.get(
                        "start_time",
                        0
                    )
                )

            })



        if texts:



            self.db.add_texts(

                texts=texts,

                metadatas=metadatas

            )



        print(

            f"[VECTOR] Added {len(texts)} memories"

        )









    # =====================================================
    # SEARCH FUNCTION
    # Compatible with HybridRetriever
    # =====================================================


    def search(

        self,

        query,

        k=5,

        top_k=None

    ):


        # HybridRetriever uses top_k
        if top_k is not None:

            k = top_k



        results = self.db.similarity_search_with_score(

            query,

            k=k

        )



        output=[]



        for doc,score in results:



            output.append({



                "content":

                doc.page_content,



                "metadata":

                doc.metadata,



                "score":

                float(score)

            })



        return output







    # =====================================================
    # LANGCHAIN SIMILARITY SEARCH
    # =====================================================


    def similarity_search(

        self,

        query,

        k=5

    ):


        return self.db.similarity_search(

            query,

            k=k

        )








    # =====================================================
    # DELETE COLLECTION
    # =====================================================


    def clear(self):


        self.db.delete_collection()



        print(
            "[VECTOR] Collection cleared"
        )








    # =====================================================
    # COUNT DOCUMENTS
    # =====================================================


    def count_documents(self):


        try:


            return self.db._collection.count()



        except Exception:


            return 0