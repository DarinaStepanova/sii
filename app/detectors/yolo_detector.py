import cv2
from ultralytics import YOLO
import os
from datetime import datetime

weight_path = os.path.abspath("app/detectors/yolov8n.pt")
model = YOLO(weight_path)  # можно заменить на yolov8s.pt или другую

def detect_image(image_path: str, output_path: str):
    results = model(image_path)
    count = sum(1 for c in results[0].boxes.cls if int(c) == 0)  # class 0 = person
    results[0].save(output_path)
    return count

def detect_video(video_path: str, output_path: str):
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # можно заменить на 'avc1' при поддержке H.264
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    max_persons = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)[0]
        frame = results.plot()
        out.write(frame)

        current_count = sum(1 for c in results.boxes.cls if int(c) == 0)
        max_persons = max(max_persons, current_count)

    cap.release()
    out.release()
    return max_persons

import threading

def detect_stream(camera_index: int = 0):  # 0 — это обычно встроенная камера
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("Не удалось подключиться к камере.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Детекция с YOLO
        results = model(frame)[0]
        frame = results.plot()

        # Показываем изображение в окне
        cv2.imshow("Stream — Подсчёт посетителей", frame)

        # Выход по кнопке 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

