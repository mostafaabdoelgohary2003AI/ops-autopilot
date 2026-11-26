"""Ops Autopilot web app: run the multi-agent pipeline, browse history, download DOCX."""
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from . import pipeline, db
from .docx_export import export_docx

app = FastAPI(title="Ops Autopilot")
LAST = {}

class Job(BaseModel):
    topic: str

@app.on_event("startup")
def startup():
    os.makedirs("results", exist_ok=True)
    db.init()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run")
def run_job(job: Job):
    result = pipeline.run(job.topic)
    db.save_run(result)
    path = f"results/report_{abs(hash(job.topic)) % 100000}.docx"
    export_docx(result, path)
    LAST["docx"] = path
    return {"metrics": result["metrics"],
            "sections": [{"question": s["facet"], "draft": s.get("draft"), "url": s.get("url")}
                         for s in result["sections"]],
            "docx": "/download"}

@app.get("/download")
def download():
    return FileResponse(LAST.get("docx", ""), filename="ops-autopilot-report.docx")

@app.get("/history")
def get_history():
    return db.history()

@app.get("/", response_class=HTMLResponse)
def index():
    return open("static/index.html").read()
