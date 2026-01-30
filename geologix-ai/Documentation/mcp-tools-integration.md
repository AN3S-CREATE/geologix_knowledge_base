# MCP Tools Integration Guide

## Overview
The **Model Context Protocol (MCP)** tools enable GeoLogix AI to perform actions beyond simple text generation. Tools are implemented in `geologix-backend/Core_System/mcp_tools.py` and exposed through the backend API.

The backend exposes:
- `GET /api/tools` to list available tools
- `POST /api/tools/execute` to execute a tool by name

## Available Tools

GeoLogix currently exposes **34 MCP tools** grouped into categories:

- **Knowledge**: `search_knowledge_base`, `read_document`, `search_archives`, `get_archive_summary`
- **Web**: `web_search`, `search_industry_news`
- **Analysis**: `deep_analyze`, `swot_analysis`, `risk_assessment`, `root_cause_analysis`
- **Forecasting**: `forecast`, `calculate_growth`, `calculate_roi`, `calculate_breakeven`
- **Utility**: `calculator`
- **Chat**: `list_chats`, `get_chat_history`, `create_folder`, `list_folders`, `move_chat`
- **Memory**: `remember_fact`, `recall_facts`, `remember_entity`, `get_entity`, `memory_stats`
- **Extractors**: `extract_entities`, `analyze_sentiment`, `summarize_text`, `extract_timeline`, `compare_documents`
- **Agents**: `analyze_intent`, `create_plan`, `execute_plan`, `suggest_followups`

### `search_knowledge_base`
- **Purpose**: Retrieves information from the indexed company documents, emails, strategic knowledge, and archives.
- **Trigger**: "Search for...", "Find information about..."
- **Parameters**:
  - `query` (string)
  - `source` (string, optional: `all|documents|emails|knowledge|archives`)

### `read_document`
- **Purpose**: Reads the full content of a specific file.
- **Trigger**: "Read file...", "What does [filename] say?"
- **Parameters**: `file_path` (string)
- **Note**: Strictly read-only to preserve data integrity.

### `calculator`
- **Purpose**: Performs mathematical evaluations.
- **Trigger**: "Calculate...", "What is X + Y?"
- **Parameters**: `expression` (string)

## Executing Tools via API

Use `GET /api/tools` to discover tool names and parameters.

Example:

```
POST /api/tools/execute
Content-Type: application/json
```

```json
{
  "tool_name": "calculator",
  "params": { "expression": "(100+50)*2" }
}
```

## Developer Reference
To add new tools, modify `geologix-backend/Core_System/mcp_tools.py`.

```python
{
    "name": "new_tool_name",
    "description": "Description of what it does",
    "parameters": {"param": "type"}
}
```
