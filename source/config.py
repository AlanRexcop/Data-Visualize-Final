# source/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Secrets
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Model Settings
# Using gemini-3.1-flash-lite as default, easily swappable
GEMINI_MODEL = "gemini-3.1-flash-lite"

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "source", "data")
TOOLS_DIR = os.path.join(BASE_DIR, "source", "tools")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Sandbox Constraints
ALLOWED_LIBS = ["pandas", "numpy", "plotly"]

# Setup Logging Path
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)