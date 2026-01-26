import subprocess
import cv2
import mediapipe as mp
import numpy as np
import os
import tempfile

# ===============================
# FFmpeg + ASS subtitle (LAMA)
# ===============================
def render(video_path, ass_path, output="output.mp4"):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf", f"scale=1080:1920,ass={ass_path}",
        output
    ]
    subprocess.run(cmd, check=True)


# ===============================
# PHASE 1: FACE CENTER + AUTO CROP
# ===============================
mp_face = mp.solutions.face_detection

def detect_face_center(frame, detector):
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = detector.process(rgb)

    if result.detections:
        box = result.detections[0].location_data.relative_bounding_box
        cx = int((box.xmin + box.width / 2) * w)
        cy = int((box.ymin + box.height / 2) * h)
        return cx, cy

    return w // 2, h // 2


def crop_9_16(frame, center_x):
    h, w, _ = frame.shape
    target_w = int(h * 9 / 16)

    x1 = max(0, center_x - target_w // 2)
    x2 = min(w, x1 + target_w)

    if x2 - x1 < target_w:
        x1 = max(0, w - target_w)
        x2 = w

    return frame[:, x1:x2]


def process_video_face_crop(
    input_path,
    output_path,
    detect_every=5
):
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    target_w = int(h * 9 / 16)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_w, h))

    face_detector = mp_face.FaceDetection(
        model_selection=0,
        min_detection_confidence=0.5
    )

    last_center_x = w // 2
    frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % detect_every == 0:
            cx, _ = detect_face_center(frame, face_detector)
            last_center_x = int(0.7 * last_center_x + 0.3 * cx)

        cropped = crop_9_16(frame, last_center_x)
        out.write(cropped)
        frame_idx += 1

    cap.release()
    out.release()
    face_detector.close()
