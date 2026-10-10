import json
from pathlib import Path

from app.query.query_engine import QueryEngine

VIDEO_ID = "VID_TEST_TEMPORAL"


# ============================================================
# CREATE SYNTHETIC EVENT
# ============================================================

def make_event(
    event_id,
    event_type,
    description,
    start,
    end,
    subject_id,
    track_id,
):
    return {
        "memory_id": f"M_{event_id}",
        "video_id": VIDEO_ID,
        "event_id": event_id,
        "event_type": event_type,
        "object_id": subject_id,
        "track_id": track_id,
        "class_name": "person",
        "start_time": start,
        "end_time": end,
        "duration": end - start,
        "start_frame": int(start * 25),
        "end_frame": int(end * 25),
        "description": description,
        "confidence": 0.95,
        "relations": {
            "before": [],
            "after": [],
            "overlaps": [],
        },
    }


# ============================================================
# CREATE SYNTHETIC EVENT MEMORY
# ============================================================

def create_synthetic_memory():

    events = [
        make_event(
            "E00001",
            "OBJECT_ENTER",
            "Person entered the room",
            5.0,
            8.0,
            "PERSON_001",
            1,
        ),
        make_event(
            "E00002",
            "OBJECT_MOVEMENT",
            "Person moved toward the table",
            9.0,
            14.0,
            "PERSON_001",
            1,
        ),
        make_event(
            "E00003",
            "OBJECT_MOVEMENT",
            "Person moved near the laptop",
            15.0,
            20.0,
            "PERSON_001",
            1,
        ),
        make_event(
            "E00004",
            "OBJECT_ENTER",
            "Second person entered the room",
            22.0,
            25.0,
            "PERSON_002",
            2,
        ),
        make_event(
            "E00005",
            "OBJECT_MOVEMENT",
            "Second person moved across the room",
            26.0,
            30.0,
            "PERSON_002",
            2,
        ),
        make_event(
            "E00006",
            "OBJECT_EXIT",
            "Person left the room",
            35.0,
            38.0,
            "PERSON_001",
            1,
        ),
        make_event(
            "E00007",
            "OBJECT_MOVEMENT",
            "Second person remained in the room",
            39.0,
            45.0,
            "PERSON_002",
            2,
        ),
    ]

    memory = {
        "total_memories": len(events),
        "memories": events,
    }

    memory_path = Path(
        f"data/memory/{VIDEO_ID}_event_memory.json"
    )

    memory_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        memory_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            memory,
            file,
            indent=4,
        )

    return memory_path


# ============================================================
# CREATE SYNTHETIC KNOWLEDGE GRAPH
# ============================================================

def create_synthetic_graph():

    graph = {
        "video_id": VIDEO_ID,
        "nodes": [],
        "edges": [],
        "stats": {
            "total_nodes": 0,
            "total_edges": 0,
        },
    }

    graph_path = Path(
        f"data/graphs/{VIDEO_ID}_graph.json"
    )

    graph_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        graph_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            graph,
            file,
            indent=4,
        )

    return graph_path


# ============================================================
# TEMPORAL INTENT TEST
# ============================================================

def test_temporal_intents(engine):

    print()
    print("=" * 70)
    print("TEMPORAL INTENT DETECTION")
    print("=" * 70)

    temporal_queries = [
        (
            "What happened before the person left?",
            "BEFORE_EVENT",
        ),
        (
            "What happened after the person entered?",
            "AFTER_EVENT",
        ),
        (
            "What happened during the person's movement?",
            "DURING_EVENT",
        ),
        (
            "What happened between 20 and 40 seconds?",
            "TIME_RANGE",
        ),
        (
            "Who entered first?",
            "FIRST_EVENT",
        ),
    ]

    for query, expected in temporal_queries:

        result = engine.classifier.classify(
            query
        )

        if isinstance(result, dict):
            intent = result.get("intent")
        else:
            intent = result

        print()
        print("Query    :", query)
        print("Expected :", expected)
        print("Detected :", intent)

        assert intent == expected, (
            f"Expected {expected}, "
            f"but detected {intent}"
        )

    print()
    print("PASS: Temporal intent detection")


# ============================================================
# RETRIEVAL BYPASS TEST
# ============================================================

def test_temporal_retrieval_bypass(engine):

    print()
    print("=" * 70)
    print("TEMPORAL RETRIEVAL BYPASS")
    print("=" * 70)

    temporal_queries = [
        (
            "BEFORE_EVENT",
            "What happened before the person left?",
        ),
        (
            "AFTER_EVENT",
            "What happened after the person entered?",
        ),
        (
            "DURING_EVENT",
            "What happened during the person's movement?",
        ),
        (
            "OVERLAPS_EVENT",
            "What events overlapped with the person's movement?",
        ),
        (
            "MEETS_EVENT",
            "What event meets the person's movement?",
        ),
        (
            "STARTS_EVENT",
            "Which event started with the person's movement?",
        ),
        (
            "ENDS_EVENT",
            "Which event ended with the person's movement?",
        ),
        (
            "FOLLOWS_EVENT",
            "What happened immediately following the person's movement?",
        ),
        (
            "TIME_RANGE",
            "What happened between 20 and 40 seconds?",
        ),
        (
            "FIRST_EVENT",
            "Who entered first?",
        ),
        (
            "LAST_EVENT",
            "Who entered last?",
        ),
    ]

    for intent_name, query in temporal_queries:

        budget = engine.retrieval_budget(
            intent_name,
            query,
        )

        print()
        print("Intent :", intent_name)
        print("Query  :", query)
        print("Budget :", budget)

        assert budget["vector_top_k"] == 0, (
            f"Vector retrieval should be 0 "
            f"for {intent_name}"
        )

        assert budget["graph_top_k"] == 0, (
            f"Graph retrieval should be 0 "
            f"for {intent_name}"
        )

    print()
    print("PASS: Temporal retrieval bypass")


