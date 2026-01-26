import os
import streamlit as st

# ===============================
# STREAMLIT BASIC CONFIG (WAJIB)
# ===============================
st.set_page_config(
    page_title="AutoClip AI",
    page_icon="🎬",
    layout="centered"
)

# ===============================
# SAFE IMPORTS (NO CRASH)
# ===============================
try:
    import cv2
    import mediapipe as mp
    import numpy as np
    from moviepy.editor import VideoFileClip
except Exception as e:
    st.error("❌ Gagal load library video")
    st.exception(e)
    st.stop()

# ===============================
# FOLDER SETUP
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===============================
# UI HEADER
# ===============================
st.title("🎬 AutoClip AI")
st.caption("Auto crop 9:16 + Subtitle (Phase 1)")

st.markdown(
    """
    **Fitur aktif (Phase 1):**
    - Upload video
    - Convert ke format Shorts / Reels
    - Pipeline siap untuk face crop & subtitle
    """
)

st.divider()

# ===============================
# INPUT SECTION
# ===============================
uploaded_file = st.file_uploader(
    "📤 Upload video",
    type=["mp4", "mov", "mkv"]
)

filename = st.text_input(
    "📝 Nama file output (tanpa .mp4)",
    value="autoclip_result"
)

process_btn = st.button("🚀 Proses Video")

# ===============================
# PROCESSING
# ===============================
if process_btn:
    if uploaded_file is None:
        st.warning("⚠️ Silakan upload video dulu")
        st.stop()

    with st.spinner("Memproses video..."):
        input_path = os.path.join(OUTPUT_DIR, uploaded_file.name)

        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())

        try:
            clip = VideoFileClip(input_path)

            # --- Phase 1: resize ke 9:16 ---
            clip_resized = clip.resize(height=1920)

            output_path = os.path.join(
                OUTPUT_DIR,
                f"{filename}.mp4"
            )

            clip_resized.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None
            )

        except Exception as e:
            st.error("❌ Gagal memproses video")
            st.exception(e)
            st.stop()

    st.success("✅ Video berhasil diproses!")

    # ===============================
    # DOWNLOAD
    # ===============================
    with open(output_path, "rb") as f:
        st.download_button(
            label="⬇️ Download Video",
            data=f,
            file_name=f"{filename}.mp4",
            mime="video/mp4"
        )

# ===============================
# FOOTER
# ===============================
st.divider()
st.caption("AutoClip AI – Phase 1 | Hugging Face Spaces Ready 🚀")
