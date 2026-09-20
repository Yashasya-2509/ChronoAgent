from pathlib import Path
import json

from app.vector_memory.embedding_manager import (
    EmbeddingManager
)

from app.vector_memory.vector_store import (
    VectorStore
)


VIDEO_ID = "VID_91bbf259"

MEMORY_FILE = (
    Path("data/memory")
    / f"{VIDEO_ID}_event_memory.json"
)


def main():

    print("\n")
    print("=" * 60)
    print(" CHRONOAGENT - VECTOR SEMANTIC MEMORY ")
    print("=" * 60)

    # -------------------------------------------------
    # LOAD EVENT MEMORY
    # -------------------------------------------------

    with open(MEMORY_FILE) as file:

        data = json.load(file)

    memories = data["memories"]

    print(
        f"\nMemories loaded: "
        f"{len(memories)}"
    )

    # -------------------------------------------------
    # EMBEDDING MODEL
    # -------------------------------------------------

    embedding_manager = (
        EmbeddingManager()
    )

    descriptions = [
        memory["description"]
        for memory in memories
    ]

    embeddings = (
        embedding_manager.encode_batch(
            descriptions
        )
    )

    print(
        f"Embeddings created: "
        f"{len(embeddings)}"
    )

    print(
        f"Embedding dimension: "
        f"{len(embeddings[0])}"
    )

    # -------------------------------------------------
    # VECTOR STORE
    # -------------------------------------------------

    vector_store = VectorStore()

    stored = vector_store.add_memories(
        memories,
        embeddings
    )

    print(
        f"\nMemories stored: "
        f"{stored}"
    )

    print(
        f"Vector database count: "
        f"{vector_store.count()}"
    )

    # -------------------------------------------------
    # SEMANTIC SEARCH
    # -------------------------------------------------

    query = (
        "When did a person appear?"
    )

    print(
        f"\nSearch query:"
    )

    print(query)

    query_embedding = (
        embedding_manager.encode(
            query
        )
    )

    results = vector_store.search(
        query_embedding,
        top_k=3
    )

    print("\nSearch results:")

    for i, memory_id in enumerate(
        results["ids"][0]
    ):

        document = (
            results["documents"][0][i]
        )

        distance = (
            results["distances"][0][i]
        )

        print(
            f"\nResult {i + 1}"
        )

        print(
            f"Memory ID: {memory_id}"
        )

        print(
            f"Description: {document}"
        )

        print(
            f"Distance: {distance:.4f}"
        )

    print("\n")
    print("=" * 60)
    print(" VECTOR SEMANTIC MEMORY COMPLETE ")
    print("=" * 60)


if __name__ == "__main__":
    main()