# ============================================================
# TEMPORAL INTENT CLASSIFICATION CHECK
# ============================================================

def test_is_temporal_intent(engine):

    print()
    print("=" * 70)
    print("TEMPORAL INTENT CHECK")
    print("=" * 70)

    temporal_intents = [
        "BEFORE_EVENT",
        "AFTER_EVENT",
        "DURING_EVENT",
        "OVERLAPS_EVENT",
        "MEETS_EVENT",
        "STARTS_EVENT",
        "ENDS_EVENT",
        "FOLLOWS_EVENT",
        "TIME_RANGE",
        "FIRST_EVENT",
        "LAST_EVENT",
    ]

    for intent_name in temporal_intents:

        assert engine.is_temporal_intent(
            intent_name
        ), (
            f"{intent_name} "
            f"should be temporal"
        )

    assert not engine.is_temporal_intent(
        "GENERAL_QUERY"
    )

    print(
        "PASS: is_temporal_intent()"
    )


# ============================================================
# EVENT MEMORY TEST
# ============================================================

def test_memory(engine):

    print()
    print("=" * 70)
    print("EVENT MEMORY")
    print("=" * 70)

    assert len(engine.memories) == 7, (
        f"Expected 7 events, "
        f"loaded {len(engine.memories)}"
    )

    print(
        "Loaded events:",
        len(engine.memories)
    )

    print(
        "PASS: Event memory loaded"
    )


# ============================================================
# VIDEO ID TEST
# ============================================================

def test_video_id(engine):

    print()
    print("=" * 70)
    print("VIDEO ID")
    print("=" * 70)

    assert engine.video_id == VIDEO_ID

    print(
        "Video ID:",
        engine.video_id
    )

    print(
        "PASS: Video ID"
    )


# ============================================================
# ACTUAL ANSWER TEST
# ============================================================

def test_actual_answers(engine):

    print()
    print("=" * 70)
    print("ACTUAL TEMPORAL ANSWERS")
    print("=" * 70)

    queries = [
        "What happened before the person left?",
        "What happened after the person entered?",
        "What happened during the person's movement?",
        "What happened between 20 and 40 seconds?",
        "Who entered first?",
        "Who entered last?",
    ]

    results = {}

    for query in queries:

        print()
        print("-" * 70)
        print("QUERY")
        print("-" * 70)

        print(query)

        result = engine.answer(
            query
        )

        results[query] = result

        print()
        print("-" * 70)
        print("RAW RESULT")
        print("-" * 70)

        print(
            json.dumps(
                result,
                indent=4,
                default=str,
            )
        )

        assert result is not None, (
            f"Query returned None: {query}"
        )

        assert isinstance(result, dict), (
            f"Expected dictionary result "
            f"for query: {query}"
        )

        assert "answer" in result, (
            f"Missing 'answer' field "
            f"for query: {query}"
        )

        assert "intent" in result, (
            f"Missing 'intent' field "
            f"for query: {query}"
        )

        assert "retrieval" in result, (
            f"Missing 'retrieval' field "
            f"for query: {query}"
        )

        print()
        print("PASS: Query returned valid result")

    return results


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("CHRONOAGENT — QUERY ENGINE TEMPORAL ANSWER TEST")
    print("=" * 70)

    # ========================================================
    # 1. CREATE SYNTHETIC DATA
    # ========================================================

    memory_path = create_synthetic_memory()
    graph_path = create_synthetic_graph()

    print()
    print("Synthetic memory created:")
    print(memory_path)

    print()
    print("Synthetic graph created:")
    print(graph_path)

    # ========================================================
    # 2. INITIALIZE QUERY ENGINE
    # ========================================================

    print()
    print("=" * 70)
    print("INITIALIZING QUERY ENGINE")
    print("=" * 70)

    engine = QueryEngine(
        video_id=VIDEO_ID
    )

    print()
    print("PASS: QueryEngine initialized")

    # ========================================================
    # 3. TEST TEMPORAL INTENTS
    # ========================================================

    test_temporal_intents(
        engine
    )

    # ========================================================
    # 4. TEST RETRIEVAL BYPASS
    # ========================================================

    test_temporal_retrieval_bypass(
        engine
    )

    # ========================================================
    # 5. TEST TEMPORAL INTENT FUNCTION
    # ========================================================

    test_is_temporal_intent(
        engine
    )

    # ========================================================
    # 6. TEST EVENT MEMORY
    # ========================================================

    test_memory(
        engine
    )

    # ========================================================
    # 7. TEST VIDEO ID
    # ========================================================

    test_video_id(
        engine
    )

    # ========================================================
    # 8. TEST ACTUAL ANSWERS
    # ========================================================

    test_actual_answers(
        engine
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print()
    print("=" * 70)
    print("QUERY ENGINE TEMPORAL ANSWER TEST COMPLETED")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()