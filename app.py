# app.py
# Streamlit Auto Subtitle Shorts (2short.ai-like MVP)

import streamlit as st
import tempfile
import os
import math
import numpy as np
from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Auto Shorts Subtitle AI", layout="wide")

st.title("🎬 Auto Shorts Subtitle AI")
st.caption("Versi MVP ala 2short.ai — Python + Streamlit + Whisper")

# ==============================
# Sidebar Settings
# ==============================
st.sidebar.header("⚙️ Pengaturan Subtitle")
style = st.sidebar.selectbox("Style Subtitle", ["Background Highlight", "Simple", "Bounce"])
max_letters = st.sidebar.slider("Max huruf per baris", 10, 30, 20)
bg_color = st.sidebar.color_picker("Warna Highlight", "#169EFF")

# ==============================
# Upload Video
# ==============================
video_file = st.file_uploader("Upload video (mp4)", type=["mp4", "mov", "mkv"])

if video_file:
    st.video(video_file)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(video_file.read())
        video_path = tmp.name

    if st.button("🚀 Generate Subtitle & Short Video"):
        with st.spinner("Transcribing audio..."):
            model = WhisperModel("small", device="cpu", compute_type="int8")

            segments, info = model.transcribe(video_path, word_timestamps=True)

            words = []
            for seg in segments:
                for w in seg.words:
                    words.append({
                        "word": w.word.strip(),
                        "start": w.start,
                        "end": w.end
                    })

        st.success(f"Transkrip selesai ({len(words)} kata)")

        with st.spinner("Rendering video..."):
            video = VideoFileClip(video_path)
            subtitle_clips = []

            def subtitle_clip(text, duration, bounce=False):
                img = Image.new("RGB", (900, 120), bg_color if style != "Simple" else (0,0,0))
                draw = ImageDraw.Draw(img)
                draw.text((40, 30), text, fill="white")
                clip = ImageClip(np.array(img)).set_duration(duration)
                if bounce:
                    clip = clip.resize(lambda t: 1 + 0.08 * abs(math.sin(t * 20)))
                return clip

            for w in words:
                clip = subtitle_clip(
                    w['word'],
                    w['end'] - w['start'],
                    bounce=(style == "Bounce")
                )
                clip = clip.set_start(w['start']).set_position(("center", "bottom"))
                subtitle_clips.append(clip)

            final = CompositeVideoClip([video] + subtitle_clips)

            output_path = os.path.join(tempfile.gettempdir(), "output_short.mp4")
            final.write_videofile(output_path, fps=30, audio_codec="aac")

        st.success("✅ Video selesai!")
        st.video(output_path)

        with open(output_path, "rb") as f:
            st.download_button("⬇️ Download Video", f, file_name="short_subtitle.mp4")

st.markdown("---")
st.caption("Dibuat dengan ❤️ | Python • Streamlit • Whisper • MoviePy")
