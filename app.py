# ===============================
# AutoClip AI - Streamlit App
# FINAL (Colab Safe)
# ===============================

import os
import uuid
import subprocess
from pathlib import Path

# ---- WAJIB DI PALING ATAS (anti crash Colab) ----
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import streamlit as st

# ===============================
# CONFIG
# ===============================
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="AutoClip AI",
    layout="centered"
)

# ===============================
# UI HEADER
# ===============================
st.title("🎬 AutoClip AI")
st.caption("Auto crop 9:16 + Karaoke Subtitle (Phase 1)")
st.success("Streamlit berhasil dimuat")

# ===============================
# LAZY IMPORT (AMAN COLAB)
# ===============================
def get_face_detector():
    import mediapipe as mp
    return mp.solutions.face_detection.FaceDetection(
        model_selection=0,
        min_detection_confidence=0.5
    )

# ===============================
# VIDEO PROCESSING
# ===============================
def render_video(video_path, output_path):
    """
    Phase 1:
    - crop center
    - scale 9:16
    """
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-vf", "crop=in_h*9/16:in_h,scale=1080:1920",
        "-preset", "veryfast",
        "-movflags", "+faststart",
        str(output_path)
    ]
    subprocess.run(cmd, check=True)

# ===============================
# STREAMLIT UI
# ===============================
uploaded_file = st.file_uploader(
    "📤 Upload video (MP4)",
    type=["mp4"]
)

filename_option = st.radio(
    "Nama file output",
    [
        "Otomatis (UUID)",
        "Gunakan nama asli + _short"
    ]
)

if uploaded_file:
    video_id = str(uuid.uuid4())[:8]

    input_path = UPLOAD_DIR / f"{video_id}_{uploaded_file.name}"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    st.video(str(input_path))
    st.info("Video berhasil diupload")

    if st.button("🚀 Proses Video"):
        with st.spinner("Rendering video..."):
            if filename_option.startswith("Gunakan"):
                out_name = input_path.stem + "_short.mp4"
            else:
                out_name = f"autoclip_{video_id}.mp4"

            output_path = OUTPUT_DIR / out_name

            try:
                render_video(input_path, output_path)
                st.success("Render selesai!")

                st.video(str(output_path))

                with open(output_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Video",
                        f,
                        file_name=out_name,
                        mime="video/mp4"
                    )

            except Exception as e:
                st.error("Terjadi error saat rendering")
                st.exception(e)

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.caption("AutoClip AI • Phase 1 • Built with Streamlit")
