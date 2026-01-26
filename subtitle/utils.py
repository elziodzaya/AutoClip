def ass_time(seconds: float):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def ass_header_karaoke(font="Arial Black", size=64, marginV=260):
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,{font},{size},&H00FFFFFF,&H00000000,1,0,1,3,0,2,50,50,{marginV},1

[Events]
Format: Layer, Start, End, Style, Text
"""
