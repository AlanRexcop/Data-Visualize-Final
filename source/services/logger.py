# source/services/logger.py
import json
import os
from datetime import datetime
from config import LOG_DIR

def log_session(session_data):
    """Appends a session entry to logs/session_history.json"""
    log_file = os.path.join(LOG_DIR, "session_history.json")
    
    # Add timestamp
    session_data["timestamp"] = datetime.now().isoformat()
    
    # Read existing or start new
    history =[]
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history =[]
            
    history.append(session_data)
    
    # Write back to file safely
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)