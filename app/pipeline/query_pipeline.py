import json
from pathlib import Path


from app.query.query_classifier import QueryClassifier
from app.retrieval.hybrid_retriever import HybridRetriever
from app.reasoning.temporal_reasoner import TemporalReasoner
from app.agent.answer_agent import AnswerAgent





class QueryPipeline:


    def __init__(
        self,
        graph_path
    ):


        print("[QUERY] Initializing Query Pipeline")



        self.graph_path = Path(
            graph_path
        )



        if not self.graph_path.exists():

            raise FileNotFoundError(
                f"Graph not found: {self.graph_path}"
            )



        self.classifier = QueryClassifier()



        self.retriever = HybridRetriever(

            str(self.graph_path)

        )



        self.reasoner = TemporalReasoner()



        self.answer_agent = AnswerAgent()



        print("[QUERY] Ready")






    # =====================================================
    # LOAD EVENT MEMORY
    # =====================================================

    def load_memory(
        self,
        memory_path
    ):


        memory_path = Path(
            memory_path
        )



        if not memory_path.exists():

            raise FileNotFoundError(
                f"Memory file not found: {memory_path}"
            )



        with open(
            memory_path,
            "r"
        ) as file:


            data = json.load(file)



        return data.get(
            "memories",
            []
        )







    # =====================================================
    # MAIN QUERY FUNCTION
    # =====================================================

    def ask(
        self,
        query,
        memory_path
    ):


        print("\n")
        print("="*60)
        print(" CHRONOAGENT QUERY ")
        print("="*60)



        print(
            "QUERY:",
            query
        )





        # =====================================
        # 1 QUERY CLASSIFICATION
        # =====================================


        query_type = self.classifier.classify(

            query

        )



        print(
            "Query Type:",
            query_type
        )







        # =====================================
        # 2 LOAD EVENT MEMORY
        # =====================================


        event_memories = self.load_memory(

            memory_path

        )



        print(
            "Event memories loaded:",
            len(event_memories)
        )







        # =====================================
        # 3 HYBRID RETRIEVAL
        # =====================================


        retrieved_memories = self.retriever.retrieve(

            query,

            top_k=10

        )



        print(
            "Retrieved memories:",
            len(retrieved_memories)
        )







        # =====================================
        # 4 TEMPORAL REASONING
        # =====================================


        reasoning = self.reasoner.reason(

            event_memories,

            query

        )



        print(
            "Reasoning completed"
        )







        # =====================================
        # 5 ANSWER GENERATION
        # =====================================


        answer = self.answer_agent.generate(

            query,

            reasoning

        )



        print(
            "Answer generated"
        )



        print("="*60)



        return answer