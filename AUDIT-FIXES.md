# GeoLogix Wiring Audit / Fix Log

This file records the wiring-level fixes applied to make GeoLogix UI and backend work end-to-end. Treat this as the source of truth for critical integration points.

## Critical invariants (do not change without updating counterparts)

- Backend must expose these endpoints:
  - `GET /api/health`
  - `GET /api/stats`
  - `GET /api/search` (query params: `q`, `source`, `limit`)
  - `POST /api/chat` (body accepts both `chat_id` and `conversation_id`)
- UI must use `CONFIG.API_BASE_URL` from `geologix-ai/UI/scripts/shared-utils.js` (avoid hardcoded `http://localhost:8000/...` in variant scripts).
- UI `variant-*.html` files must only reference assets that exist under `geologix-ai/UI/scripts/*` and `geologix-ai/UI/styles/*`.

## Files changed/created (Jan 2026)

### Backend

- `geologix-ai/geologix-backend/Core_System/server.py`
  - Added `GET /api/stats` for UI dashboards.
  - Updated `GET /api/search` to accept `source` and `limit`.
  - Added chat compatibility: `conversation_id` accepted and merged with `chat_id`.
  - Normalized imports (moved `StreamingResponse` import to the top).
- `geologix-ai/geologix-backend/Core_System/mcp_tools.py`
  - Fixed `search_knowledge_base` to map `source` to `KnowledgeEngine.search(sources=...)` and honor `limit`.
  - Implemented archive search wiring via `KnowledgeEngine.search_archives`.
- `geologix-ai/geologix-backend/Core_System/knowledge_engine.py`
  - Added `search_archives(query, tags, limit)`.
- `geologix-ai/geologix-backend/Core_System/ai_agents.py`
  - Fixed tool reference `summarize` -> `summarize_text`.

### UI

- `geologix-ai/UI/scripts/shared-utils.js`
  - `sendChatMessage()` sends both `chat_id` and `conversation_id`.
  - Exposes shared API + utilities on `window.GeoLogixAPI` and `window.GeoLogixUtils`.
- `geologix-ai/UI/variant-5-maximum.html`
  - Loads `scripts/shared-utils.js` before `scripts/variant-5.js`.
- `geologix-ai/UI/scripts/variant-5.js`
  - Uses `CONFIG.API_BASE_URL` (removes hardcoded URLs).
  - Tracks `conversationId` between calls.
- Created missing assets so variants 1-4 always load:
  - `geologix-ai/UI/scripts/variant-1.js`
  - `geologix-ai/UI/scripts/variant-2.js`
  - `geologix-ai/UI/scripts/variant-3.js`
  - `geologix-ai/UI/scripts/variant-4.js`
  - `geologix-ai/UI/styles/variant-1.css`
  - `geologix-ai/UI/styles/variant-2.css`
  - `geologix-ai/UI/styles/variant-3.css`
  - `geologix-ai/UI/styles/variant-4.css`

### PowerShell scripts

- `geologix-ai/start-geologix.ps1`
  - Replaced hardcoded paths with `$PSScriptRoot`-derived paths.
  - Starts backend using `python -m uvicorn Core_System.server:app ...`.
  - Opens UI using `http://localhost:8000/` once health check passes.
- `geologix-ai/start-ngrok.ps1`
  - Supports `-Domain` parameter (or env var `GEOLOGIX_NGROK_DOMAIN`).
  - Checks `ngrok` is available and waits for backend readiness.
  - Falls back to default `ngrok http 8000` if no domain is supplied.
- `geologix-ai/verify-installation.ps1`
  - Replaced hardcoded paths with `$PSScriptRoot`-derived paths.
  - Required package list aligned to `geologix-ai/geologix-backend/Configuration/requirements.txt`.

### Regression checks (to prevent silent breakage)

- `geologix-ai/geologix-backend/tests/test_wiring.py`
  - Verifies UI HTML references point to real files.
  - Verifies backend endpoints `/api/health`, `/api/stats`, `/api/search` respond.

## How to re-validate quickly

From `geologix-ai/geologix-backend`:

- `python -m compileall .`
- `python tests/test_wiring.py`

From `geologix-ai`:

- `./verify-installation.ps1`
- `./start-geologix.ps1`
