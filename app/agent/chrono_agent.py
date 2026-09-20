from app.query.query_engine import QueryEngine


class ChronoAgent:


    def __init__(
        self,
        video_id
    ):

        print(
            "[AGENT] Initializing ChronoAgent..."
        )


        self.video_id = video_id


        self.query_engine = QueryEngine(
            video_id
        )


        print(
            "[AGENT] Ready."
        )



    # ==========================================
    # ANSWER USER QUERY
    # ==========================================

    def answer(
        self,
        query
    ):


        print(
            "\n[AGENT QUERY]"
        )

        print(query)



        response = (
            self.query_engine.answer(
                query
            )
        )


        return response