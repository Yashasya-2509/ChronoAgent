import json

from app.reasoning.temporal_reasoner import TemporalReasoner
from app.agent.answer_generator import AnswerGenerator



VIDEO_ID = "VID_91bbf259"


MEMORY_PATH = (
    f"data/memory/"
    f"{VIDEO_ID}_event_memory.json"
)



def main():

    print("\n")
    print("="*60)
    print(
        " CHRONOAGENT ANSWER AGENT "
    )
    print("="*60)



    with open(
        MEMORY_PATH,
        "r"
    ) as file:

        data=json.load(file)



    memories = data["memories"]



    query = (
        "Who appeared first?"
    )


    reasoner = TemporalReasoner()



    first_person = (
        reasoner.find_first_event(
            memories,
            "person"
        )
    )



    generator = AnswerGenerator()



    answer = generator.generate(
        query,
        first_person
    )



    print("\nFINAL ANSWER")
    print("-"*40)


    for key,value in answer.items():

        print(
            f"{key}: {value}"
        )


    print("\n")
    print("="*60)

    print(
        " ANSWER GENERATION COMPLETE "
    )

    print("="*60)



if __name__=="__main__":
    main()