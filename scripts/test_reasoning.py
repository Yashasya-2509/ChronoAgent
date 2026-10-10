import json

from app.reasoning.temporal_reasoner import TemporalReasoner



path="data/memory/VID_f6241814_event_memory.json"



with open(path) as f:

    memories=json.load(f)["memories"]



reasoner=TemporalReasoner()



print("\nFIRST PERSON")

print(
    reasoner.find_first_event(
        memories,
        "person"
    )
)



print("\nTIMELINE")

for x in reasoner.create_timeline(
    memories,
    10
):

    print(x)



print("\nBEFORE SUITCASE")

for x in reasoner.before_event(
    memories,
    "suitcase"
):

    print(
        x["description"]
    )