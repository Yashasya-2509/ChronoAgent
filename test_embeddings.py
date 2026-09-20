from app.vector_memory.embedding_manager import (
    EmbeddingManager
)


def main():

    print("\n")
    print("=" * 60)
    print(" CHRONOAGENT - EMBEDDING TEST ")
    print("=" * 60)

    manager = EmbeddingManager()

    text = (
        "A person appeared in the CCTV scene."
    )

    embedding = manager.encode(text)

    print("\nInput:")
    print(text)

    print("\nEmbedding type:")
    print(type(embedding))

    print("\nEmbedding dimension:")
    print(len(embedding))

    print("\nFirst 10 values:")
    print(embedding[:10])

    print("\n")
    print("=" * 60)
    print(" EMBEDDING TEST COMPLETE ")
    print("=" * 60)


if __name__ == "__main__":
    main()