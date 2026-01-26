import streamlit as st
import os
import subprocess
import uuid

# =============================
# KONFIGURASI DASAR
# =============================
BASE_DIR = "/content/AutoClip"
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.set_page_config(page_title="AutoClip AI", layout="centered")
st.title("🎬 AutoClip AI (Colab Edition)")

# =============================
# UI INPUT
# =============================
uploaded_video = st.file_uploader(
    "Upload video (mp4)",
    type=["mp4"]
)

clip_duration = st.slider(
    "Durasi clip (detik)",
    min_value=5,
    max_value=60,
    value=15
)

render_btn = st.button("🚀 Render Video")

# =============================
# FUNGSI RENDER (FFMPEG)
# =============================
def render_video(input_path, output_path, duration):
    """
    Render video sederhana:
    - ambil 0-detik awal
    - potong sesuai durasi
    """
    cmd = f"""
    ffmpeg -y -i "{input_path}" \
    -t {duration} \
    -c:v libx264 -preset veryfast -crf 23 \
    -c:a aac \
    "{output_path}"
    """

    result = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    return result


# =============================
# AKSI UTAMA
# =============================
if render_btn and uploaded_video is not None:

    # simpan file upload
    input_video_path = os.path.join(
        UPLOAD_DIR,
        f"{uuid.uuid4()}.mp4"
    )

    with open(input_video_path, "wb") as f:
        f.write(uploaded_video.read())

    output_video_path = os.path.join(
        OUTPUT_DIR,
        f"final_{uuid.uuid4()}.mp4"
    )

    # proses render
    with st.spinner("⏳ Rendering video..."):
        result = render_video(
            input_video_path,
            output_video_path,
            clip_duration
        )

    # =============================
    # CEK HASIL
    # =============================
    if not os.path.exists(output_video_path):
        st.error("❌ Render gagal, file output tidak ditemukan")
        st.text(result.stderr)
    else:
        st.success("✅ Render selesai!")

        # tampilkan video (CARA PALING AMAN)
        with open(output_video_path, "rb") as video_file:
            video_bytes = video_file.read()
            st.video(video_bytes)

        # tombol download
        st.download_button(
            label="⬇️ Download Video",
            data=video_bytes,
            file_name="autoclip_result.mp4",
            mime="video/mp4"
        )

        # debug opsional
        with st.expander("🛠 Debug Info"):
            st.write("Input:", input_video_path)
            st.write("Output:", output_video_path)
            st.text(result.stderr)

else:
    st.info("⬆️ Upload video lalu klik Render")
with open(output_video_path, "rb") as video_file:
    video_bytes = video_file.read()

st.video(video_bytes)

st.download_button(
    label="⬇️ Download Video",
    data=video_bytes,
    file_name="autoclip_result.mp4",
    mime="video/mp4"
)

