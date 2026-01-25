import streamlit as st
st.write("🚀 App started")

import tempfile
from utils.whisper import transcribe
from utils.video import render
from subtitle.karaoke import build

st.set_page_config(page_title="AutoClip AI", layout="centered")

st.title("🎬 AutoClip AI")
st.caption("Auto subtitle shorts ala 2short.ai")

video = st.file_uploader("Upload video", type=["mp4", "mov"])

preset = st.selectbox(
    "Pilih preset subtitle",
    ["Karaoke", "Simple (soon)", "Bounce (soon)"]
)

if video:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
        f.write(video.read())
        video_path = f.name

    if st.button("🚀 Generate"):
        with st.spinner("Transcribing..."):
            words = transcribe(video_path)

        with st.spinner("Generating subtitle..."):
            ass_text = build(words)
            ass_path = "subtitle.ass"
            with open(ass_path, "w", encoding="utf-8") as f:
                f.write(ass_text)

        with st.spinner("Rendering video..."):
            render(video_path, ass_path)

        st.success("Selesai!")
        st.video("output.mp4")
