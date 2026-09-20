from pathlib import Path
import json
import time


from app.video_processing.video_ingestion import VideoIngestion
from app.video_processing.frame_processor import FrameProcessor
from app.video_processing.keyframe_selector import KeyframeSelector
from app.video_processing.manifest_manager import ManifestManager


from app.object_detection.yolo_detector import YOLODetector
from app.tracking.object_tracker import ObjectTracker


from app.event_detection.event_detector import EventDetector


from app.memory.event_memory import EventMemory


from app.knowledge_graph.knowledge_graph_builder import KnowledgeGraphBuilder


from app.vector_memory.embedding_manager import EmbeddingManager
from app.vector_memory.vector_store import VectorStore


from app.config import (
    FRAME_FOLDER,
    MANIFEST_FOLDER
)



class ChronoPipeline:


    def __init__(self):


        print("[INIT] Loading ChronoAgent modules...")


        self.ingestion = VideoIngestion()



        self.frame_processor = FrameProcessor(
            sample_fps=2.0,
            scene_threshold=27.0,
            min_scene_len=15
        )


        self.keyframe_selector = KeyframeSelector(
            max_keyframes_per_scene=3
        )


        self.manifest_manager = ManifestManager(
            MANIFEST_FOLDER
        )



        self.detector = YOLODetector(
            model_name="yolo11n.pt"
        )


        self.tracker = ObjectTracker(
            model_name="yolo11n.pt"
        )



        self.event_detector = EventDetector()


        self.memory = EventMemory()


        self.graph_builder = KnowledgeGraphBuilder()


        self.embedding = EmbeddingManager()


        self.vector_store = VectorStore()



        print("[INIT] ChronoAgent ready")




    def run(self, video_path):


        start_time=time.time()


        print("\n")
        print("="*60)
        print(" CHRONOAGENT FULL PIPELINE ")
        print("="*60)


        print(
            "VIDEO:",
            video_path
        )



        try:


            # =============================
            # VIDEO INGESTION
            # =============================


            print("\n[1] VIDEO INGESTION")


            metadata = self.ingestion.ingest(
                video_path
            )


            video_id = metadata["video_id"]


            print(
                "VIDEO ID:",
                video_id
            )



            # =============================
            # FRAME EXTRACTION
            # =============================


            print("\n[2] FRAME PROCESSING")


            frame_dir = (
                FRAME_FOLDER /
                video_id
            )


            frame_dir.mkdir(
                parents=True,
                exist_ok=True
            )


            frames = self.frame_processor.extract_frames(
                video_path,
                frame_dir,
                video_id
            )


            print(
                "Frames:",
                len(frames)
            )



            # =============================
            # SCENE DETECTION
            # =============================


            print("\n[3] SCENE DETECTION")


            scenes = self.frame_processor.detect_scenes(
                video_path
            )


            print(
                "Scenes:",
                len(scenes)
            )



            # =============================
            # KEYFRAMES
            # =============================


            print("\n[4] KEYFRAMES")


            keyframes = (
                self.keyframe_selector
                .select_keyframes(
                    frames,
                    scenes
                )
            )


            print(
                "Keyframes:",
                len(keyframes)
            )



            # =============================
            # OBJECT DETECTION
            # =============================


            print("\n[5] OBJECT DETECTION")


            detections = (
                self.detector.detect_frames(
                    frames,
                    video_id
                )
            )


            print(
                "Detections:",
                len(detections)
            )



            # =============================
            # TRACKING
            # =============================


            print("\n[6] OBJECT TRACKING")


            tracks = (
                self.tracker.track(
                    video_path,
                    detections,
                    video_id
                )
            )


            print(
                "Tracks:",
                len(tracks)
            )



            # =============================
            # EVENT DETECTION
            # =============================


            print("\n[7] EVENT DETECTION")


            events = (
                self.event_detector.detect(
                    tracks
                )
            )


            print(
                "Events:",
                len(events)
            )



            # =============================
            # EVENT MEMORY
            # =============================


            print("\n[8] EVENT MEMORY")


            memories = (
                self.memory.add_events(
                    events
                )
            )


            memory_folder = Path(
                "data/memory"
            )


            memory_folder.mkdir(
                parents=True,
                exist_ok=True
            )



            memory_path = (
                memory_folder /
                f"{video_id}_event_memory.json"
            )



            self.memory.save(
                memory_path
            )



            print(
                "Memory:",
                memory_path
            )



            # =============================
            # KNOWLEDGE GRAPH
            # =============================


            print("\n[9] KNOWLEDGE GRAPH")


            graph_folder = Path(
                "data/graphs"
            )


            graph_folder.mkdir(
                parents=True,
                exist_ok=True
            )


            graph_path = (
                graph_folder /
                f"{video_id}_graph.json"
            )



            self.graph_builder.build_graph(
                events,
                graph_path
            )


            print(
                "Graph:",
                graph_path
            )



            # =============================
            # VECTOR MEMORY
            # =============================


            print("\n[10] VECTOR MEMORY")


            texts = [

                m["description"]

                for m in memories

            ]



            embeddings = (
                self.embedding
                .encode_batch(
                    texts
                )
            )



            self.vector_store.add_memories(
                memories,
                embeddings
            )



            print(
                "Vector memory updated"
            )



            duration = (
                time.time()
                -
                start_time
            )



            result = {


                "video_id":
                    video_id,


                "video":
                    str(video_path),


                "frames":
                    len(frames),


                "detections":
                    len(detections),


                "tracks":
                    len(tracks),


                "events":
                    len(events),


                "memory":
                    str(memory_path),


                "graph":
                    str(graph_path),


                "processing_time":
                    duration

            }



            # save result

            Path(
                "data/evaluation"
            ).mkdir(
                parents=True,
                exist_ok=True
            )


            with open(
                "data/evaluation/pipeline_results.json",
                "a"
            ) as f:

                f.write(
                    json.dumps(result)
                    +
                    "\n"
                )



            print("\n")
            print("="*60)
            print(" PIPELINE COMPLETE ")
            print("="*60)



            return result



        except Exception as e:


            print("\nPIPELINE FAILED")

            print(e)


            return {


                "video":
                    str(video_path),


                "status":
                    "FAILED",


                "error":
                    str(e)

            }