# app.py
# =====================================================
# AutoClip AI — Refactor Modular (Streamlit Cloud Safe)
# Features:
# 1. Modular code
# 2. Auto crop 9:16
# 3. Subtitle per kalimat (grouped)
# 4. Preset subtitle style (2short / CapCut-like)
# =====================================================

import streamlit as st
import tempfile, os, math
import numpy as np
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw
import whisper

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AutoClip AI", layout="wide")
st.title("🎬 AutoClip AI — Shorts Subtitle Generator")
st.caption("Refactor • Auto Crop • Preset Subtitle • Streamlit Cloud Safe")

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙️ Pengaturan Subtitle")
STYLE = st.sidebar.selectbox(
    "Preset Subtitle",
    ["2Short Highlight", "CapCut Clean", "Bounce Bold"]
)
MAX_CHARS = st.sidebar.slider("Max huruf per baris", 15, 40, 28)
HIGHLIGHT_COLOR = st.sidebar.color_picker("Warna Highlight", "#169EFF")

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("tiny")  # paling aman CPU

model = load_whisper_model()

# ---------------- UTILS ----------------
def auto_crop_9_16(video):
    w, h = video.size
    new_w = int(h * 9 / 16)
    x_center = w // 2
    x1 = max(0, x_center - new_w // 2)
    return video.crop(x1=x1, y1=0, x2=x1 + new_w, y2=h)


def group_words_to_sentences(words, max_chars):
    lines, current = [], ""
    start_time = None

    for w in words:
        if start_time is None:
            start_time = w['start']
        if len(current) + len(w['word']) <= max_chars:
            current += w['word'] + " "
        else:
            lines.append({
                "text": current.strip(),
                "start": start_time,
                "end": w['start']
            })
            current = w['word'] + " "
            start_time = w['start']

    if current:
        lines.append({
            "text": current.strip(),
            "start": start_time,
            "end": w['end']
        })

    return lines


def make_subtitle_clip(text, duration, style):
    img = Image.new("RGB", (900, 140), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    if style == "2Short Highlight":
        draw.rectangle([0, 0, 900, 140], fill=HIGHLIGHT_COLOR)
        draw.text((40, 40), text, fill="white")
    elif style == "CapCut Clean":
        draw.text((40, 40), text, fill="white")
    elif style == "Bounce Bold":
        draw.rectangle([0, 0, 900, 140], fill=HIGHLIGHT_COLOR)
        draw.text((40, 40), text.upper(), fill="white")

    clip = ImageClip(np.array(img)).set_duration(duration)

    if style == "Bounce Bold":
        clip = clip.resize(lambda t: 1 + 0.05 * abs(math.sin(t * 20)))

    return clip

# ---------------- UI ----------------
video_file = st.file_uploader("Upload video (maks 3 menit)", type=["mp4", "mov", "mkv"])

if video_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(video_file.read())
        video_path = tmp.name

    video = VideoFileClip(video_path)

    if video.duration > 180:
        st.error("❌ Maksimal durasi video 3 menit")
        st.stop()

    st.video(video_path)

    if st.button("🚀 Generate Short Video"):
        with st.spinner("🔍 Transcribing..."):
            result = model.transcribe(video_path, word_timestamps=True)

            words = []
            for seg in result["segments"]:
                if "words" in seg:
                    for w in seg["words"]:
                        words.append({
                            "word": w["word"].strip(),
                            "start": w["start"],
                            "end": w["end"]
                        })
                else:
                    # fallback aman
                    words.append({
                        "word": seg["text"].strip(),
                        "start": seg["start"],
                        "end": seg["end"]
                    })


        sentences = group_words_to_sentences(words, MAX_CHARS)

        with st.spinner("🎬 Rendering video..."):
            video = auto_crop_9_16(video)
            subs = []

            for s in sentences:
                clip = make_subtitle_clip(
                    s['text'],
                    s['end'] - s['start'],
                    STYLE
                ).set_start(s['start']).set_position(("center", "bottom"))
                subs.append(clip)

            final = CompositeVideoClip([video] + subs)

            out_path = os.path.join(tempfile.gettempdir(), "autoclip_short.mp4")
            final.write_videofile(out_path, fps=30, audio_codec="aac")

        st.success("✅ Video berhasil dibuat")
        st.video(out_path)

        with open(out_path, "rb") as f:
            st.download_button("⬇️ Download Video", f, file_name="autoclip_short.mp4")

st.markdown("---")
st.caption("AutoClip AI • Modular • Streamlit Cloud Ready")
