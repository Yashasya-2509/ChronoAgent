import json
from pathlib import Path

from app.reasoning.temporal_reasoner import TemporalReasoner



# ============================================================
# Automatically find latest event memory
# ============================================================

MEMORY_FOLDER = Path(
    "data/memory"
)



def get_latest_memory():

    memory_files = list(
        MEMORY_FOLDER.glob(
            "*_event_memory.json"
        )
    )


    if not memory_files:

        raise FileNotFoundError(
            "No event memory found. Run ChronoPipeline first."
        )


    # latest created file
    latest_file = max(
        memory_files,
        key=lambda x: x.stat().st_mtime
    )


    return latest_file





def main():


    print("\n")
    print("="*60)
    print(" CHRONOAGENT TEMPORAL REASONING ")
    print("="*60)



    # ========================================================
    # Load latest memory
    # ========================================================

    memory_path = get_latest_memory()


    print(
        "\nUsing Memory:"
    )

    print(
        memory_path
    )



    with open(
        memory_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)



    memories = data.get(
        "memories",
        []
    )



    print(
        "\nMemories loaded:",
        len(memories)
    )



    if len(memories)==0:

        raise Exception(
            "Memory file is empty"
        )





    # ========================================================
    # Temporal Reasoner
    # ========================================================

    agent = TemporalReasoner()





    # ========================================================
    # Test 1: First appearance
    # ========================================================


    print("\nFIRST PERSON APPEARANCE")
    print("-"*40)



    result = agent.find_first_event(
        memories,
        "person"
    )



    print(
        result
    )






    # ========================================================
    # Test 2: Timeline generation
    # ========================================================


    print("\nEVENT TIMELINE")
    print("-"*40)



    timeline = agent.create_timeline(
        memories
    )



    for item in timeline:


        print(
            f"{item['time']:.2f}s | "
            f"{item['event']} | "
            f"{item['frame']}"
        )







    print("\n")
    print("="*60)

    print(
        " TEMPORAL REASONING COMPLETE "
    )

    print("="*60)






if __name__=="__main__":

    main()