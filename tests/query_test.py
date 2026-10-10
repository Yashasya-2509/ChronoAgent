from app.pipeline.query_pipeline import QueryPipeline



# =========================================================
# SELECT VIDEO MEMORY
# =========================================================

VIDEO_ID = "VID_9b8f8d24"



GRAPH_PATH = (
    "data/graphs/"
    f"{VIDEO_ID}_graph.json"
)


MEMORY_PATH = (
    "data/memory/"
    f"{VIDEO_ID}_event_memory.json"
)





# =========================================================
# QUERY TEST
# =========================================================


def main():


    print("\n")
    print("=" * 60)
    print(" CHRONOAGENT QUERY TEST ")
    print("=" * 60)



    print(
        "\nVIDEO:",
        VIDEO_ID
    )


    print(
        "GRAPH:",
        GRAPH_PATH
    )


    print(
        "MEMORY:",
        MEMORY_PATH
    )





    # -----------------------------------------
    # INITIALIZE QUERY PIPELINE
    # -----------------------------------------


    pipeline = QueryPipeline(

        GRAPH_PATH

    )





    # -----------------------------------------
    # TEST QUERY
    # -----------------------------------------


    query = (

        "Which object appeared first?"

    )



    answer = pipeline.ask(

        query,

        MEMORY_PATH

    )





    # -----------------------------------------
    # OUTPUT
    # -----------------------------------------


    print("\n")

    print("=" * 60)

    print(" FINAL ANSWER ")

    print("=" * 60)



    print(answer)





if __name__ == "__main__":

    main()