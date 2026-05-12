# source/services/logger.py
import json
import os
import glob
from config import LOG_DIR

def save_conversation(conversation_id: str, data: dict):
    """Overwrites the specific conversation JSON file with the latest state."""
    log_file = os.path.join(LOG_DIR, f"{conversation_id}.json")
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def list_conversations() -> list:
    """Returns a list of all conversation JSON file paths sorted by newest first."""
    files = glob.glob(os.path.join(LOG_DIR, "conv_*.json"))
    files.sort(reverse=True)
    return files

def load_conversation(filepath: str) -> dict:
    """Loads a specific conversation JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}