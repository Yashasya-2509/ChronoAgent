import json
from pathlib import Path


from app.vector_memory.vector_store import VectorStore



video_id = "VID_dad243f7"


memory_path = Path(
    f"data/memory/{video_id}_event_memory.json"
)



print("="*60)
print(" CHRONOAGENT CHROMA INDEXING ")
print("="*60)



if not memory_path.exists():

    raise FileNotFoundError(
        memory_path
    )



with open(memory_path) as f:

    data=json.load(f)



memories=data["memories"]



print(
    "Memories found:",
    len(memories)
)



vector_store = VectorStore()



vector_store.add_memories(
    memories
)



print()

print(
    "INDEXING COMPLETE"
)

print("="*60)