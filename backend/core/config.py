import os

# Project base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _auto_create_env():
    env_path = os.path.join(os.path.dirname(BASE_DIR), ".env")
    if not os.path.exists(env_path):
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("# Smart College AI Environment Settings\n")
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
            f.write("GROQ_API_KEY=your_groq_api_key_here\n")

def _load_env():
    env_path = os.path.join(os.path.dirname(BASE_DIR), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key and key not in os.environ:
                        os.environ[key] = val

_auto_create_env()
_load_env()

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
DB_FILE_PATH = os.path.join(STORAGE_DIR, "db.json")

# Ensure required directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STORAGE_DIR, exist_ok=True)

# Settings
PROJECT_NAME = "Smart College AI Assistant"
ALLOWED_EXTENSIONS = {"pdf", "txt"}
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25MB

# CORS settings for local development
CORS_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
