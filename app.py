import os
import re
import uuid
from datetime import datetime

import streamlit as st
import requests
import yt_dlp

# ===============================
# CONFIG
# ===============================
st.set_page_config(
    page_title="AutoClip – Short Video Generator",
    layout="centered"
)

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===============================
# HELPER FUNCTIONS
# ===============================
def safe_filename(text, max_len=30):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '_', text.strip())
    return text[:max_len] if text else "clip"

def generate_filename(title, preset):
    title_safe = safe_filename(title)
    preset_safe = safe_filename(preset)
    uid = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{title_safe}_{preset_safe}_{timestamp}_{uid}.mp4"

def download_direct_video(url, output_path):
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

def download_youtube_video(url, output_path):
    ydl_opts = {
        "outtmpl": output_path,
        "format": "mp4/best",
        "quiet": True,
        "merge_output_format": "mp4"
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# ===============================
# UI
# ===============================
st.title("🎬 AutoClip")
st.caption("Short video generator ala 2short.ai (Colab Friendly)")

video_title = st.text_input(
    "Judul Video / Podcast",
    placeholder="Contoh: Podcast AI Paling Lucu"
)

preset_name = st.selectbox(
    "Preset Style",
    ["Funny", "Podcast", "Motivational", "Karaoke"]
)

source_type = st.radio(
    "Sumber Video",
    ["Upload File", "Link Video"]
)

uploaded_video = None
video_url = None

if source_type == "Upload File":
    uploaded_video = st.file_uploader(
        "Upload Video (MP4)",
        type=["mp4"]
    )
else:
    video_url = st.text_input(
        "Masukkan URL Video",
        placeholder="https://example.com/video.mp4 atau https://youtube.com/..."
    )
    st.caption("⚠️ YouTube hanya video publik & non-restricted")

render_btn = st.button("🚀 Render Video")

# ===============================
# RENDER PROCESS
# ===============================
if render_btn:
    if not video_title.strip():
        st.error("⚠️ Judul video wajib diisi")
        st.stop()

    input_path = os.path.join(OUTPUT_DIR, "input_temp.mp4")

    with st.spinner("Menyiapkan video..."):
        try:
            if source_type == "Upload File":
                if not uploaded_video:
                    st.error("⚠️ Upload video terlebih dahulu")
                    st.stop()

                with open(input_path, "wb") as f:
                    f.write(uploaded_video.read())

            else:
                if not video_url:
                    st.error("⚠️ URL video wajib diisi")
                    st.stop()

                if "youtube.com" in video_url or "youtu.be" in video_url:
                    download_youtube_video(video_url, input_path)
                else:
                    download_direct_video(video_url, input_path)

        except Exception as e:
            st.error(f"❌ Gagal mengambil video: {e}")
            st.stop()

    with st.spinner("Rendering video..."):
        filename = generate_filename(video_title, preset_name)
        output_path = os.path.join(OUTPUT_DIR, filename)

        # ===============================
        # PIPELINE RENDER (PLACEHOLDER)
        # ===============================
        # GANTI BAGIAN INI DENGAN LOGIC ASLI KAMU
        import shutil
        shutil.copy(input_path, output_path)

    st.success("✅ Rendering selesai!")

    # ===============================
    # PREVIEW & DOWNLOAD
    # ===============================
    st.video(output_path)

    with open(output_path, "rb") as f:
        st.download_button(
            label="⬇️ Download Video",
            data=f,
            file_name=filename,
            mime="video/mp4"
        )

    st.caption(f"📁 Disimpan sementara di: `{output_path}`")

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.caption("AutoClip • Streamlit + Google Colab")
