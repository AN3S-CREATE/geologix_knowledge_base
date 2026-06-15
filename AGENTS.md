# GeoLogix AI

FastAPI backend + static HTML UI for an enterprise knowledge-management / AI
assistant over a JSON-indexed corpus (documents, emails, archives) with an
optional Ollama LLM for chat.

## Cursor Cloud specific instructions

### Layout (important)

- The **canonical** Python package is `src/geologix` (tests import
  `geologix.core.server`). Run everything with `PYTHONPATH=src`.
- `geologix-ai/geologix-backend/` is an **older duplicate** of the same code.
  Do not run it; its only unique value is the data indexes it ships (see below).
- Dependencies: `src/geologix/config/requirements.txt`. A venv lives at
  `.venv` (gitignored); activate with `. .venv/bin/activate`.

### Data directory (knowledge indexes)

- `src/geologix/config/config.py` resolves the read/write data dir from the
  `GEOLOGIX_DATA_DIR` env var, defaulting to `<repo>/data/runtime` (which does
  **not** contain the real indexes, so search/stats come back empty).
- The real index files (`company_index.json`, `email_index.json`,
  `archive_index.json`, `archive_stats.json`, `knowledge_index.json`,
  ~20k items) live in `geologix-ai/geologix-backend/Data_Directories`.
- To run/search against the real corpus, set:
  `export GEOLOGIX_DATA_DIR="$PWD/geologix-ai/geologix-backend/Data_Directories"`
- Importing the config has a side effect: it `mkdir`s `storage/`, `chroma_db/`,
  `logs/`, `chats/` under the active data dir. Leave these (runtime artifacts);
  don't commit them.

### Run the backend (dev)

```bash
. .venv/bin/activate
export PYTHONPATH=src
export GEOLOGIX_DATA_DIR="$PWD/geologix-ai/geologix-backend/Data_Directories"
python -m uvicorn geologix.core.server:app --host 0.0.0.0 --port 8000 --reload
```

UI: `http://localhost:8000/ui/index.html` (redirects to the copilot variant).
`variant-4-dashboard.html` shows live stats + a knowledge-search box.
Key APIs: `/api/health`, `/api/stats`, `/api/search?q=`, `/api/tools/execute`,
`/api/chat`. See `docs/API_ENDPOINTS.md`.

### Tests

```bash
. .venv/bin/activate
PYTHONPATH=src python -m pytest tests/ -v
```

Tests pass with or without `GEOLOGIX_DATA_DIR` (search just returns empty
results when the indexes aren't found).

### Ollama (only needed for `/api/chat`)

- Chat needs an Ollama server on `http://localhost:11434` with model
  `llama3.2:1b` (see `OLLAMA_MODEL_PRIORITY` in `config.py`). Search, stats,
  tools and the UI all work **without** Ollama.
- Gotcha: the latest Ollama (0.30.x) **segfaults** in this VM during model
  warmup. Pin a stable build: `OLLAMA_VERSION=0.11.4 sh ollama_install.sh`.
  systemd isn't running, so start it manually: `ollama serve` (e.g. in tmux),
  then `ollama pull llama3.2:1b`.

### Lint

- The only configured linter is markdownlint (`.markdownlint.json`) for docs;
  it needs Node/`markdownlint-cli` (not installed by default). There is no
  Python linter config in the repo.
