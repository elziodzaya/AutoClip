from subtitle.utils import ass_time, ass_header_karaoke

def build(words):
    lines = [ass_header_karaoke()]

    for w in words:
        start = ass_time(w["start"])
        end = ass_time(w["end"])
        text = r"{\c&H00FFFF&}" + w["word"].upper()
        lines.append(f"Dialogue: 0,{start},{end},Karaoke,{text}")

    return "\n".join(lines)

