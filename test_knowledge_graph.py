import json

from app.knowledge_graph.knowledge_graph_builder import (
    KnowledgeGraphBuilder
)



VIDEO_ID="VID_91bbf259"



EVENT_PATH = (
    "data/events/"
    f"{VIDEO_ID}_events.json"
)



OUTPUT = (
    "data/graphs/"
    f"{VIDEO_ID}_graph.json"
)



def main():


    print("\n")
    print("="*60)
    print(" CHRONOAGENT KNOWLEDGE GRAPH ")
    print("="*60)



    with open(EVENT_PATH) as f:

        data=json.load(f)


    events=data["events"]


    print(
        "Events loaded:",
        len(events)
    )



    graph=KnowledgeGraphBuilder()



    for event in events:

        graph.add_event(event)



    graph.add_temporal_edges()



    output=graph.save(
        OUTPUT
    )


    print(
        "Graph saved:",
        output
    )


    print(
        "Nodes:",
        graph.graph.number_of_nodes()
    )


    print(
        "Edges:",
        graph.graph.number_of_edges()
    )



if __name__=="__main__":

    main()