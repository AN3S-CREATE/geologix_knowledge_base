# Professional AI Setup Guide

## AI Provider Overview
GeoLogix AI supports two local inference providers:
- **Ollama** (default)
- **LM Studio** (optional fallback)

The active provider is configured in `geologix-backend/Configuration/config.py` via `AI_PROVIDER`.

---

## Ollama (Default)

### 1. Start Ollama
Ensure Ollama is running on the default port `11434`:

```bash
ollama serve
```

### 2. Ensure the model is available
The default backend model is `llama3:latest`.

```bash
ollama pull llama3:latest
```

### 3. Verification

```bash
curl http://localhost:11434/api/tags
curl http://localhost:8000/api/ai/status
```

---

## LM Studio (Fallback)

### 1. Installation
1. Download LM Studio from [lmstudio.ai](https://lmstudio.ai).
2. Install and launch the application.

### 2. Model Selection
We recommend the **Llama 3.1 8B Instruct** model for a good balance of quality and speed.
- **Search**: "Llama 3.1 8B Instruct"
- **Quantization**: `Q4_K_M` (Recommended) or `Q5_K_M`

### 3. Configuration
1. Navigate to the **Local Server** tab in LM Studio.
2. **Port**: Set to `1234` (default)
3. Click **Start Server**

### 4. Verification
Run the backend checks:

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/ai/status
```
