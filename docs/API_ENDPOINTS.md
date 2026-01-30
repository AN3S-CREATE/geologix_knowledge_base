# GeoLogix AI - API Reference

**Base URL**: `http://localhost:8000` (local) | (printed by `start-ngrok.ps1`) (public via ngrok)

---

## System Endpoints

### Root
```
GET /
```
Redirects to UI (`/ui/index.html`)

### API Status
```
GET /api
```
**Response:**
```json
{
  "system": "Geologix AI",
  "status": "online",
  "version": "1.0.0",
  "message": "Operational Intelligence Ready"
}
```

### Health Check
```
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "geologix-backend"
}
```

### Knowledge Stats
```
GET /api/stats
```
**Response:**
```json
{
  "success": true,
  "total_items": 20182,
  "categories": {
    "documents": 752,
    "emails": 2838,
    "knowledge": 13,
    "archives": 16579
  }
}
```

### System Dashboard
```
GET /api/dashboard
```
**Response:**
```json
{
  "timestamp": "2026-01-28T21:00:00",
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 45.3,
    "memory_used_gb": 7.2,
    "memory_total_gb": 16.0,
    "disk_percent": 65.0,
    "disk_free_gb": 120.5
  },
  "knowledge_base": {
    "company_docs": 752,
    "emails": 2838,
    "archives": 16579
  },
  "ai": {
    "provider": "ollama",
    "available": true
  }
}
```

### AI Status
```
GET /api/ai/status
```
**Response:**
```json
{
  "provider": "ollama",
  "available": true,
  "model": "llama3:latest",
  "endpoint": "http://localhost:11434"
}
```

---

## Chat Endpoints

