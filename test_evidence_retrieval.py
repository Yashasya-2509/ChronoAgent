import json
from pathlib import Path

from app.evidence.evidence_retriever import (
    EvidenceRetriever
)


MEMORY_FOLDER = Path("data/memory")


def get_latest_memory_file():

    files = list(
        MEMORY_FOLDER.glob(
            "*_event_memory.json"
        )
    )

    if not files:
        raise FileNotFoundError(
            "No event memory files found."
        )

    return max(
        files,
        key=lambda file:
        file.stat().st_mtime
    )


def main():

    print()
    print("=" * 60)
    print(" CHRONOAGENT - EVIDENCE RETRIEVAL ")
    print("=" * 60)

    memory_file = get_latest_memory_file()

    video_id = (
        memory_file.stem
        .replace(
            "_event_memory",
            ""
        )
    )

    print("\nVideo ID:")
    print(video_id)

    with open(
        memory_file,
        "r"
    ) as file:

        data = json.load(file)

    memories = data["memories"]

    # Use the first memory as test evidence
    reasoning_result = memories[0]

    retriever = EvidenceRetriever()

    evidence = retriever.get_evidence(
        video_id,
        reasoning_result
    )

    print("\nEvidence:")
    print("-" * 40)

    for key, value in evidence.items():

        print(
            f"{key}: {value}"
        )

    print()
    print("=" * 60)
    print(" EVIDENCE RETRIEVAL COMPLETE ")
    print("=" * 60)


if __name__ == "__main__":
    main()