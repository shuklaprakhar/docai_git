# Referral Agent (rferral_agent)

Lightweight prototype for a multi-agent system that ingests referral PDFs, classifies pages, extracts structured JSON (patient, orders, addresses), and performs basic ENR matching. This repo provides a modular Python backend (FastAPI) and unit tests. Front-end React app is described in the README with next steps.

Quick start (backend):

1. Create and activate a Python virtualenv (macOS zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r server/requirements.txt
```

2. Run the API server:

```bash
uvicorn rferral_agent.server.app.main:app --reload --port 8000
```

3. Ingest a PDF (single-file example using `curl`):

```bash
curl -F "files=@/path/to/referral.pdf" http://127.0.0.1:8000/ingest
```

Notes:
- The code uses `PyMuPDF` for PDF page text extraction. If `ANTHROPIC_API_KEY` is set, LLM-based extraction and classification will be used where available; otherwise heuristic fallbacks are used.
- This is a prototype skeleton. Next steps: add React front-end (`web/`), implement MCP server/agents using the Model Context Protocol library you prefer, add background job queue (Celery/RQ), and add E2E integration tests.
