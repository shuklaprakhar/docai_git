from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
import os
from .mcp_orchestrator import Orchestrator
from . import db

app = FastAPI(title="Referral Multi-Agent API")
orchestrator = Orchestrator(prefer_llm=bool(os.getenv("ANTHROPIC_API_KEY")))


@app.on_event("startup")
def startup_event():
    # initialize local DB for approvals and ENR matching
    try:
        db.init_db()
    except Exception:
        pass


@app.post("/ingest")
async def ingest(files: List[UploadFile] = File(...)):
    """Accept one or more PDF files, run the orchestrator, and return structured results."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    saved_paths = []
    for f in files:
        # Save to a temp file
        path = f"/tmp/{f.filename}"
        content = await f.read()
        with open(path, "wb") as fh:
            fh.write(content)
        saved_paths.append(path)

    results = orchestrator.process_documents(saved_paths)
    return {"status": "ok", "results": results}


@app.post("/approve")
async def approve(payload: dict):
    """Accept finalized extracted JSON and persist patient and orders.

    Payload example:
    {
      "file": "/tmp/referral.pdf",
      "extracted": { ... },
      "approver": "user@example.com"
    }
    """
    extracted = payload.get("extracted")
    if not extracted:
        raise HTTPException(status_code=400, detail="Missing extracted payload")

    patient = extracted.get("patient") or {}
    orders = extracted.get("orders") or []

    # Save patient (if present)
    pid = None
    if patient:
        pid = db.save_patient(patient)

    # Save orders
    saved_orders = []
    for o in orders:
        oid = db.save_order(o, patient_id=pid)
        saved_orders.append(oid)

    return {"status": "ok", "patient_id": pid, "orders_saved": len(saved_orders)}
