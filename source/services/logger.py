import os
import json
from datetime import datetime

LOG_PATH = "output/audit_log.json"

def load_history():
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def log_interaction(history, prompt, ai_explanation, ai_code, final_code, was_edited, result_log, plot_json):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prompt": prompt,
        "ai_explanation": ai_explanation,
        "ai_code": ai_code,
        "final_code": final_code,
        "was_edited": was_edited,
        "result_log": result_log,
        "plot_json": plot_json
    }
    history.append(entry)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)
    return history
