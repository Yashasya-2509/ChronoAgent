from pathlib import Path
import json

from app.memory.event_memory import EventMemory


VIDEO_ID = "VID_91bbf259"


EVENT_FILE = (
    Path("data/events")
    / f"{VIDEO_ID}_events.json"
)


MEMORY_FILE = (
    Path("data/memory")
    / f"{VIDEO_ID}_event_memory.json"
)


def main():

    print("\n")
    print("=" * 60)
    print(" CHRONOAGENT - EVENT MEMORY ")
    print("=" * 60)

    # -------------------------------------------------
    # LOAD EVENTS
    # -------------------------------------------------

    with open(EVENT_FILE) as file:

        data = json.load(file)

    events = data["events"]

    print(
        f"\nEvents loaded: {len(events)}"
    )

    # -------------------------------------------------
    # CREATE MEMORY
    # -------------------------------------------------

    memory = EventMemory()

    memories = memory.add_events(
        events
    )

    print(
        f"Memories created: "
        f"{len(memories)}"
    )

    # -------------------------------------------------
    # SAVE
    # -------------------------------------------------

    output = memory.save(
        MEMORY_FILE
    )

    print(
        f"\nMemory file:"
    )

    print(output)

    # -------------------------------------------------
    # DISPLAY
    # -------------------------------------------------

    print("\nMemory entries:")

    for item in memories:

        print(
            f"\n{item['memory_id']} | "
            f"{item['event_type']} | "
            f"{item['class_name']} | "
            f"{item['start_time']:.2f}s"
        )

    print("\n")
    print("=" * 60)
    print(" EVENT MEMORY COMPLETE ")
    print("=" * 60)


if __name__ == "__main__":

    main()