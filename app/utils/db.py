import os
import json
from datetime import datetime

HISTORY_FILE = "app/static/results/history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_to_history(record: dict):
    # Загружаем историю из файла
    history = load_history()
    
    # Добавляем новый объект в историю
    history.append(record)
    
    # Сохраняем обновлённую историю в файл
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)
