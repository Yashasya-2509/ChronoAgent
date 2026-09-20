import json
from pathlib import Path


from app.retrieval.hybrid_retriever import HybridRetriever
from app.reasoning.temporal_reasoner import TemporalReasoner
from app.agent.answer_generator import AnswerGenerator
from app.evidence.evidence_retriever import EvidenceRetriever
from app.query.query_classifier import QueryClassifier



class QueryEngine:


    def __init__(
        self,
        video_id
    ):


        self.video_id = video_id


        # ==============================
        # PATHS
        # ==============================


        self.memory_path = (
            Path("data/memory")
            /
            f"{video_id}_event_memory.json"
        )


        self.graph_path = (
            Path("data/graphs")
            /
            f"{video_id}_graph.json"
        )


        if not self.memory_path.exists():

            raise FileNotFoundError(
                f"Memory missing: {self.memory_path}"
            )


        if not self.graph_path.exists():

            raise FileNotFoundError(
                f"Graph missing: {self.graph_path}"
            )



        # ==============================
        # LOAD MEMORY
        # ==============================


        with open(
            self.memory_path,
            "r"
        ) as f:

            data = json.load(f)


        self.memories = data["memories"]



        # ==============================
        # COMPONENTS
        # ==============================


        self.retriever = HybridRetriever(
            str(self.graph_path)
        )


        self.reasoner = TemporalReasoner()


        self.generator = AnswerGenerator()


        self.evidence_retriever = EvidenceRetriever()


        self.classifier = QueryClassifier()



    # =====================================================
    # OBJECT DETECTION
    # =====================================================


    def detect_object_name(
        self,
        query
    ):


        query = query.lower()


        objects=set()


        for memory in self.memories:


            name = memory.get(
                "class_name"
            )


            if name:

                objects.add(
                    name.lower()
                )



        for obj in objects:


            if obj in query:

                return obj


        return None




    # =====================================================
    # GET APPEARANCE EVENTS
    # =====================================================


    def get_appearance_events(
        self,
        object_name=None
    ):


        events=[]


        for event in self.memories:


            if (
                event.get("event_type")
                !=
                "OBJECT_APPEARED"
            ):

                continue



            if object_name:


                if (
                    event.get("class_name")
                    !=
                    object_name
                ):

                    continue



            events.append(event)



        return events




    # =====================================================
    # NORMALIZE EVENT
    # =====================================================


    def normalize_event(
        self,
        event
    ):


        # timeline is already formatted

        if isinstance(event, dict):

            if "timeline" in event:

                return event



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





    # =====================================================
    # MAIN QUERY FUNCTION
    # =====================================================


    def answer(
        self,
        query
    ):


        print(
            "\n[QUERY]",
            query
        )


        # ==============================
        # CLASSIFY QUERY
        # ==============================


        intent = (
            self.classifier.classify(
                query
            )
        )


        print(
            "[INTENT]",
            intent
        )



        # ==============================
        # RETRIEVAL
        # ==============================


        retrieval_results = (
            self.retriever.retrieve(
                query,
                top_k=5
            )
        )



        reasoning_result=None



        object_name = (
            self.detect_object_name(
                query
            )
        )


        intent_name = (
            intent["intent"]
        )




        # =================================================
        # FIRST EVENT
        # =================================================


        if intent_name == "FIRST_EVENT":


            events = (
                self.get_appearance_events(
                    object_name
                )
            )


            reasoning_result = (
                self.reasoner.find_first_event(
                    events
                )
            )




        # =================================================
        # LAST EVENT
        # =================================================


        elif intent_name == "LAST_EVENT":


            events = (
                self.get_appearance_events(
                    object_name
                )
            )


            reasoning_result = (
                self.reasoner.find_last_event(
                    events
                )
            )




        # =================================================
        # TIMELINE
        # =================================================


        elif intent_name == "TIMELINE":


            timeline = (
                self.reasoner.get_timeline(
                    self.memories
                )
            )


            reasoning_result = {


                "timeline":
                timeline,


                "description":
                "Complete event timeline",


                "start_time":
                0,


                "start_frame":
                "",


                "confidence":
                1.0

            }




        # =================================================
        # COUNT OBJECT
        # =================================================


        elif intent_name == "COUNT_OBJECT":


            count = len(
                self.get_appearance_events(
                    object_name
                )
            )


            reasoning_result = {


                "description":

                f"{count} {object_name or 'objects'} appeared.",


                "start_time":

                0,


                "start_frame":

                "",


                "confidence":

                1.0

            }




        # =================================================
        # GENERAL VECTOR SEARCH
        # =================================================


        else:


            results = (
                retrieval_results[
                    "vector_results"
                ]
            )


            if results:


                best_id = (
                    results[0]
                    ["memory_id"]
                )


                for memory in self.memories:


                    if (
                        memory["memory_id"]
                        ==
                        best_id
                    ):

                        reasoning_result = memory

                        break





        # =================================================
        # EMPTY HANDLING
        # =================================================


        if reasoning_result is None:


            reasoning_result = {


                "description":

                "No matching event found.",


                "start_time":

                0,


                "start_frame":

                "",


                "confidence":

                0.0

            }



        reasoning_result = (
            self.normalize_event(
                reasoning_result
            )
        )



        # ==============================
        # GENERATE ANSWER
        # ==============================


        answer = (
            self.generator.generate(
                query,
                reasoning_result
            )
        )



        # ==============================
        # EVIDENCE
        # ==============================


        evidence = (
            self.evidence_retriever.get_evidence(
                self.video_id,
                reasoning_result
            )
        )



        return {


            "video_id":

            self.video_id,


            "query":

            query,


            "intent":

            intent,


            "retrieval":

            retrieval_results,


            "answer":

            answer,


            "evidence":

            evidence

        }