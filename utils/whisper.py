import whisper

_model = None

def get_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model

def transcribe(video_path):
    model = get_model()
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
