import os
from pathlib import Path

# Base Paths
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent.parent  # Points to geologix_knowledge_base

# Data Sources (Read-Only)
SOURCE_DOCUMENTS = PROJECT_ROOT / "Company_documents"
SOURCE_EMAILS = PROJECT_ROOT / "emails"
SOURCE_KNOWLEDGE_DB = PROJECT_ROOT / "knowledge_database"

# Internal Data (Read/Write)
DATA_DIR = BACKEND_DIR / "Data_Directories"
STORAGE_DIR = DATA_DIR / "storage"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"
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
for path in [STORAGE_DIR, CHROMA_DB_DIR, LOGS_DIR]:
    path.mkdir(parents=True, exist_ok=True)
