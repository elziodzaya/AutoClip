import subprocess

def render(video_path, ass_path, output="output.mp4"):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf", f"scale=1080:1920,ass={ass_path}",
        output
    ]
    subprocess.run(cmd, check=True)

