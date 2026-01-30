# 🌍 GeoLogix AI - Enterprise Intelligence System

**Version**: 2.1.1  
**Status**: Production Ready  
**Built for**: Veralogix Group  
**UI Version**: Clean Layout v1.0.1 with AI Tech House  
**Last Updated**: 29 January 2026

---

## 🎯 Overview

GeoLogix AI is a powerful enterprise intelligence system for Veralogix Group. It provides AI-powered knowledge management, business analytics, forecasting, and decision support.

### Core Capabilities

| Feature | Description |
|---------|-------------|
| 🧠 **Deep Thinking** | Chain-of-thought reasoning for complex analysis |
| 🌐 **Web Search** | Real-time internet search integration |
| 📊 **Forecasting** | Future projections with confidence levels |
| 💬 **Chat History** | Persistent conversations with folder organization |
| 📁 **16,579+ Archives** | Full company historical data indexed |
| 🔍 **Knowledge Search** | Instant search across all documents and emails |
| 📈 **Business Analytics** | SWOT, PESTEL, Risk, Financial analysis |
| 🧩 **Long-Term Memory** | Remember facts and entities across sessions |
| 📋 **Smart Extractors** | Entity, sentiment, timeline extraction |
| 🤖 **Agentic AI** | Auto tool chaining and execution planning |
| ⚡ **Streaming** | Real-time token streaming responses |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Ollama** with llama3 model (or LM Studio as fallback)

### Start the System

```powershell
# Navigate to project
cd "Q:\Dev\Google Avinity\geologix_knowledge_base\geologix-ai"

# Start everything
.\start-geologix.ps1

# Or with ngrok tunnel (for remote access)
.\start-ngrok.ps1
```

### Access Points

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Local UI |
| http://localhost:8000/ui/ | Direct UI access |
| http://localhost:8000/api | API status |
| (printed by `start-ngrok.ps1`) | Public URL (ngrok) |

---

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                            │
│              6 UI Variants • Voice • Mobile                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Port 8000)                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │ Chat API    │ │ Search API  │ │ Analysis & Forecast API ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└──────┬──────────────────┬────────────────────┬──────────────┘
       │                  │                    │
       ▼                  ▼                    ▼
┌─────────────┐  ┌────────────────┐  ┌─────────────────────────┐
│   Ollama    │  │ Knowledge Base │  │      MCP Tools (34)     │
│  llama3     │  │ ├─ Documents   │  │ • Web Search            │
│             │  │ ├─ Emails      │  │ • Deep Analysis         │
│             │  │ ├─ Archives    │  │ • Forecasting           │
│             │  │ └─ Strategic   │  │ • Chat Management       │
└─────────────┘  └────────────────┘  └─────────────────────────┘
```

---

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Redirects to UI |
| GET | `/api` | API status |
| GET | `/api/health` | Health check |
| GET | `/api/dashboard` | System metrics |
| GET | `/api/stats` | Knowledge base stats |
| GET | `/api/ai/status` | AI provider status |
| POST | `/api/chat` | AI chat (main endpoint) |
| GET | `/api/search?q=&source=&limit=` | Knowledge base search |
| POST | `/api/chats` | Create new chat |
| GET | `/api/tools` | List MCP tools |
| POST | `/api/tools/execute` | Execute MCP tool |
| GET | `/api/files?source=` | List files |
| POST | `/api/upload` | Upload file |

### Chat Options

```json
POST /api/chat
{
  "message": "Your question here",
  "chat_id": "abc123",        // Optional: continue existing chat
  "deep_thinking": true,      // Optional: enable chain-of-thought
  "web_search": true          // Optional: search internet
}
```

### Chat Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/chats` | List all chats |
| GET | `/api/chats/{id}` | Get chat history |
| DELETE | `/api/chats/{id}` | Delete chat |
| POST | `/api/chats/{id}/move` | Move chat to folder |

### Folder Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/folders` | List folders |
| POST | `/api/folders` | Create folder |
| DELETE | `/api/folders/{id}` | Delete folder |

