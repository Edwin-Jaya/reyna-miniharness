import os
from pathlib import Path

from dotenv import load_dotenv

# project root = two levels above this file (src/miniharness/config.py)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

ENDPOINT = os.getenv("ENDPOINT")      
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL", "your-model-name") 

MAX_TOKENS = 1024
MAX_STEPS = 5
# relative paths are anchored to the project root, so it doesn't matter where you run from
WORKSPACE = Path(os.getenv("WORKSPACE", "data/workspace"))
if not WORKSPACE.is_absolute():
    WORKSPACE = PROJECT_ROOT / WORKSPACE