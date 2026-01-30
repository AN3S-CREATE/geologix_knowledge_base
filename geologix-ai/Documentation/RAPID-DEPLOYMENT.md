# Rapid Deployment Guide - Geologix AI

## 🚀 Quick Start (Production)

### 1. Prerequisites
- **Python 3.10+** must be installed.
- **Ollama** installed and running (default AI provider) *or* **LM Studio** (fallback provider).
- **Chrome/Edge/Firefox** for the web interface.
- **Local Network Access** (for secure, offline operation).

### 2. Installation
Install backend dependencies.

**Windows**:
Open PowerShell and run:
```powershell
python -m pip install -r "geologix-backend\Configuration\requirements.txt"
```

Then verify your setup:

```powershell
.\verify-installation.ps1
```

**Linux / Mac**:
```bash
python -m pip install -r geologix-backend/Configuration/requirements.txt
```

### 3. Starting the System
**Windows**:
Run in PowerShell:
```powershell
.\start-geologix.ps1
```

**Linux / Mac**:
```bash
cd geologix-ai/geologix-backend
python -m uvicorn Core_System.server:app --host 0.0.0.0 --port 8000
```

### 4. Accessing the Command Center
Once the backend is running:

1. Open http://localhost:8000/ (UI landing page)
2. Choose a UI variant (including **variant-6-copilot**)
3. Begin typing commands (e.g., "Search for invoices")

## ❓ Troubleshooting

**"Module not found" error**:
- Ensure you ran `python -m pip install -r geologix-backend\Configuration\requirements.txt`.
- If starting manually with `uvicorn`, run it from the `geologix-backend` folder.

**"Connection Failed" in UI**:
- Check if the terminal window (Backend) is still open and running.
- Ensure port 8000 is not blocked by a firewall.

**Knowledge Base is empty**:
- Run the import tools manually:
  ```powershell
  cd geologix-backend\Import_Tools
  python import_company_repository.py
  python import_emails.py
  python import_knowledge_db.py
  python import_archives.py
  ```
