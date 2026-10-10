class AnswerAgent:


    def __init__(self):

        print("[ANSWER] Answer Agent initialized")



    def generate(
        self,
        query,
        reasoning
    ):

        """
        Convert reasoning output into final answer.
        """


        if reasoning is None:

            return {
                "answer":
                    "No relevant evidence found.",
                "evidence":
                    []
            }



        # If reasoning already contains answer

        if isinstance(reasoning, dict):


            answer = reasoning.get(
                "answer",
                None
            )


            evidence = reasoning.get(
                "evidence",
                []
            )



            if answer:


                return {

                    "query":
                        query,

                    "answer":
                        answer,

                    "evidence":
                        evidence

                }



        # fallback response


        return {


            "query":
                query,


            "answer":
                str(reasoning),


            "evidence":
                []

        }