### Main Chat (POST)
```
POST /api/chat
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "What are our Q4 production numbers?",
  "chat_id": "abc12345",
  "conversation_id": "abc12345",
  "deep_thinking": false,
  "web_search": false,
  "model": "auto"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | ✅ | User's question |
| chat_id | string | ❌ | Continue existing chat (preferred) |
| conversation_id | string | ❌ | Alias for `chat_id` (supported for compatibility) |
| deep_thinking | bool | ❌ | Enable chain-of-thought analysis |
| web_search | bool | ❌ | Include web search results |
| model | string | ❌ | Model selection (default: "auto") |

**Response (Standard):**
```json
{
  "response": "Based on the Q4 2024 operational report...",
  "chat_id": "abc12345",
  "provider": "ollama"
}
```

**Response (With Deep Thinking):**
```json
{
  "response": "Based on analysis...",
  "chat_id": "abc12345",
  "thinking": "╔══════════════════════════════════════╗\n║    DEEP THINKING PROCESS             ║\n...",
  "analysis": {
    "question_type": "financial",
    "framework_used": "forecast",
    "confidence": "HIGH",
    "insights": ["..."],
    "recommendations": [{"priority": "HIGH", "action": "..."}]
  },
  "web_search": null,
  "provider": "ollama"
}
```

**Response (With Web Search):**
```json
{
  "response": "According to recent data...",
  "chat_id": "abc12345",
  "web_search": {
    "success": true,
    "query": "coal prices south africa",
    "results": [
      {"title": "...", "snippet": "...", "url": "..."}
    ]
  },
  "provider": "ollama"
}
```

### Streaming Chat (SSE)
```
POST /api/chat/stream
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Summarize our safety audits",
  "chat_id": "abc12345",
  "deep_thinking": false,
  "web_search": false,
  "model": "auto"
}
```

**Response:**
- Server-Sent Events stream (`text/event-stream`)
- Each chunk is sent as `data: <text>` lines, terminated by a final `data: [DONE]`

---

## Chat History Endpoints

### List All Chats
```
GET /api/chats
GET /api/chats?folder_id=financial
```

**Response:**
```json
[
  {
    "id": "abc12345",
    "title": "Q4 Production Analysis",
    "folder_id": "operations",
    "updated": "2026-01-28T21:00:00",
    "message_count": 12
  }
]
```

### Create Chat
```
POST /api/chats
Content-Type: application/json
```

**Request Body:**
```json
{
  "folder_id": "default",
  "title": "Optional title"
}
```

**Response:**
```json
{
  "chat_id": "abc12345",
  "title": "Optional title",
  "folder_id": "default"
}
```

### Get Chat
```
GET /api/chats/{chat_id}
```

**Response:**
```json
{
  "id": "abc12345",
  "title": "Q4 Production Analysis",
  "folder_id": "operations",
  "created": "2026-01-28T20:00:00",
  "updated": "2026-01-28T21:00:00",
  "messages": [
    {
      "role": "user",
      "content": "What are our Q4 numbers?",
      "timestamp": "2026-01-28T20:00:00"
    },
    {
      "role": "assistant",
      "content": "Based on the data...",
      "timestamp": "2026-01-28T20:00:05"
    }
  ]
}
```

### Delete Chat
```
DELETE /api/chats/{chat_id}
```

**Response:**
```json
{
  "success": true,
  "deleted": "abc12345"
}
```

### Move Chat to Folder
```
POST /api/chats/{chat_id}/move
Content-Type: application/json
```

**Request Body:**
```json
{
  "chat_id": "abc12345",
  "target_folder_id": "financial"
}
```

**Response:**
```json
{
  "success": true,
  "chat_id": "abc12345",
  "from_folder": "default",
  "to_folder": "financial"
}
```

---

## Folder Endpoints

### List Folders
```
GET /api/folders
```

**Response:**
```json
[
  {"id": "default", "name": "General", "created": "2026-01-28T21:00:00"},
  {"id": "financial", "name": "Financial Analysis", "created": "2026-01-28T21:00:00"},
  {"id": "operations", "name": "Operations", "created": "2026-01-28T21:00:00"},
  {"id": "strategic", "name": "Strategic Planning", "created": "2026-01-28T21:00:00"}
]
```

### Create Folder
```
POST /api/folders
Content-Type: application/json
```

**Request Body:**
```json
{
  "folder_id": "compliance",
  "name": "Compliance & Safety"
}
```

**Response:**
```json
{
  "success": true,
  "folder_id": "compliance",
  "name": "Compliance & Safety"
}
```

### Delete Folder
```
DELETE /api/folders/{folder_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Folder 'compliance' deleted, chats moved to default"
}
```

---

## Tools Endpoints

### List Available Tools
```
GET /api/tools
```

**Response:**
```json
{
  "tools": [
    {
      "name": "calculator",
      "description": "Evaluate a mathematical expression.",
      "parameters": {"expression": "string"}
    }
  ],
  "categories": {
    "knowledge": ["search_knowledge_base", "read_document"],
    "utility": ["calculator"]
  },
  "total": 34
}
```

### Execute Tool
```
POST /api/tools/execute
Content-Type: application/json
```

**Request Body:**
```json
{
  "tool_name": "calculator",
  "params": {
    "expression": "1+1"
  }
}
```

**Response:** (tool-specific)
```json
{
  "expression": "1+1",
  "result": 2
}
```

---

## Search Endpoints

### Knowledge Base Search
```
GET /api/search?q={query}&source={source}&limit={limit}
```

**Query Params:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| q | string | ✅ | Search query |
| source | string | ❌ | `all` (default), `documents`, `emails`, `knowledge`, `archives` |
| limit | int | ❌ | Max results (default: 10) |

**Example:**
```
GET /api/search?q=invoice%202024&source=all&limit=10
```

**Response:**
```json
[
  {
    "type": "archive",
    "filename": "Invoice_2024_001.pdf",
    "relative_path": "C\\Users\\...\\Invoice_2024_001.pdf",
    "score": 10
  },
  {
    "type": "email",
    "subject": "Invoice for Q4 Services",
    "sender": "accounts@vendor.com",
    "date": "2024-10-15",
    "score": 8
  }
]
```

### Web Search
```
GET /api/web-search?q={query}&max_results=5
```

**Example:**
```
GET /api/web-search?q=coal%20prices%20south%20africa
```

**Response:**
```json
{
  "success": true,
  "query": "coal prices south africa",
  "timestamp": "2026-01-28T21:00:00",
  "results": [
    {
      "title": "Coal Prices - Market Overview",
      "snippet": "Current coal prices in South Africa...",
      "url": "https://example.com/coal-prices",
      "type": "abstract"
    }
  ],
  "source": "DuckDuckGo"
}
```

---

## Analysis Endpoints

### Deep Analysis
```
POST /api/analyze
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "What are the risks of expanding operations?"
}
```

**Response:**
```json
{
  "question": "What are the risks of expanding operations?",
  "question_type": "risk_assessment",
  "framework_used": "risk",
  "thinking_process": [
    {"stage": "UNDERSTANDING", "thought": "Analyzing question..."},
    {"stage": "CLASSIFICATION", "thought": "Question type: risk_assessment"},
    {"stage": "FRAMEWORK_SELECTION", "thought": "Using framework: risk"}
  ],
  "analysis": {
    "framework": "Risk Assessment Matrix",
    "risk_categories": {
      "operational": {"probability": "Medium", "impact": "High", "score": 12},
      "financial": {"probability": "Medium", "impact": "Medium", "score": 9}
    }
  },
  "insights": ["..."],
  "recommendations": [
    {"priority": "HIGH", "action": "...", "expected_impact": "...", "timeline": "..."}
  ],
  "confidence": "MEDIUM"
}
```

### Generate Forecast
```
POST /api/forecast?metric={name}&current_value={value}&growth_rate={rate}&periods={n}
```

**Example:**
```
POST /api/forecast?metric=production&current_value=45000&growth_rate=0.03&periods=12
```

**Response:**
```json
{
  "metric": "production",
  "current_value": 45000,
  "growth_rate": "3.0%",
  "projections": [
    {"period": 1, "date": "2026-02", "projected_value": 46350.0, "growth_from_current": "3.0%"},
    {"period": 2, "date": "2026-03", "projected_value": 47740.5, "growth_from_current": "6.1%"},
    {"period": 3, "date": "2026-04", "projected_value": 49172.72, "growth_from_current": "9.3%"}
  ],
  "summary": {
    "3_month": {"projected_value": 49172.72},
    "6_month": {"projected_value": 53746.85},
    "12_month": {"projected_value": 64179.55}
  },
  "confidence": "HIGH (90%)",
  "methodology": "Compound growth with optional seasonal adjustment"
}
```

---

## Memory Endpoints

### Remember Fact
```
POST /api/memory/fact?fact={text}&category={category}&confidence={confidence}
```

### Recall Facts
```
GET /api/memory/facts?query={query}&category={category}&limit={limit}
```

### Remember Entity
```
POST /api/memory/entity?name={name}&entity_type={type}
```

### Get Entity
```
GET /api/memory/entity/{name}?entity_type={type}
```

### Memory Stats
```
GET /api/memory/stats
```

---

## Extractor Endpoints

These endpoints accept text input and return structured outputs.

```
POST /api/extract/entities?text={text}
POST /api/extract/sentiment?text={text}
POST /api/extract/summary?text={text}&max_sentences=5
POST /api/extract/timeline?text={text}
POST /api/extract/compare?doc1={text}&doc2={text}
```

---

## Agent Endpoints

### Analyze Intent
```
POST /api/agent/intent?query={query}
```

### Create Plan
```
POST /api/agent/plan?query={query}
```

### Execute Plan
```
POST /api/agent/execute
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "Analyze Q4 performance",
  "steps": []
}
```

### Suggest Followups
```
GET /api/agent/followups?query={query}
```

---

## File Endpoints

### List Files
```
GET /api/files?source={type}
```

**Source options:** `documents`, `emails`, `knowledge`

**Response:**
```json
[
  {
    "filename": "report.pdf",
    "path": "Q:\\Dev\\...\\Company_documents\\...\\report.pdf",
    "relative_path": "BRAIN\\VAULT\\...\\report.pdf",
    "size": 125000,
    "modified": 1719432000.0,
    "is_source": true
  }
]
```

### Upload File
```
POST /api/upload
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: The file to upload

