from app.vector_memory.vector_store import VectorStore



class LangChainRetriever:


    def __init__(self):

        print("[RAG] Initializing retriever")

        self.vector_store = VectorStore()

        self.db = self.vector_store.db



    def retrieve(self, query, k=5):


        results = self.db.similarity_search(
            query,
            k=k
        )


        events=[]


        for doc in results:


            events.append({

                "content":
                    doc.page_content,


                "metadata":
                    doc.metadata

            })


        return events