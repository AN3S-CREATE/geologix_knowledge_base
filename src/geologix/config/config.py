import os
from pathlib import Path

# Base Paths - Updated for new structure
CONFIG_DIR = Path(__file__).resolve().parent  # src/geologix/config/
PROJECT_ROOT = CONFIG_DIR.parents[2]  # geologix_knowledge_base/

# Data Sources (Read-Only) - Now in data/sources/
SOURCE_DOCUMENTS = PROJECT_ROOT / "data" / "sources" / "Company_documents"
SOURCE_EMAILS = PROJECT_ROOT / "data" / "sources" / "emails"
SOURCE_KNOWLEDGE_DB = PROJECT_ROOT / "data" / "sources" / "knowledge_database"

# Internal Data (Read/Write) - Now in data/runtime/
# Uses GEOLOGIX_DATA_DIR env var if set, otherwise defaults to data/runtime
DATA_DIR = Path(os.getenv("GEOLOGIX_DATA_DIR", PROJECT_ROOT / "data" / "runtime")).resolve()

# Subdirectories
STORAGE_DIR = DATA_DIR / "storage"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"
CHATS_DIR = DATA_DIR / "chats"
LOGS_DIR = DATA_DIR / "logs"

# System Settings
APP_NAME = "Geologix AI"
VERSION = "1.0.0"
DEBUG = True
HOST = "0.0.0.0"
PORT = 8000

# Security (Placeholder for JWT)
SECRET_KEY = "geologix-internal-secure-key-change-in-prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# AI Model Settings (Ollama - Primary)
OLLAMA_URL = "http://localhost:11434"
# Model priority: try smaller models first if memory is limited
OLLAMA_MODEL_PRIORITY = ["llama3.2:1b", "llama3.2:3b", "llama3:latest", "mistral:latest"]
OLLAMA_MODEL = "llama3.2:1b"  # Using smaller model for lower memory usage

# AI Model Settings (LM Studio - Fallback)
LM_STUDIO_URL = "http://localhost:1234/v1"
LM_STUDIO_MODEL = "llama-3.1-8b-instruct"

# Active AI Provider: "ollama" or "lmstudio"
AI_PROVIDER = "ollama"
CONTEXT_WINDOW = 128000

# Ensure directories exist
for path in [STORAGE_DIR, CHROMA_DB_DIR, LOGS_DIR, CHATS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Startup Diagnostics (Visible in Console)
print(f"--- GEOLOGIX CONFIG ---")
print(f"DATA_DIR: {DATA_DIR}")
print(f"CHATS_DIR: {CHATS_DIR} ({len(list(CHATS_DIR.glob('*.json'))) if CHATS_DIR.exists() else 0} files)")
print(f"CHROMA_DB: {CHROMA_DB_DIR} (Exists: {CHROMA_DB_DIR.exists()})")
print(f"-----------------------")