**Response:**
```json
{
  "status": "saved",
  "path": "Q:\\Dev\\...\\geologix-backend\\Data_Directories\\storage\\uploaded_report.pdf",
  "metadata": {
    "category": "OPERATIONS",
    "tags": [],
    "sensitivity": "INTERNAL"
  }
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "error": "Error description",
  "detail": "Additional details if available"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Server Error

---

## Usage Examples

### PowerShell

```powershell
# Simple chat
$body = @{message="What invoices do we have from October?"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"

# Chat with deep thinking
$body = @{message="Analyze our Q4 performance"; deep_thinking=$true} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"

# Chat with web search
$body = @{message="What are current coal prices?"; web_search=$true} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"

# Search knowledge base
Invoke-RestMethod -Uri "http://localhost:8000/api/search?q=safety%20audit"

# List folders
Invoke-RestMethod -Uri "http://localhost:8000/api/folders"
```

### curl

```bash
# Simple chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What invoices do we have?"}'

# Deep thinking
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Analyze risks","deep_thinking":true}'

# Web search
curl "http://localhost:8000/api/web-search?q=mining+news"

# Create folder
curl -X POST http://localhost:8000/api/folders \
  -H "Content-Type: application/json" \
  -d '{"folder_id":"hr","name":"HR & Recruitment"}'
```

### JavaScript

```javascript
// Chat with fetch
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Show me production data',
    deep_thinking: true
  })
});
const data = await response.json();
console.log(data.response);
```

---

## Rate Limits

No rate limits for local deployment. For ngrok public access, consider implementing authentication.

---

*GeoLogix AI v2.0.0 - Enterprise Intelligence System*
