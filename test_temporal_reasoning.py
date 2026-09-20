import json

from app.reasoning.temporal_reasoner import TemporalReasoner



VIDEO_ID="VID_91bbf259"


MEMORY_PATH=(
    f"data/memory/"
    f"{VIDEO_ID}_event_memory.json"
)



def main():

    print("\n")
    print("="*60)
    print(" CHRONOAGENT TEMPORAL REASONING ")
    print("="*60)



    with open(
        MEMORY_PATH,
        "r"
    ) as file:

        data=json.load(file)


    memories=data["memories"]


    print(
        "Memories loaded:",
        len(memories)
    )


    agent=TemporalReasoner()



    print("\nFIRST PERSON APPEARANCE")
    print("-"*40)


    result=agent.find_first_event(
        memories,
        "person"
    )


    print(
        result
    )



    print("\nEVENT TIMELINE")
    print("-"*40)


    timeline=agent.create_timeline(
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