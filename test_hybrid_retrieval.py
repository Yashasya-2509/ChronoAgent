import json
from pathlib import Path

from app.retrieval.hybrid_retriever import HybridRetriever


# -------------------------------------------------
# DATA DIRECTORIES
# -------------------------------------------------

MEMORY_FOLDER = Path(
    "data/memory"
)

GRAPH_FOLDER = Path(
    "data/graphs"
)


# -------------------------------------------------
# FIND LATEST EVENT MEMORY
# -------------------------------------------------

def get_latest_memory_file():

    memory_files = list(
        MEMORY_FOLDER.glob(
            "*_event_memory.json"
        )
    )

    if not memory_files:

        raise FileNotFoundError(
            "No event memory files found."
        )

    latest_file = max(
        memory_files,
        key=lambda file: file.stat().st_mtime
    )

    return latest_file



# -------------------------------------------------
# EXTRACT VIDEO ID
# -------------------------------------------------

def extract_video_id(memory_file):

    filename = memory_file.stem

    video_id = filename.replace(
        "_event_memory",
        ""
    )

    return video_id



# -------------------------------------------------
# MAIN
# -------------------------------------------------

def main():


    print("\n")
    print("=" * 60)
    print(" CHRONOAGENT - HYBRID RETRIEVAL ")
    print("=" * 60)


    # ---------------------------------------------
    # FIND VIDEO DATA DYNAMICALLY
    # ---------------------------------------------

    memory_file = get_latest_memory_file()

    video_id = extract_video_id(
        memory_file
    )


    graph_file = (
        GRAPH_FOLDER /
        f"{video_id}_graph.json"
    )


    print("\nVideo ID:")
    print(video_id)


    print("\nMemory File:")
    print(memory_file)


    print("\nGraph File:")
    print(graph_file)



    if not graph_file.exists():

        raise FileNotFoundError(
            f"Graph file missing: {graph_file}"
        )



    # ---------------------------------------------
    # LOAD EVENT MEMORY
    # ---------------------------------------------

    with open(
        memory_file,
        "r"
    ) as file:

        memory_data = json.load(
            file
        )


    memories = memory_data[
        "memories"
    ]


    print(
        "\nMemories loaded:",
        len(memories)
    )



    # ---------------------------------------------
    # INITIALIZE HYBRID RETRIEVER
    # ---------------------------------------------

    retriever = HybridRetriever(
        graph_path=str(graph_file)
    )



    # ---------------------------------------------
    # USER QUERY
    # ---------------------------------------------

    query = (
        "When did a person appear?"
    )


    results = retriever.retrieve(
        query=query,
        top_k=3
    )



    # ---------------------------------------------
    # VECTOR SEARCH OUTPUT
    # ---------------------------------------------

    print("\n")
    print(
        "VECTOR SEARCH RESULTS"
    )

    print("-" * 40)


    for result in results[
        "vector_results"
    ]:

        print(
            f"Memory ID: {result['memory_id']}"
        )

        print(
            f"Description: {result['description']}"
        )

        print(
            f"Distance: {result['distance']:.4f}"
        )

        print()



    # ---------------------------------------------
    # GRAPH SEARCH OUTPUT
    # ---------------------------------------------

    print("\n")
    print(
        "GRAPH RELATIONSHIPS"
    )

    print("-" * 40)


    if results[
        "graph_results"
    ]:

        for relation in results[
            "graph_results"
        ]:

            print(
                f"{relation['source']} "
                f"--{relation['relation']}--> "
                f"{relation['target']}"
            )

    else:

        print(
            "No graph relationships found."
        )



    print("\n")
    print("=" * 60)
    print(
        " HYBRID RETRIEVAL COMPLETE "
    )
    print("=" * 60)



if __name__ == "__main__":

    main()