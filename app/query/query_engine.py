import json
from pathlib import Path

from app.retrieval.hybrid_retriever import HybridRetriever
from app.reasoning.temporal_reasoner import TemporalReasoner
from app.agent.answer_generator import AnswerGenerator
from app.evidence.evidence_retriever import EvidenceRetriever
from app.query.query_classifier import QueryClassifier


class QueryEngine:

    def __init__(
        self,
        video_id
    ):

        self.video_id = video_id

        # ==============================
        # PATHS
        # ==============================

        self.memory_path = (
            Path("data/memory")
            /
            f"{video_id}_event_memory.json"
        )

        self.graph_path = (
            Path("data/graphs")
            /
            f"{video_id}_graph.json"
        )

        if not self.memory_path.exists():

            raise FileNotFoundError(
                f"Memory missing: {self.memory_path}"
            )

        if not self.graph_path.exists():

            raise FileNotFoundError(
                f"Graph missing: {self.graph_path}"
            )

        # ==============================
        # LOAD MEMORY
        # ==============================

        with open(
            self.memory_path,
            "r"
        ) as f:

            data = json.load(f)

        self.memories = data.get(
            "memories",
            []
        )

        # ==============================
        # COMPONENTS
        # ==============================

        self.retriever = HybridRetriever(
            str(self.graph_path),
            self.video_id
        )

        self.reasoner = TemporalReasoner()

        self.generator = AnswerGenerator()

        self.evidence_retriever = EvidenceRetriever()

        self.classifier = QueryClassifier()

    # =====================================================
    # OBJECT DETECTION
    # =====================================================

    def detect_object_name(
        self,
        query
    ):

        query = query.lower()

        objects = set()

        for memory in self.memories:

            name = memory.get(
                "class_name"
            )

            if name:

                objects.add(
                    name.lower()
                )

        for obj in objects:

            if obj in query:

                return obj

        return None

    # =====================================================
    # GET APPEARANCE EVENTS
    # =====================================================

    def get_appearance_events(
        self,
        object_name=None
    ):

        events = []

        for event in self.memories:

            if event.get(
                "event_type"
            ) not in [

                "OBJECT_APPEARED",

                "OBJECT_ENTER"

            ]:

                continue

            if object_name:

                if (
                    event.get(
                        "class_name"
                    ) != object_name
                ):

                    continue

            events.append(
                event
            )

        return events

    # =====================================================
    # NORMALIZE EVENT
    # =====================================================

    def normalize_event(
        self,
        event
    ):

        if event is None:

            return {

                "description":
                    "No matching event found.",

                "start_time":
                    0,

                "end_time":
                    0,

                "start_frame":
                    "",

                "confidence":
                    0.0

            }

        # Timeline / temporal result
        # should be preserved as-is.
        if (
            "timeline" in event
            or
            "related_events" in event
        ):

            return event

        start_time = event.get(
            "start_time",
            event.get(
                "timestamp",
                0
            )
        )

        end_time = event.get(
            "end_time",
            start_time
        )

        return {

            "description":
                event.get(
                    "description",
                    "Unknown event"
                ),

            "event_id":
                event.get(
                    "event_id"
                ),

            "event_type":
                event.get(
                    "event_type"
                ),

            "class_name":
                event.get(
                    "class_name"
                ),

            "track_id":
                event.get(
                    "track_id"
                ),

            "start_time":
                start_time,

            "end_time":
                end_time,

            "timestamp":
                start_time,

            "start_frame":
                event.get(
                    "start_frame",
                    ""
                ),

            "end_frame":
                event.get(
                    "end_frame",
                    ""
                ),

            "confidence":
                event.get(
                    "confidence",
                    1.0
                )

        }

    # =====================================================
    # TEMPORAL INTENT CHECK
    # =====================================================

    def is_temporal_intent(
        self,
        intent_name
    ):

        return intent_name in {

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

            "LAST_EVENT"

        }

    # =====================================================
    # RETRIEVAL BUDGET
    # =====================================================

    def retrieval_budget(
        self,
        intent_name,
        query
    ):

        # ==========================================
        # TEMPORAL QUERIES
        # ==========================================

        if self.is_temporal_intent(
            intent_name
        ):

            return {

                "vector_top_k": 0,

                "graph_top_k": 0

            }

        # ==========================================
        # TIMELINE
        # ==========================================

        if intent_name == "TIMELINE":

            return {

                "vector_top_k": 10,

                "graph_top_k": 30

            }

        # ==========================================
        # FIRST / LAST
        # ==========================================

        if intent_name in {

            "FIRST_EVENT",

            "LAST_EVENT"

        }:

            return {

                "vector_top_k": 0,

                "graph_top_k": 0

            }

        # ==========================================
        # OBJECT COUNT / APPEARANCE
        # ==========================================

        if intent_name in {

            "COUNT_OBJECT",

            "OBJECT_APPEARANCE_TIME"

        }:

            return {

                "vector_top_k": 10,

                "graph_top_k": 10

            }

        # ==========================================
        # GENERAL QUERY
        # ==========================================

        return {

            "vector_top_k": 5,

            "graph_top_k": 10

        }

    # =====================================================
    # TEMPORAL TARGET EXTRACTION
    # =====================================================

    def extract_temporal_target(
        self,
        query
    ):
        """
        Extract the semantic event/action target from
        a temporal natural-language query.

        Examples:

        "What happened before the person entered?"
            -> "entered"

        "What happened after the person left?"
            -> "left"

        "What happened during the person's movement?"
            -> "moved"

        "What happened during the person moving?"
            -> "moved"

        "What happened during the person's motion?"
            -> "moved"

        The method returns semantic keywords rather
        than hard-coded event IDs.
        """

        if not query:

            return None

        query_lower = (
            query
            .lower()
            .strip()
        )

        # =================================================
        # NORMALIZE POSSESSIVES
        # =================================================
        #
        # Examples:
        #
        # person's movement
        # person's entry
        # person's exit
        #
        # become:
        #
        # person movement
        # person entry
        # person exit
        # =================================================

        query_lower = (
            query_lower
            .replace("'s ", " ")
            .replace("’s ", " ")
        )

        # =================================================
        # HIGH-CONFIDENCE ACTION PHRASES
        # =================================================

        phrases = [

            # ---------------------------------------------
            # PICK UP
            # ---------------------------------------------

            "picked up the bag",

            "picked up the backpack",

            "picked up the laptop",

            "picked up the phone",

            "picked up",

            # ---------------------------------------------
            # ENTER
            # ---------------------------------------------

            "entered the room",

            "entered",

            "entering",

            "entry",

            # ---------------------------------------------
            # EXIT
            # ---------------------------------------------

            "left the room",

            "left",

            "leaving",

            "exited the room",

            "exited",

            "exiting",

            "exit",

            # ---------------------------------------------
            # OTHER ACTIONS
            # ---------------------------------------------

            "sat down",

            "stood up",

            "arrived",

            "appeared",

            # ---------------------------------------------
            # MOVEMENT
            # ---------------------------------------------

            "moved",

            "movement",

            "moving",

            "motion",

            # ---------------------------------------------
            # STATE
            # ---------------------------------------------

            "stationary"

        ]

        # =================================================
        # EXACT / HIGH-CONFIDENCE PHRASE MATCH
        # =================================================

        for phrase in phrases:

            if phrase in query_lower:

                # -----------------------------------------
                # Movement normalization
                # -----------------------------------------

                if phrase in {

                    "movement",

                    "moving",

                    "motion"

                }:

                    return "moved"

                # -----------------------------------------
                # Entry normalization
                # -----------------------------------------

                if phrase in {

                    "entering",

                    "entry"

                }:

                    return "entered"

                # -----------------------------------------
                # Exit normalization
                # -----------------------------------------

                if phrase in {

                    "leaving",

                    "exiting",

                    "exit"

                }:

                    return "left"

                return phrase

        # =================================================
        # CLEAN GENERIC TEMPORAL QUERY
        # =================================================

        cleaned = query_lower

        temporal_words = [

            "what happened",

            "what happens",

            "what occurred",

            "what occurs",

            "which event",

            "which events",

            "before",

            "after",

            "during",

            "while",

            "following",

            "prior to",

            "earlier than",

            "later than",

            "overlap",

            "overlapped",

            "overlapping",

            "meets",

            "meet",

            "starts",

            "started",

            "ends",

            "ended",

            "next",

            "immediately",

            "directly",

            "the event",

            "the person",

            "person",

            "object",

            "event",

            "who",

            "which"

        ]

        for word in temporal_words:

            cleaned = cleaned.replace(
                word,
                " "
            )

        cleaned = " ".join(
            cleaned.split()
        ).strip()

        # =================================================
        # SEMANTIC NORMALIZATION
        # =================================================

        semantic_aliases = {

            # Movement
            "movement": "moved",

            "moving": "moved",

            "motion": "moved",

            # Entry
            "entering": "entered",

            "entry": "entered",

            # Exit
            "leaving": "left",

            "exit": "left",

            "exiting": "left",

            # Arrival
            "arrival": "arrived",

            # Appearance
            "appearing": "appeared",

            # Sitting / standing
            "sitting": "sat down",

            "standing": "stood up"

        }

        for source, target in semantic_aliases.items():

            if source in cleaned:

                return target

        # =================================================
        # EMPTY RESULT
        # =================================================

        if not cleaned:

            return None

        return cleaned

    # =====================================================
    # BUILD TEMPORAL RESULT
    # =====================================================

    def build_temporal_result(
        self,
        description,
        events,
        confidence=1.0,
        **extra_fields
    ):

        result = {

            "description":
                description,

            "event_type":
                "TEMPORAL_RESULT",

            "timeline":
                events,

            "related_events":
                events,

            "confidence":
                confidence

        }

        result.update(
            extra_fields
        )

        return result

    # =====================================================
    # FIND TARGET EVENT
    # =====================================================

    def find_temporal_target(
        self,
        query
    ):

        keyword = (
            self.extract_temporal_target(
                query
            )
        )

        if not keyword:

            return None

        return (
            self.reasoner.find_target_event(
                self.memories,
                keyword
            )
        )

    # =====================================================
    # MAIN ANSWER
    # =====================================================

    def answer(
        self,
        query
    ):

        print(
            "\n[QUERY]",
            query
        )

        # =================================================
        # CLASSIFY QUERY
        # =================================================

        intent = self.classifier.classify(
            query
        )

        print(
            "[INTENT]",
            intent
        )

        intent_name = intent[
            "intent"
        ]

        # =================================================
        # RETRIEVAL BUDGET
        # =================================================

        budget = self.retrieval_budget(

            intent_name,

            query

        )

        # =================================================
        # VIDEO AWARE RETRIEVAL
        # =================================================
        #
        # Temporal reasoning is deterministic and should
        # operate directly on event memory.
        #
        # Therefore vector / graph retrieval is skipped
        # for temporal queries.
        # =================================================

        if self.is_temporal_intent(
            intent_name
        ):

            retrieval_results = {

                "vector_results": [],

                "graph_results": [],

                "retrieval_mode":
                    "TEMPORAL"

            }

        else:

            retrieval_results = (
                self.retriever.retrieve(

                    query=query,

                    video_id=self.video_id,

                    vector_top_k=
                        budget[
                            "vector_top_k"
                        ],

                    graph_top_k=
                        budget[
                            "graph_top_k"
                        ]

                )
            )

        # =================================================
        # INITIAL STATE
        # =================================================

        reasoning_result = None

        object_name = (
            self.detect_object_name(
                query
            )
        )

        # =================================================
        # FIRST EVENT
        # =================================================

        if intent_name == "FIRST_EVENT":

            events = (
                self.get_appearance_events(
                    object_name
                )
            )

            # If no explicit object was found,
            # default to persons.
            if not object_name:

                reasoning_result = (
                    self.reasoner.find_first_event(
                        events,
                        object_type="person"
                    )
                )

            else:

                reasoning_result = (
                    self.reasoner.find_first_event(
                        events,
                        object_type=object_name
                    )
                )

        # =================================================
        # LAST EVENT
        # =================================================

        elif intent_name == "LAST_EVENT":

            events = (
                self.get_appearance_events(
                    object_name
                )
            )

            if not object_name:

                reasoning_result = (
                    self.reasoner.find_last_event(
                        events,
                        object_type="person"
                    )
                )

            else:

                reasoning_result = (
                    self.reasoner.find_last_event(
                        events,
                        object_type=object_name
                    )
                )

        # =================================================
        # TIMELINE
        # =================================================

        elif intent_name == "TIMELINE":

            timeline = (
                self.reasoner.create_timeline(
                    self.memories
                )
            )

            reasoning_result = {

                "timeline":
                    timeline,

                "description":
                    "Complete event timeline",

                "confidence":
                    1.0

            }

        # =================================================
        # COUNT OBJECT
        # =================================================

        elif intent_name == "COUNT_OBJECT":

            events = (
                self.get_appearance_events(
                    object_name
                )
            )

            tracks = set()

            for event in events:

                track = event.get(
                    "track_id"
                )

                if track:

                    tracks.add(
                        track
                    )

            reasoning_result = {

                "description":

                    f"{len(tracks)} "
                    f"{object_name or 'objects'} "
                    f"appeared.",

                "confidence":
                    1.0

            }

        # =================================================
        # BEFORE EVENT
        # =================================================

        elif intent_name == "BEFORE_EVENT":

            keyword = (
                self.extract_temporal_target(
                    query
                )
            )

            related_events = (
                self.reasoner.before_event(

                    self.memories,

                    keyword

                )
            )

            reasoning_result = (
                self.build_temporal_result(

                    f"Events before "
                    f"{keyword or 'the target event'}.",

                    related_events,

                    1.0
                    if related_events
                    else 0.0

                )
            )

        # =================================================
        # AFTER EVENT
        # =================================================

        elif intent_name == "AFTER_EVENT":

            keyword = (
                self.extract_temporal_target(
                    query
                )
            )

            related_events = (
                self.reasoner.after_event(

                    self.memories,

                    keyword

                )
            )

            reasoning_result = (
                self.build_temporal_result(

                    f"Events after "
                    f"{keyword or 'the target event'}.",

                    related_events,

                    1.0
                    if related_events
                    else 0.0

                )
            )

        # =================================================
        # DURING EVENT
        # =================================================

        elif intent_name == "DURING_EVENT":

            target = (
                self.find_temporal_target(
                    query
                )
            )

            if target:

                related_events = (
                    self.reasoner.find_related_events(

                        self.memories,

                        target,

                        "DURING"

                    )
                )

                reasoning_result = (
                    self.build_temporal_result(

                        "Events occurring during "
                        f"{target.get('description', 'the target event')}.",

                        related_events,

                        1.0
                        if related_events
                        else 0.0

                    )
                )

        # =================================================
        # OVERLAPS EVENT
        # =================================================

        elif intent_name == "OVERLAPS_EVENT":

            target = (
                self.find_temporal_target(
                    query
                )
            )

            if target:

                related_events = (
                    self.reasoner.find_related_events(

                        self.memories,

                        target,

                        "OVERLAPS"

                    )
                )

                reasoning_result = (
                    self.build_temporal_result(

                        "Events overlapping "
                        f"{target.get('description', 'the target event')}.",

                        related_events,

                        1.0
                        if related_events
                        else 0.0

                    )
                )

        # =================================================
        # MEETS EVENT
        # =================================================

        elif intent_name == "MEETS_EVENT":

            target = (
                self.find_temporal_target(
                    query
                )
            )

            if target:

                related_events = (
                    self.reasoner.find_related_events(

                        self.memories,

                        target,

                        "MEETS"

                    )
                )

                reasoning_result = (
                    self.build_temporal_result(

                        "Events meeting "
                        f"{target.get('description', 'the target event')}.",

                        related_events,

                        1.0
                        if related_events
                        else 0.0

                    )
                )

        # =================================================
        # STARTS EVENT
        # =================================================

        elif intent_name == "STARTS_EVENT":

            target = (
                self.find_temporal_target(
                    query
                )
            )

            if target:

                related_events = (
                    self.reasoner.find_related_events(

                        self.memories,

                        target,

                        "STARTS"

                    )
                )

                reasoning_result = (
                    self.build_temporal_result(

                        "Events starting with "
                        f"{target.get('description', 'the target event')}.",

                        related_events,

                        1.0
                        if related_events
                        else 0.0

                    )
                )

        # =================================================
        # ENDS EVENT
        # =================================================

        elif intent_name == "ENDS_EVENT":

            target = (
                self.find_temporal_target(
                    query
                )
            )

            if target:

                related_events = (
                    self.reasoner.find_related_events(

                        self.memories,

                        target,

                        "ENDS"

                    )
                )

                reasoning_result = (
                    self.build_temporal_result(

                        "Events ending with "
                        f"{target.get('description', 'the target event')}.",

                        related_events,

                        1.0
                        if related_events
                        else 0.0

                    )
                )

        # =================================================
        # FOLLOWS EVENT
        # =================================================

        elif intent_name == "FOLLOWS_EVENT":

            target = (
                self.find_temporal_target(
                    query
                )
            )

            if target:

                next_event = (
                    self.reasoner.follows_event(

                        self.memories,

                        target

                    )
                )

                if next_event:

                    reasoning_result = {

                        "description":
                            next_event[
                                "description"
                            ],

                        "event_id":
                            next_event[
                                "event_id"
                            ],

                        "event_type":
                            next_event[
                                "event_type"
                            ],

                        "class_name":
                            next_event[
                                "class_name"
                            ],

                        "track_id":
                            next_event[
                                "track_id"
                            ],

                        "start_time":
                            next_event[
                                "start_time"
                            ],

                        "end_time":
                            next_event[
                                "end_time"
                            ],

                        "start_frame":
                            next_event[
                                "start_frame"
                            ],

                        "confidence":
                            next_event.get(
                                "confidence",
                                1.0
                            )

                    }

        # =================================================
        # TIME RANGE
        # =================================================

        elif intent_name == "TIME_RANGE":

            time_range = (
                self.reasoner.parse_time_range(
                    query
                )
            )

            if time_range:

                start_time, end_time = (
                    time_range
                )

                events = (
                    self.reasoner.events_in_time_range(

                        self.memories,

                        start_time,

                        end_time

                    )
                )

                reasoning_result = {

                    "description":
                        (
                            f"Events between "
                            f"{start_time}s and "
                            f"{end_time}s."
                        ),

                    "event_type":
                        "TIME_RANGE",

                    "start_time":
                        start_time,

                    "end_time":
                        end_time,

                    "timeline":
                        events,

                    "related_events":
                        events,

                    "confidence":
                        1.0
                        if events
                        else 0.0

                }

        # =================================================
        # GENERAL QUERY
        # =================================================

        else:

            results = (
                retrieval_results.get(
                    "vector_results",
                    []
                )
            )

            if results:

                best_id = results[0].get(
                    "memory_id"
                )

                for memory in self.memories:

                    if (
                        memory.get(
                            "memory_id"
                        )
                        ==
                        best_id
                    ):

                        reasoning_result = (
                            memory
                        )

                        break

        # =================================================
        # FALLBACK
        # =================================================

        if reasoning_result is None:

            reasoning_result = {

                "description":
                    "No matching event found.",

                "confidence":
                    0.0

            }

        # =================================================
        # NORMALIZE RESULT
        # =================================================

        reasoning_result = (
            self.normalize_event(
                reasoning_result
            )
        )

        # =================================================
        # GENERATE ANSWER
        # =================================================

        answer = self.generator.generate(

            query,

            reasoning_result

        )

        # =================================================
        # EVIDENCE
        # =================================================

        evidence = (
            self.evidence_retriever.get_evidence(

                self.video_id,

                reasoning_result

            )
        )

        # =================================================
        # FINAL RESPONSE
        # =================================================

        return {

            "video_id":
                self.video_id,

            "query":
                query,

            "intent":
                intent,

            "retrieval":
                retrieval_results,

            "answer":
                answer,

            "evidence":
                evidence

        }