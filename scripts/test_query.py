from app.query.query_pipeline import QueryPipeline


graph_path = "data/graphs/VID_f6241814_graph.json"

memory_path = "data/memory/VID_f6241814_event_memory.json"



query_engine = QueryPipeline(
    graph_path
)



questions = [

    "Which object appeared first?",

    "Which person appeared first?",

    "Show timeline"

]



for q in questions:

    print("\n====================")

    print(q)


    answer = query_engine.ask(
        q,
        memory_path
    )


    print(answer)