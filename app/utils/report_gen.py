import pandas as pd
import os
from datetime import datetime
from app.utils.db import load_history

from pathlib import Path

REPORTS_DIR = Path("app/static/results")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def generate_excel_report():
    history = load_history()
    df = pd.DataFrame(history)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"report_{timestamp}.xlsx"
    df.to_excel(report_path, index=False)
    return str(report_path.resolve())  # Возвращаем абсолютный путь
