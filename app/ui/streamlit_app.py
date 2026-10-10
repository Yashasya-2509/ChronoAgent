from pathlib import Path
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from app.query.query_engine import QueryEngine
from app.pipeline.chrono_pipeline import ChronoPipeline

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="ChronoAgent | CCTV Intelligence",
    page_icon="C",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = PROJECT_ROOT / "data"
VIDEO_DIR = DATA_DIR / "videos"
MEMORY_DIR = DATA_DIR / "memory"
GRAPH_DIR = DATA_DIR / "graphs"


def load_json(path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def indexed_videos():
    videos = []
    for memory_path in sorted(MEMORY_DIR.glob("*_event_memory.json")):
        video_id = memory_path.name.removesuffix("_event_memory.json")
        graph_path = GRAPH_DIR / f"{video_id}_graph.json"
        video_paths = list(VIDEO_DIR.glob(f"{video_id}.*"))
        video_path = video_paths[0] if video_paths else None
        if graph_path.exists() and video_path and video_path.exists():
            memory = load_json(memory_path)
            videos.append({
                "id": video_id,
                "path": video_path,
                "events": memory.get("memories", []),
            })
    return videos


st.markdown(
    """
    <style>
    .block-container { max-width: 1200px; padding-top: 3rem; }
    [data-testid="stMetricValue"] { color: #0f766e; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("ChronoAgent")
st.caption("CCTV video understanding, event memory, and evidence retrieval")

videos = indexed_videos()
video_by_id = {video["id"]: video for video in videos}

with st.sidebar:
    st.header("Video workspace")
    uploaded_video = st.file_uploader(
        "Preview a CCTV video",
        type=["mp4", "avi", "mov", "mkv", "webm"],
    )

    if uploaded_video:
        upload_dir = DATA_DIR / "videos" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        uploaded_path = upload_dir / uploaded_video.name
        uploaded_path.write_bytes(uploaded_video.getvalue())
        st.video(str(uploaded_path))
        if st.button("Process uploaded video", type="primary", use_container_width=True):
            try:
                with st.spinner("Processing video, detecting events, and building memory..."):
                    metadata = ChronoPipeline().run(str(uploaded_path))
                st.success(f"Processing complete: {metadata}")
                st.rerun()
            except Exception as error:
                st.error(f"Video processing failed: {error}")

    if not videos:
        st.warning("No indexed videos are available yet.")
        if not uploaded_video:
            st.stop()
        st.info("Process the uploaded video above, then select it here.")
        st.stop()

    if not video_by_id:
        st.info("No completed video index is available yet. Process an upload above.")
        st.stop()

    selected_id = st.selectbox(
        "Indexed video",
        options=list(video_by_id),
        format_func=lambda video_id: video_id,
    )

selected_video = video_by_id[selected_id]
st.video(str(selected_video["path"]))

event_types = sorted({event.get("event_type", "Unknown") for event in selected_video["events"]})
metric_columns = st.columns(3)
metric_columns[0].metric("Indexed events", len(selected_video["events"]))
metric_columns[1].metric("Event types", len(event_types))
metric_columns[2].metric("Video ID", selected_id)

st.divider()
st.subheader("Ask about this video")
question = st.text_input(
    "Question",
    placeholder="Who appeared first? How many cars appeared?",
)

if st.button("Analyze", type="primary", use_container_width=True):
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        with st.spinner("Searching event memory and evidence..."):
            try:
                result = QueryEngine(selected_id).answer(question.strip())
            except Exception as error:
                st.error(f"Could not analyze this video: {error}")
            else:
                answer = result.get("answer", {})
                if isinstance(answer, dict):
                    st.success(answer.get("answer", "No answer generated."))
                    answer_columns = st.columns(3)
                    answer_columns[0].metric("Timestamp", f"{answer.get('timestamp', 0):.2f}s")
                    answer_columns[1].metric("Evidence frame", answer.get("evidence_frame") or "None")
                    answer_columns[2].metric("Confidence", f"{answer.get('confidence', 0):.0%}")
                else:
                    st.info(str(answer))

                evidence = result.get("evidence") or {}
                evidence_path = evidence.get("frame_path")
                if evidence_path and Path(evidence_path).exists():
                    st.subheader("Evidence")
                    st.image(evidence_path, caption=f"Frame {evidence.get('frame_id')}")

                with st.expander("Retrieval details"):
                    st.json(result.get("retrieval", {}))