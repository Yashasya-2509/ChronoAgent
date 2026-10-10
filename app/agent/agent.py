"""
ChronoAgent Core Agent

Responsible for:
- Query understanding
- Intent routing
- Temporal reasoning
- Hybrid retrieval
- Answer generation
"""


class ChronoAgent:


    def __init__(
        self,
        intent_classifier,
        retriever,
        temporal_reasoner,
        generator,
        memory_manager=None
    ):


        print("[AGENT] Initializing ChronoAgent...")


        self.intent_classifier = intent_classifier

        self.retriever = retriever

        self.temporal_reasoner = temporal_reasoner

        self.generator = generator

        self.memory_manager = memory_manager



        print("[AGENT] Ready.")





    # =====================================================
    # TEMPORAL INTENTS
    # =====================================================

    TEMPORAL_INTENTS = [

        "FIRST_EVENT",

        "LAST_EVENT",

        "BEFORE_EVENT",

        "AFTER_EVENT",

        "TIMELINE",

        "OBJECT_APPEARANCE_TIME",

        "OBJECT_HISTORY"

    ]





    # =====================================================
    # MAIN QUERY FUNCTION
    # =====================================================

    def ask(
        self,
        question,
        video_id
    ):


        print("\n[AGENT QUERY]")
        print(question)



        # ---------------------------------
        # STEP 1
        # INTENT DETECTION
        # ---------------------------------


        intent = self.intent_classifier.detect(
            question
        )


        print(
            "[INTENT]",
            intent
        )



        intent_name = intent.get(
            "intent"
        )




        # ---------------------------------
        # STEP 2
        # TEMPORAL ROUTING
        # ---------------------------------


        if intent_name in self.TEMPORAL_INTENTS:


            print(
                "[AGENT] Temporal reasoning activated"
            )


            memories = self.load_all_events(
                video_id
            )



            result = self.temporal_reasoner.reason(

                memories,

                question,

                intent

            )



            return {


                "video_id":

                    video_id,


                "query":

                    question,


                "intent":

                    intent,


                "answer":

                    result,


                "evidence":

                    self.extract_evidence(
                        result
                    )

            }





        # ---------------------------------
        # STEP 3
        # NORMAL RETRIEVAL
        # ---------------------------------


        print(
            "[AGENT] Hybrid retrieval activated"
        )



        retrieved = self.retriever.search(

            question,

            video_id

        )




        answer = self.generator.generate(

            question,

            retrieved

        )




        return {


            "video_id":

                video_id,


            "query":

                question,


            "intent":

                intent,


            "retrieval":

                retrieved,


            "answer":

                answer

        }





    # =====================================================
    # LOAD COMPLETE EVENT MEMORY
    # =====================================================

    def load_all_events(
        self,
        video_id
    ):


        if self.memory_manager is None:


            print(
                "[WARNING] Memory manager missing"
            )


            return []



        events = self.memory_manager.get_all_events(

            video_id

        )



        print(

            "[MEMORY] Loaded events:",

            len(events)

        )


        return events





    # =====================================================
    # EVIDENCE GENERATION
    # =====================================================

    def extract_evidence(
        self,
        result
    ):


        if result is None:

            return {}



        if isinstance(
            result,
            dict
        ):


            return {


                "frame":

                    result.get(
                        "start_frame",
                        ""
                    ),


                "timestamp":

                    result.get(
                        "start_time",
                        0
                    )


            }



        return {}





    # =====================================================
    # SIMPLE COMPATIBILITY
    # =====================================================

    def query(
        self,
        question,
        video_id
    ):


        return self.ask(

            question,

            video_id

        )