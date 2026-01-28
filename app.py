import os
import streamlit as st
import numpy as np
import cv2
import mediapipe as mp
from moviepy.editor import VideoFileClip
import yt_dlp

# ===============================
# STREAMLIT CONFIG
# ===============================
st.set_page_config(
    page_title="AutoClip AI",
    page_icon="🎬",
    layout="centered"
)

# ===============================
# FOLDER SETUP
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===============================
# MEDIA PIPE FACE DETECTOR
# ===============================
mp_face = mp.solutions.face_detection
face_detector = mp_face.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.6
)

# ===============================
# UTILS
# ===============================
def download_video_from_url(url, output_dir):
    ydl_opts = {
        "outtmpl": os.path.join(output_dir, "input.%(ext)s"),
        "format": "mp4/best",
        "quiet": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def get_face_center(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_detector.process(rgb)
    if not results.detections:
        return None
    bbox = results.detections[0].location_data.relative_bounding_box
    h, w, _ = frame.shape
    cx = int((bbox.xmin + bbox.width / 2) * w)
    cy = int((bbox.ymin + bbox.height / 2) * h)
    return cx, cy

def auto_crop_9_16(frame):
    h, w, _ = frame.shape
    target_w = int(h * 9 / 16)

    center = get_face_center(frame)
    if center:
        cx, _ = center
    else:
        cx = w // 2

    x1 = max(0, cx - target_w // 2)
    x2 = min(w, x1 + target_w)
    return frame[:, x1:x2]

# ===============================
# UI
# ===============================
st.title("🎬 AutoClip AI")
st.caption("Shorts / Reels / TikTok Generator")

st.subheader("📥 Sumber Video")
source_type = st.radio(
    "Pilih sumber:",
    ["Upload File", "Video dari Link"]
)

uploaded_file = None
video_url = None

if source_type == "Upload File":
    uploaded_file = st.file_uploader(
        "📤 Upload video",
        type=["mp4", "mov", "mkv"]
    )
else:
    video_url = st.text_input(
        "🔗 Link YouTube / TikTok",
        placeholder="https://www.youtube.com/..."
    )

st.subheader("🎬 Mode Output")
mode = st.selectbox(
    "Pilih format:",
    ["Shorts (9:16)", "Reels (9:16)", "TikTok (9:16)"]
)

filename = st.text_input(
    "📝 Nama file output",
    value="autoclip_result"
)

process_btn = st.button("🚀 Proses Video")

# ===============================
# PROCESS
# ===============================
if process_btn:
    if source_type == "Upload File" and not uploaded_file:
        st.warning("⚠️ Upload video dulu")
        st.stop()

    if source_type == "Video dari Link" and not video_url:
        st.warning("⚠️ Masukkan link video")
        st.stop()

    with st.spinner("📥 Menyiapkan video..."):
        if uploaded_file:
            input_path = os.path.join(OUTPUT_DIR, uploaded_file.name)
            with open(input_path, "wb") as f:
                f.write(uploaded_file.read())
        else:
            input_path = download_video_from_url(video_url, OUTPUT_DIR)

    with st.spinner("🔍 Memproses video..."):
        clip = VideoFileClip(input_path)

        # 🔐 DURASI LIMIT (WAJIB UNTUK HF)
        if clip.duration > 180:
            st.error("❌ Video terlalu panjang (maks 3 menit)")
            st.stop()

        fps = clip.fps
        frames = []

        for t in np.arange(0, clip.duration, 1 / fps * 10):
            frame = clip.get_frame(t)
            cropped = auto_crop_9_16(frame)
            frames.append(cropped)

        h, w, _ = frames[0].shape
        out_path = os.path.join(OUTPUT_DIR, f"{filename}.mp4")

        out = cv2.VideoWriter(
            out_path,
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (w, h)
        )

        for f in frames:
            out.write(f)

        out.release()

    st.success("✅ Video berhasil diproses!")

    with open(out_path, "rb") as f:
        st.download_button(
            "⬇️ Download Video",
            data=f,
            file_name=f"{filename}.mp4",
            mime="video/mp4"
        )

st.divider()
st.caption("AutoClip AI | CPU-safe Hugging Face Space 🚀")
