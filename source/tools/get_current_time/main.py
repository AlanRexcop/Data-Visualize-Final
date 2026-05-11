from datetime import datetime
import pytz

def execute(timezone: str = "Asia/Bangkok") -> str:
    """
    (This docstring will be dynamically overwritten by description.md in ai_logic.py, 
    but type hints must remain in the function signature for Gemini to parse them).
    """
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return f"Thời gian hiện tại là: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    except Exception as e:
        # Fallback if pytz is not installed or timezone is invalid
        now = datetime.now()
        return f"Thời gian local là: {now.strftime('%Y-%m-%d %H:%M:%S')} (Lỗi timezone: {e})"