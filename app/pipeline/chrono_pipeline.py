from pathlib import Path
import time
import os


# ===========================
# VIDEO MODULES
# ===========================

from app.video_processing.video_ingestion import VideoIngestion
from app.video_processing.frame_processor import FrameProcessor
from app.video_processing.scene_detector import SceneDetector
from app.video_processing.keyframe_selector import KeyframeSelector
from app.video_processing.manifest_manager import ManifestManager


# ===========================
# AI MODULES
# ===========================

from app.object_detection.yolo_detector import YOLODetector
from app.tracking.object_tracker import ObjectTracker

from app.event_detection.event_detector import EventDetector

from app.memory.event_memory import EventMemory

from app.knowledge_graph.knowledge_graph_builder import KnowledgeGraphBuilder

from app.vector_memory.embedding_manager import EmbeddingManager
from app.vector_memory.vector_store import VectorStore

from app.vision_language.vlm_analyzer import VLMAnalyzer


# ===========================
# QUERY ENGINE
# ===========================

from app.query.query_engine import QueryEngine


from app.config import (
    FRAME_FOLDER,
    MANIFEST_FOLDER
)


class ChronoPipeline:

    def __init__(self):

        print("[INIT] Loading ChronoAgent modules...")

        # ===========================
        # VIDEO PIPELINE
        # ===========================

        self.ingestion = VideoIngestion()

        self.scene_detector = SceneDetector()

        self.frame_processor = FrameProcessor(
            sample_fps=2.0,
            scene_threshold=27.0,
            min_scene_len=15,
            max_frames_per_scene=20,
            max_total_frames=300
        )

        self.keyframe_selector = KeyframeSelector(
            max_keyframes_per_scene=8
        )

        self.manifest_manager = ManifestManager(
            MANIFEST_FOLDER
        )

        # ===========================
        # OBJECT DETECTION
        # ===========================

        self.detector = YOLODetector(
            model_name="yolo11n.pt"
        )

        # ===========================
        # OBJECT TRACKING
        # ===========================

        self.tracker = ObjectTracker(
            model_name="yolo11n.pt"
        )

        # ===========================
        # EVENT DETECTION
        # ===========================

        self.event_detector = EventDetector()

        # ===========================
        # VISION-LANGUAGE ANALYZER
        # ===========================

        self.vlm = VLMAnalyzer(
            mode=os.getenv(
                "CHRONO_VLM_MODE",
                "yolo"
            ),
            model_name="yolo11n.pt",
            confidence=0.25,
        )

        # ===========================
        # EVENT MEMORY
        # ===========================

        self.memory = EventMemory()

        # ===========================
        # KNOWLEDGE GRAPH
        # ===========================

        self.graph_builder = KnowledgeGraphBuilder()

        # ===========================
        # VECTOR MEMORY
        # ===========================

        self.embedding = EmbeddingManager()

        self.vector_store = VectorStore()

        # ===========================
        # QUERY MEMORY
        # ===========================

        self.query_engines = {}

        print("[INIT] ChronoAgent ready")

    # =====================================================
    # VIDEO PROCESSING PIPELINE
    # =====================================================

    def run(self, video_path):

        start_time = time.time()

        print("\n")
        print("=" * 60)
        print(" CHRONOAGENT FULL PIPELINE ")
        print("=" * 60)

        print(
            "VIDEO:",
            video_path
        )

        try:

            # =================================================
            # 1. VIDEO INGESTION
            # =================================================

            print("\n[1] VIDEO INGESTION")

            metadata = self.ingestion.ingest(
                video_path
            )

            video_id = metadata["video_id"]

            print(
                "VIDEO ID:",
                video_id
            )

            # =================================================
            # 2. SCENE DETECTION
            # =================================================

            print("\n[2] SCENE DETECTION")

            scenes = self.scene_detector.detect_scenes(
                video_path
            )

            print(
                "Scenes:",
                len(scenes)
            )

            # =================================================
            # 3. FRAME EXTRACTION
            # =================================================

            print("\n[3] FRAME EXTRACTION")

            frame_dir = FRAME_FOLDER / video_id

            frame_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            frames = self.frame_processor.extract_frames(
                video_path,
                scenes,
                frame_dir
            )

            print(
                "Frames:",
                len(frames)
            )

            # =================================================
            # 4. KEYFRAME SELECTION
            # =================================================

            print("\n[4] KEYFRAME SELECTION")

            keyframes = self.keyframe_selector.select_keyframes(
                frames,
                scenes
            )

            print(
                "Keyframes:",
                len(keyframes)
            )

            # =================================================
            # 5. VLM ANALYSIS
            # =================================================

            print("\n[5] VLM")

            vlm_results = self.vlm.analyze_frames(
                keyframes
            )

            print(
                "VLM:",
                len(vlm_results)
            )

            # =================================================
            # 6. OBJECT DETECTION
            # =================================================

            print("\n[6] OBJECT DETECTION")

            detections = self.detector.detect_frames(
                keyframes,
                video_id
            )

            print(
                "Detections:",
                len(detections)
            )

            # =================================================
            # 7. OBJECT TRACKING
            # =================================================

            print("\n[7] TRACKING")

            tracks = self.tracker.track(
                video_path,
                detections,
                video_id,
                self.frame_processor.sample_fps
            )

            print(
                "Tracks:",
                len(tracks)
            )

            # =================================================
            # 8. EVENT DETECTION
            # =================================================

            print("\n[8] EVENT DETECTION")

            # IMPORTANT:
            # Pass video_id and VLM results into EventDetector.
            #
            # The EventDetector now creates canonical fields:
            #
            # subject_id
            # subject_class
            # subject_track_id
            #
            # and also preserves the existing fields.
            #
            # VLM results are passed through for
            # SCENE_DESCRIPTION events.

            events = self.event_detector.detect(
                tracks,
                video_id,
                vlm_results
            )

            print(
                "Events:",
                len(events)
            )

            # =================================================
            # 9. EVENT MEMORY
            # =================================================

            print("\n[9] MEMORY")

            memories = self.memory.add_events(
                events
            )

            memory_folder = Path(
                "data/memory"
            )

            memory_folder.mkdir(
                parents=True,
                exist_ok=True
            )

            memory_path = memory_folder / (
                f"{video_id}_event_memory.json"
            )

            self.memory.save(
                memory_path
            )

            print(
                "Memory:",
                memory_path
            )

            # =================================================
            # 10. KNOWLEDGE GRAPH
            # =================================================

            print("\n[10] KNOWLEDGE GRAPH")

            graph_folder = Path(
                "data/graphs"
            )

            graph_folder.mkdir(
                parents=True,
                exist_ok=True
            )

            graph_path = graph_folder / (
                f"{video_id}_graph.json"
            )

            # Same event list goes directly into
            # the multi-type Knowledge Graph.
            self.graph_builder.build_graph(
                events,
                graph_path
            )

            print(
                "Graph:",
                graph_path
            )

            # =================================================
            # 11. VECTOR MEMORY
            # =================================================

            print("\n[11] VECTOR MEMORY")

            if memories:

                texts = [
                    memory["description"]
                    for memory in memories
                ]

                embeddings = self.embedding.encode_batch(
                    texts
                )

                self.vector_store.add_memories(
                    memories,
                    embeddings
                )

            print(
                "Vector memory updated"
            )

            # =================================================
            # PIPELINE COMPLETE
            # =================================================

            elapsed_time = time.time() - start_time

            print("\n")
            print("=" * 60)
            print(" PIPELINE COMPLETE ")
            print("=" * 60)

            print(
                f"Processing time: {elapsed_time:.2f}s"
            )

            return {

                "video_id":
                    video_id,

                "events":
                    len(events),

                "memory":
                    str(memory_path),

                "graph":
                    str(graph_path),

                "processing_time":
                    round(
                        elapsed_time,
                        2
                    ),

                "status":
                    "SUCCESS"
            }

        except Exception as e:

            elapsed_time = time.time() - start_time

            print(
                "PIPELINE FAILED:",
                e
            )

            return {

                "status":
                    "FAILED",

                "error":
                    str(e),

                "processing_time":
                    round(
                        elapsed_time,
                        2
                    )
            }

    # =====================================================
    # QUERY SYSTEM
    # =====================================================

    def ask(
        self,
        question,
        video_id=None
    ):

        try:

            # =================================================
            # AUTO FIND VIDEO
            # =================================================

            if video_id is None:

                memories = list(
                    Path(
                        "data/memory"
                    ).glob(
                        "*_event_memory.json"
                    )
                )

                if not memories:

                    return {
                        "error":
                            "No processed video memory found"
                    }

                latest = max(
                    memories,
                    key=lambda x:
                    x.stat().st_mtime
                )

                video_id = latest.stem.replace(
                    "_event_memory",
                    ""
                )

            print(
                "[QUERY] Video:",
                video_id
            )

            # =================================================
            # CREATE QUERY ENGINE
            # =================================================

            if video_id not in self.query_engines:

                self.query_engines[video_id] = QueryEngine(
                    video_id
                )

            engine = self.query_engines[
                video_id
            ]

            # =================================================
            # ANSWER QUESTION
            # =================================================

            return engine.answer(
                question
            )

        except Exception as e:

            return {
                "error":
                    str(e)
            }


# =========================================================
# COMMAND LINE ENTRY POINT
# =========================================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:

        print(
            "Usage: python -m app.pipeline.chrono_pipeline <video>"
        )

        exit(1)

    pipeline = ChronoPipeline()

    result = pipeline.run(
        sys.argv[1]
    )

    print(result)