### Analysis & Forecasting

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/web-search?q=` | Web search |
| POST | `/api/analyze` | Deep analysis |
| POST | `/api/forecast` | Generate projections |

---

## 🧰 MCP Tools (34 Total)

### Knowledge (4 tools)

- `search_knowledge_base` - Search documents, emails, archives
- `read_document` - Read file content
- `search_archives` - Search with tag filtering
- `get_archive_summary` - Archive statistics

### Web (2 tools)

- `web_search` - Internet search
- `search_industry_news` - Mining industry news

### Analysis (4 tools)

- `deep_analyze` - Chain-of-thought analysis
- `swot_analysis` - SWOT framework
- `risk_assessment` - Risk matrix
- `root_cause_analysis` - 5 Whys method

### Forecasting (4 tools)

- `forecast` - Future projections
- `calculate_growth` - CAGR calculation
- `calculate_roi` - Return on investment
- `calculate_breakeven` - Breakeven analysis

### Chat (5 tools)

- `list_chats` - List conversations
- `get_chat_history` - Get messages
- `create_folder` - Create chat folder
- `list_folders` - List all folders
- `move_chat` - Organize chats

### Memory (5 tools)

- `remember_fact` - Store facts in long-term memory
- `recall_facts` - Retrieve stored facts
- `remember_entity` - Store entity info (people, companies)
- `get_entity` - Retrieve entity info
- `memory_stats` - Memory system statistics

### Extractors (5 tools)

- `extract_entities` - Extract people, dates, amounts
- `analyze_sentiment` - Sentiment analysis
- `summarize_text` - Generate summaries
- `extract_timeline` - Extract events with dates
- `compare_documents` - Compare two documents

### Agents (4 tools)

- `analyze_intent` - Understand user intent
- `create_plan` - Create execution plan
- `execute_plan` - Run multi-step workflow
- `suggest_followups` - Suggest next questions

### Utility (1 tool)

- `calculator` - Math expressions

---

## 📂 Project Structure

```text
geologix-ai/
├── .gitignore
├── .env.example
├── README.md
├── API_ENDPOINTS.md
├── start-geologix.ps1          # Main startup
├── start-ngrok.ps1             # ngrok tunnel
├── verify-installation.ps1     # Verification
│
├── UI/                         # Frontend
│   ├── index.html
│   ├── variant-1-minimal.html
│   ├── variant-2-balanced.html
│   ├── variant-3-interactive.html
│   ├── variant-4-dashboard.html
│   ├── variant-5-maximum.html
│   ├── variant-6-copilot.html
│   ├── scripts/
│   └── styles/
│
├── geologix-backend/           # Backend
│   ├── Configuration/
│   │   ├── config.py
│   │   └── requirements.txt
│   │
│   ├── Core_System/
│   │   ├── server.py           # FastAPI app
│   │   ├── llm_client.py       # AI integration
│   │   ├── mcp_tools.py        # 34 MCP tools
│   │   ├── knowledge_engine.py # Search engine
│   │   ├── chat_manager.py     # Chat history
│   │   ├── web_search.py       # Web search
│   │   ├── deep_analysis.py    # Analysis engine
│   │   ├── file_storage.py
│   │   ├── categorizer.py
│   │   └── logging_config.py
│   │
│   ├── Data_Directories/
│   │   ├── archive_index.json  # 16,579 files
│   │   ├── company_index.json  # 752 docs
│   │   ├── email_index.json    # 2,838 emails
│   │   ├── knowledge_index.json
│   │   └── chats/              # Chat history
│   │
│   ├── Import_Tools/
│   │   ├── import_archives.py
│   │   ├── import_company_repository.py
│   │   ├── import_emails.py
│   │   └── import_knowledge_db.py
│   │
│   └── tests/
│
└── Documentation/
    ├── RAPID-DEPLOYMENT.md
    ├── mcp-tools-integration.md
    ├── professional-ai-setup.md
    └── walkthrough.md
```

---

## ⚙️ Configuration

### Backend Configuration

Edit `geologix-backend/Configuration/config.py`:

```python
# Active AI Provider: "ollama" or "lmstudio"
AI_PROVIDER = "ollama"

# Ollama (primary)
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3:latest"

# LM Studio (optional fallback)
LM_STUDIO_URL = "http://localhost:1234/v1"
LM_STUDIO_MODEL = "llama-3.1-8b-instruct"
```

`start-ngrok.ps1` supports an optional custom ngrok domain via `GEOLOGIX_NGROK_DOMAIN`.

---

## 📊 Data Sources

| Source | Count | Description |
|--------|-------|-------------|
| **Archives** | 16,579 | Historical files (2016-2024) |
| **Emails** | 2,838 | Company communications |
| **Documents** | 752 | Active business documents |
| **Knowledge** | Strategic | Business intelligence articles |

### Archive Categories

- Financial (invoices, budgets, statements)
- Operational (production, logistics, equipment)
- Compliance (safety, audits, permits)
- HR (payroll, recruitment, training)
- Sales (quotes, orders, customers)

---

## 🔒 Security

- **Local-first**: All data stays on your infrastructure
- **No cloud dependencies**: Works completely offline
- **JWT authentication ready**: Enterprise security
- **CORS configured**: Controlled access

---

## 🛠️ Troubleshooting

### Backend won't start

```powershell
# Check Python
python --version

# Install dependencies
python -m pip install -r geologix-backend/Configuration/requirements.txt
```

### Ollama not connecting

```powershell
# Check Ollama status
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

### Port already in use

```powershell
# Find process on port 8000
Get-NetTCPConnection -LocalPort 8000

# Kill it
Stop-Process -Id <PID> -Force
```

---

## 📝 Version History

### v2.1.0 (January 2026)

- ✅ Long-term memory system (facts, entities, metrics)
- ✅ Intelligent extractors (entity, sentiment, timeline)
- ✅ Agentic capabilities (intent, planning, execution)
- ✅ Streaming responses for real-time output
- ✅ Copilot Workspace UI (variant-6)
- ✅ 34 MCP tools (14 new tools added)
- ✅ Document comparison
- ✅ Follow-up suggestions

### v2.0.0 (January 2026)

- ✅ Deep Thinking mode with chain-of-thought
- ✅ Web Search integration
- ✅ Chat History with folder management
- ✅ 20 MCP tools
- ✅ Enhanced system instruction
- ✅ Forecasting engine
- ✅ Analysis frameworks (SWOT, PESTEL, Risk)
- ✅ Ollama integration

### v1.0.0

- Initial release
- Knowledge base search
- Basic AI chat
- 5 UI variants

---

## 📞 Support

**Built for Veralogix Group**

For technical support, refer to:

- `API_ENDPOINTS.md` - Full API documentation
- `Documentation/` - Detailed guides

---

*GeoLogix AI - Enterprise Intelligence for Veralogix Group*
