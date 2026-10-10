from pathlib import Path

from app.knowledge_graph.knowledge_graph_builder import (
    KnowledgeGraphBuilder
)


def main():

    events = [

        # -------------------------------------------------
        # EVENT 1
        # Person enters
        # -------------------------------------------------

        {
            "event_id": "E001",
            "video_id": "VID_TEST001",

            "event_type": "OBJECT_ENTER",

            "class_name": "person",
            "track_id": 17,

            "start_time": 10.2,
            "end_time": 10.2,

            "start_frame": 255,
            "end_frame": 255,

            "confidence": 0.91,

            "description":
                "Person entered the scene."
        },

        # -------------------------------------------------
        # EVENT 2
        # Person moves
        # -------------------------------------------------

        {
            "event_id": "E002",
            "video_id": "VID_TEST001",

            "event_type": "OBJECT_MOVEMENT",

            "class_name": "person",
            "track_id": 17,

            "start_time": 15.7,
            "end_time": 18.4,

            "start_frame": 392,
            "end_frame": 460,

            "confidence": 0.88,

            "description":
                "Person moved through the scene."
        },

        # -------------------------------------------------
        # EVENT 3
        # Person picks up backpack
        # -------------------------------------------------

        {
            "event_id": "E003",
            "video_id": "VID_TEST001",

            "event_type": "PICKED_UP",

            # Subject
            "class_name": "person",
            "track_id": 17,

            # Target
            "target_class": "backpack",
            "target_track_id": 3,

            "start_time": 21.4,
            "end_time": 21.4,

            "start_frame": 535,
            "end_frame": 535,

            "confidence": 0.86,

            "description":
                "Person picked up the backpack."
        }

    ]

    output_path = Path(
        "data/graphs/test_knowledge_graph.json"
    )

    builder = KnowledgeGraphBuilder()

    builder.build_graph(
        events,
        output_path
    )

    print()
    print("TEST COMPLETE")
    print(
        "Graph file:",
        output_path
    )


if __name__ == "__main__":
    main()