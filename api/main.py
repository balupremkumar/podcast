"""
FastAPI backend for the Podcast Intelligence Pipeline.
Serves the frontend and handles audio upload + job management.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

import requests as _requests
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from pipeline.orchestrator import create_job, get_job, list_jobs

app = FastAPI(title="Podcast Intelligence Pipeline", docs_url="/api/docs")

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
UPLOAD_DIR = Path(tempfile.gettempdir()) / "podcast_pipeline_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg", "audio/mp3", "audio/wav", "audio/wave",
    "audio/x-wav", "audio/mp4", "audio/m4a", "audio/x-m4a",
    "audio/ogg", "audio/webm", "video/webm",
}


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    html_path = FRONTEND_DIR / "index.html"
    if not html_path.exists():
        return HTMLResponse("<h1>Frontend not found</h1>", status_code=404)
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.post("/api/process")
async def process_audio(
    audio: UploadFile = File(...),
    guest_name: Optional[str] = Form(None),
):
    """
    Upload an audio file and start the pipeline.
    Returns a job_id to poll for status.
    """
    content_type = audio.content_type or ""

    # Validate file type
    ext = Path(audio.filename or "").suffix.lower()
    allowed_exts = {".mp3", ".wav", ".m4a", ".mp4", ".ogg", ".webm", ".flac"}
    if ext not in allowed_exts and content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext or content_type}. Use MP3, WAV, M4A, or OGG.",
        )

    # Save to temp file preserving extension
    suffix = ext if ext else ".mp3"
    tmp = tempfile.NamedTemporaryFile(
        dir=UPLOAD_DIR, suffix=suffix, delete=False
    )
    try:
        shutil.copyfileobj(audio.file, tmp)
        tmp.flush()
    finally:
        tmp.close()

    job_id = create_job(tmp.name, guest_name=guest_name or None)

    return JSONResponse({"job_id": job_id, "status": "queued"})


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Poll job status and results."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JSONResponse(job.to_dict())


@app.get("/api/jobs")
async def list_all_jobs():
    return JSONResponse(list_jobs())


@app.post("/api/synthesize")
async def synthesize_cold_open(body: dict):
    """
    Optional: send cold open text to Chatterbox TTS server for audio preview.
    Returns audio/wav bytes if Chatterbox is running, 503 otherwise.
    """
    text = body.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    chatterbox_url = os.environ.get("CHATTERBOX_URL", "http://localhost:8004")

    try:
        resp = _requests.post(
            f"{chatterbox_url}/v1/audio/speech",
            json={
                "model": "chatterbox",
                "input": text,
                "voice": "default",
                "response_format": "wav",
            },
            timeout=120,
        )
        if resp.status_code == 200:
            from fastapi.responses import Response
            return Response(content=resp.content, media_type="audio/wav")
        raise HTTPException(status_code=resp.status_code, detail="TTS synthesis failed")
    except _requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Chatterbox TTS server not running. Start it to enable audio synthesis.",
        )


@app.get("/api/health")
async def health():
    chatterbox_url = os.environ.get("CHATTERBOX_URL", "http://localhost:8004")
    tts_status = "unavailable"
    try:
        r = _requests.get(f"{chatterbox_url}/api/model-info", timeout=3)
        if r.status_code == 200 and r.json().get("loaded"):
            tts_status = "ready"
    except Exception:
        pass

    return {
        "status": "ok",
        "llm_provider": os.environ.get("LLM_PROVIDER", "claude"),
        "tts_backend": tts_status,
        "whisper_model": os.environ.get("WHISPER_MODEL", "base"),
    }
