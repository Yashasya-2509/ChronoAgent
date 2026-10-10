import json
from pathlib import Path
from datetime import datetime

import networkx as nx


class KnowledgeGraphBuilder:
    """
    ChronoAgent Multi-Type Temporal Knowledge Graph.

    Node types:
        VIDEO
        SCENE
        PERSON
        OBJECT
        LOCATION
        EVENT
        TIME

    Main relationships:
        CONTAINS
        PERFORMS
        TARGET
        OCCURS_AT
        IN_SCENE
        LOCATED_AT
        BEFORE
        AFTER
    """

    def __init__(self):
        print("[KG] Knowledge Graph Builder initialized")
        self.graph = nx.MultiDiGraph()

    # =========================================================
    # NORMALIZATION
    # =========================================================

    @staticmethod
    def normalize_class_name(class_name):
        if not class_name:
            return "UNKNOWN"

        name = str(class_name).strip().upper()

        replacements = {
            "CELL PHONE": "PHONE",
            "MOBILE PHONE": "PHONE",
            "PEOPLE": "PERSON",
            "MAN": "PERSON",
            "WOMAN": "PERSON",
        }

        return replacements.get(
            name,
            name.replace(" ", "_")
        )

    @classmethod
    def make_entity_id(cls, class_name, track_id):
        normalized = cls.normalize_class_name(class_name)

        if track_id is None:
            return normalized

        try:
            return f"{normalized}_{int(track_id):03d}"
        except (TypeError, ValueError):
            return f"{normalized}_{track_id}"

    @staticmethod
    def make_time_id(timestamp):
        try:
            value = float(timestamp)
            return f"TIME_{value:.3f}".replace(".", "_")
        except (TypeError, ValueError):
            return f"TIME_{timestamp}"

    # =========================================================
    # GENERIC NODE
    # =========================================================

    def add_node(self, node_id, node_type, **attributes):

        if not node_id:
            return

        attributes["type"] = node_type

        if self.graph.has_node(node_id):
            self.graph.nodes[node_id].update(attributes)
        else:
            self.graph.add_node(
                node_id,
                **attributes
            )

    # =========================================================
    # VIDEO
    # =========================================================

    def add_video(self, video_id):

        self.add_node(
            video_id,
            "VIDEO",
            video_id=video_id
        )

    # =========================================================
    # SCENE
    # =========================================================

    def add_scene(
        self,
        scene_id,
        video_id=None,
        start_time=None,
        end_time=None
    ):

        self.add_node(
            scene_id,
            "SCENE",
            scene_id=scene_id,
            video_id=video_id,
            start_time=start_time,
            end_time=end_time
        )

        if video_id and self.graph.has_node(video_id):

            self.add_edge(
                video_id,
                scene_id,
                "CONTAINS"
            )

    # =========================================================
    # PERSON / OBJECT
    # =========================================================

    def add_entity(
        self,
        entity_id,
        class_name,
        track_id=None,
        first_seen=None,
        last_seen=None
    ):

        normalized = self.normalize_class_name(
            class_name
        )

        node_type = (
            "PERSON"
            if normalized == "PERSON"
            else "OBJECT"
        )

        self.add_node(
            entity_id,
            node_type,
            entity_id=entity_id,
            class_name=normalized,
            track_id=track_id,
            first_seen=first_seen,
            last_seen=last_seen
        )

    # =========================================================
    # EVENT
    # =========================================================

    def add_event(self, event):

        event_id = event.get("event_id")

        if not event_id:
            return None

        start_time = event.get(
            "start_time",
            event.get("timestamp", 0)
        )

        end_time = event.get(
            "end_time",
            start_time
        )

        self.add_node(
            event_id,
            "EVENT",

            event_id=event_id,

            event_type=event.get(
                "event_type"
            ),

            action=event.get(
                "action"
            ),

            description=event.get(
                "description"
            ),

            start_time=start_time,

            end_time=end_time,

            duration=self._duration(
                start_time,
                end_time
            ),

            start_frame=event.get(
                "start_frame"
            ),

            end_frame=event.get(
                "end_frame"
            ),

            confidence=event.get(
                "confidence"
            ),

            video_id=event.get(
                "video_id"
            )
        )

        return event_id

    # =========================================================
    # TIME
    # =========================================================

    def add_time_node(self, timestamp):

        time_id = self.make_time_id(
            timestamp
        )

        self.add_node(
            time_id,
            "TIME",
            timestamp=timestamp
        )

        return time_id

    # =========================================================
    # LOCATION
    # =========================================================

    def add_location(
        self,
        location_id,
        location_name=None
    ):

        self.add_node(
            location_id,
            "LOCATION",
            location_id=location_id,
            name=location_name or location_id
        )

    # =========================================================
    # EDGE
    # =========================================================

    def add_edge(
        self,
        source,
        target,
        relation,
        **attributes
    ):

        if not source or not target:
            return

        if not self.graph.has_node(source):
            return

        if not self.graph.has_node(target):
            return

        # Avoid duplicate identical relationships.
        for _, existing_target, data in self.graph.out_edges(
            source,
            data=True
        ):

            if (
                existing_target == target
                and data.get("relation") == relation
            ):
                return

        self.graph.add_edge(
            source,
            target,
            relation=relation,
            **attributes
        )

    # =========================================================
    # EVENT → SUBJECT
    # =========================================================

    def connect_event_subject(
        self,
        event,
        event_id
    ):
        """
        Connect the entity performing the event.

        Example:

            PERSON_017
                |
                | PERFORMS
                v
               E003
        """

        class_name = (
            event.get("subject_class")
            or event.get("class_name")
            or event.get("object")
            or "UNKNOWN"
        )

        track_id = (
            event.get("subject_track_id")
            if event.get("subject_track_id") is not None
            else event.get("track_id")
        )

        if track_id is None:
            return None

        entity_id = self.make_entity_id(
            class_name,
            track_id
        )

        if not self.graph.has_node(entity_id):

            self.add_entity(
                entity_id,
                class_name,
                track_id,
                event.get("start_time"),
                event.get("end_time")
            )

        else:

            node = self.graph.nodes[
                entity_id
            ]

            current_start = event.get(
                "start_time"
            )

            current_end = event.get(
                "end_time"
            )

            first_seen = node.get(
                "first_seen"
            )

            last_seen = node.get(
                "last_seen"
            )

            if current_start is not None:

                if (
                    first_seen is None
                    or current_start < first_seen
                ):
                    node["first_seen"] = (
                        current_start
                    )

            if current_end is not None:

                if (
                    last_seen is None
                    or current_end > last_seen
                ):
                    node["last_seen"] = (
                        current_end
                    )

        # Subject performs event.
        self.add_edge(
            entity_id,
            event_id,
            "PERFORMS"
        )

        # Video contains subject.
        video_id = event.get(
            "video_id"
        )

        if (
            video_id
            and self.graph.has_node(video_id)
        ):

            self.add_edge(
                video_id,
                entity_id,
                "CONTAINS"
            )

        return entity_id

    # =========================================================
    # EVENT → TARGET
    # =========================================================

    def connect_semantic_target(
        self,
        event,
        event_id
    ):
        """
        Connect an event to its target object.

        Example:

            E003
              |
              | TARGET
              v
            BACKPACK_003
        """

        target_id = (
            event.get("target_id")
            or event.get("object_id")
        )

        target_class = event.get(
            "target_class"
        )

        target_track_id = event.get(
            "target_track_id"
        )

        if not target_id and target_class:

            target_id = self.make_entity_id(
                target_class,
                target_track_id
            )

        if not target_id:
            return None

        if not self.graph.has_node(
            target_id
        ):

            self.add_entity(
                target_id,
                target_class or "UNKNOWN",
                target_track_id
            )

        # Event targets object.
        self.add_edge(
            event_id,
            target_id,
            "TARGET"
        )

        # If the event belongs to a video,
        # the video also contains the target.
        video_id = event.get(
            "video_id"
        )

        if (
            video_id
            and self.graph.has_node(video_id)
        ):

            self.add_edge(
                video_id,
                target_id,
                "CONTAINS"
            )

        return target_id

    # =========================================================
    # EVENT → TIME
    # =========================================================

    def connect_event_time(
        self,
        event,
        event_id
    ):

        timestamp = event.get(
            "start_time",
            event.get("timestamp")
        )

        if timestamp is None:
            return

        time_id = self.add_time_node(
            timestamp
        )

        self.add_edge(
            event_id,
            time_id,
            "OCCURS_AT"
        )

    # =========================================================
    # EVENT → SCENE
    # =========================================================

    def connect_event_scene(
        self,
        event,
        event_id
    ):

        scene_id = (
            event.get("scene_id")
            or event.get("scene")
        )

        if not scene_id:
            return

        if not self.graph.has_node(
            scene_id
        ):

            self.add_scene(
                scene_id,
                event.get("video_id")
            )

        self.add_edge(
            event_id,
            scene_id,
            "IN_SCENE"
        )

    # =========================================================
    # EVENT → LOCATION
    # =========================================================

    def connect_event_location(
        self,
        event,
        event_id
    ):

        location_id = (
            event.get("location_id")
            or event.get("location")
        )

        if not location_id:
            return

        if not self.graph.has_node(
            location_id
        ):

            self.add_location(
                location_id
            )

        self.add_edge(
            event_id,
            location_id,
            "LOCATED_AT"
        )

    # =========================================================
    # TEMPORAL RELATIONSHIPS
    # =========================================================

    def add_temporal_edges(self):

        event_nodes = []

        for node_id, data in self.graph.nodes(
            data=True
        ):

            if data.get("type") != "EVENT":
                continue

            timestamp = data.get(
                "start_time",
                0
            )

            try:

                timestamp = float(
                    timestamp
                )

            except (
                TypeError,
                ValueError
            ):

                timestamp = 0.0

            event_nodes.append(
                (
                    node_id,
                    timestamp
                )
            )

        event_nodes.sort(
            key=lambda x: x[1]
        )

        # Consecutive events.
        for index in range(
            len(event_nodes) - 1
        ):

            current_id = (
                event_nodes[index][0]
            )

            current_time = (
                event_nodes[index][1]
            )

            next_id = (
                event_nodes[index + 1][0]
            )

            next_time = (
                event_nodes[index + 1][1]
            )

            if current_time <= next_time:

                self.add_edge(
                    current_id,
                    next_id,
                    "BEFORE"
                )

        # Reverse AFTER edges.
        before_edges = []

        for source, target, data in self.graph.edges(
            data=True
        ):

            if data.get(
                "relation"
            ) == "BEFORE":

                before_edges.append(
                    (
                        source,
                        target
                    )
                )

        for source, target in before_edges:

            self.add_edge(
                target,
                source,
                "AFTER"
            )

    # =========================================================
    # BUILD GRAPH
    # =========================================================

    def build_graph(
        self,
        events,
        output_path
    ):

        self.graph = nx.MultiDiGraph()

        print(
            "[GRAPH] Creating multi-type knowledge graph..."
        )

        if not events:

            print(
                "[GRAPH] No events received."
            )

            self.save(
                output_path
            )

            return output_path

        # -----------------------------------------------------
        # VIDEO NODES
        # -----------------------------------------------------

        video_ids = {
            event.get("video_id")
            for event in events
            if event.get("video_id")
        }

        for video_id in video_ids:

            self.add_video(
                video_id
            )

        # -----------------------------------------------------
        # EVENTS
        # -----------------------------------------------------

        for event in events:

            event_id = self.add_event(
                event
            )

            if not event_id:
                continue

            # Subject performing event.
            self.connect_event_subject(
                event,
                event_id
            )

            # Target object.
            self.connect_semantic_target(
                event,
                event_id
            )

            # Time.
            self.connect_event_time(
                event,
                event_id
            )

            # Scene.
            self.connect_event_scene(
                event,
                event_id
            )

            # Location.
            self.connect_event_location(
                event,
                event_id
            )

        # -----------------------------------------------------
        # TEMPORAL GRAPH
        # -----------------------------------------------------

        self.add_temporal_edges()

        # -----------------------------------------------------
        # SAVE
        # -----------------------------------------------------

        self.save(
            output_path
        )

        self.print_statistics()

        return output_path

    # =========================================================
    # SAVE
    # =========================================================

    def save(
        self,
        path
    ):

        path = Path(
            path
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        graph_data = {

            "metadata": {

                "created_at":
                    datetime.now().isoformat(),

                "graph_type":
                    "ChronoAgent Multi-Type Temporal Knowledge Graph",

                "node_count":
                    self.graph.number_of_nodes(),

                "edge_count":
                    self.graph.number_of_edges()
            },

            "nodes": [

                {
                    "id": node_id,
                    **data
                }

                for node_id, data
                in self.graph.nodes(
                    data=True
                )
            ],

            "edges": [

                {
                    "source": source,
                    "target": target,
                    **data
                }

                for source, target, data
                in self.graph.edges(
                    data=True
                )
            ]
        }

        with open(
            path,
            "w"
        ) as file:

            json.dump(
                graph_data,
                file,
                indent=2,
                default=str
            )

        print(
            f"[GRAPH] Saved: {path}"
        )

    # =========================================================
    # STATISTICS
    # =========================================================

    def print_statistics(self):

        node_counts = {}

        for _, data in self.graph.nodes(
            data=True
        ):

            node_type = data.get(
                "type",
                "UNKNOWN"
            )

            node_counts[node_type] = (
                node_counts.get(
                    node_type,
                    0
                ) + 1
            )

        edge_counts = {}

        for _, _, data in self.graph.edges(
            data=True
        ):

            relation = data.get(
                "relation",
                "UNKNOWN"
            )

            edge_counts[relation] = (
                edge_counts.get(
                    relation,
                    0
                ) + 1
            )

        print()
        print("=" * 60)
        print("CHRONOAGENT KNOWLEDGE GRAPH")
        print("=" * 60)

        print(
            f"Total Nodes : "
            f"{self.graph.number_of_nodes()}"
        )

        print(
            f"Total Edges : "
            f"{self.graph.number_of_edges()}"
        )

        print()
        print("NODE TYPES")

        for node_type, count in sorted(
            node_counts.items()
        ):

            print(
                f"  {node_type:<12} : {count}"
            )

        print()
        print("RELATION TYPES")

        for relation, count in sorted(
            edge_counts.items()
        ):

            print(
                f"  {relation:<15} : {count}"
            )

        print("=" * 60)

    # =========================================================
    # UTILITY
    # =========================================================

    @staticmethod
    def _duration(
        start_time,
        end_time
    ):

        try:

            return round(
                max(
                    0.0,
                    float(end_time)
                    - float(start_time)
                ),
                3
            )

        except (
            TypeError,
            ValueError
        ):

            return 0.0