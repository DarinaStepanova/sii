import threading
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
from datetime import datetime

from app.detectors.yolo_detector import detect_image, detect_stream, detect_video
from app.utils.report_gen import generate_excel_report
from app.utils.db import save_to_history, load_history

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "uploads")
RESULTS_FOLDER = os.path.join(BASE_DIR, "static", "results")

# Убедимся, что папки существуют
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Настройка статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/static")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    history = load_history()
    return templates.TemplateResponse("index.html", {"request": request, "history": history})


@app.post("/upload")
def upload_file(request: Request, file: UploadFile = File(...)):
    filename = file.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(RESULTS_FOLDER, f"result_{filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    person_count = detect_image(file_path, output_path)

    record = {
        "type": "image",
        "input_path": file_path,
        "output_path": output_path,
        "count": person_count,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_to_history(record)

    report_path = generate_excel_report()
    history = load_history()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "result_img": f"/static/results/{os.path.basename(output_path)}",
        "count": person_count,
        "report_path": report_path,
        "history": history
    })


@app.post("/upload-video/")
async def upload_video(request: Request, file: UploadFile = File(...)):
    filename = file.filename
    video_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(RESULTS_FOLDER, f"result_{filename}")

    contents = await file.read()
    with open(video_path, "wb") as f:
        f.write(contents)

    count = detect_video(video_path, output_path)

    record = {
        "type": "video",
        "input_path": video_path,
        "output_path": output_path,
        "count": count,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_to_history(record)

    report_path = generate_excel_report()
    history = load_history()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "result_video": f"/static/results/{os.path.basename(output_path)}",
        "count": count,
        "report_path": report_path,
        "history": history
    })


@app.get("/download_report")
def download_report():
    report_path = generate_excel_report()
    return FileResponse(
        report_path,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename=os.path.basename(report_path)
    )


@app.get("/start-stream")
def start_stream(camera_index: int = 0):
    thread = threading.Thread(target=detect_stream, args=(camera_index,), daemon=True)
    thread.start()
    return {"status": "Стрим с камеры ноутбука запущен. Окно откроется на сервере."}
