import whisper

model = whisper.load_model("base")

def transcribe(video_path):
    result = model.transcribe(
        video_path,
        word_timestamps=True
    )

    words = []
    for seg in result["segments"]:
        for w in seg["words"]:
            words.append({
                "word": w["word"].strip(),
                "start": w["start"],
                "end": w["end"]
            })

    return words


