"""
FastAPI backend for the Podcast Intelligence Pipeline.
Serves the frontend and handles audio upload + job management.
Auto-starts the Chatterbox TTS server on startup.
"""

import asyncio
import os
import shutil
import socket
import subprocess
import sys
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import httpx
import requests as _requests
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from pipeline.orchestrator import create_job, get_job, list_jobs

CHATTERBOX_DIR = Path(__file__).parent.parent / "Chatterbox-TTS-Server"
_tts_process: Optional[subprocess.Popen] = None


def _port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) == 0


def _start_tts():
    global _tts_process
    tts_port = int(os.environ.get("CHATTERBOX_PORT", "8004"))
    if _port_in_use(tts_port):
        return  # already running — don't double-launch

    candidates = [
        CHATTERBOX_DIR / "venv" / "Scripts" / "python.exe",
        CHATTERBOX_DIR / "venv" / "bin" / "python",
        Path(sys.executable),  # system Python — has all deps when venv absent
        CHATTERBOX_DIR / "python_embedded" / "python.exe",  # last resort
    ]
    cb_python = next((p for p in candidates if p.exists()), None)
    if cb_python is None:
        return  # Chatterbox not installed, skip silently

    log_out = open(Path(__file__).parent.parent / "server.log", "w")
    log_err = open(Path(__file__).parent.parent / "server_err.log", "w")
    _tts_process = subprocess.Popen(
        [str(cb_python), "server.py"],
        cwd=str(CHATTERBOX_DIR),
        stdout=log_out,
        stderr=log_err,
    )


def _stop_tts():
    global _tts_process
    if _tts_process and _tts_process.poll() is None:
        _tts_process.terminate()
        try:
            _tts_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _tts_process.kill()
    _tts_process = None


async def _ensure_tts_ready(timeout: int = 90) -> bool:
    """Start TTS if not running, then wait until it responds. Returns True if ready."""
    tts_port = int(os.environ.get("CHATTERBOX_PORT", "8004"))
    if not _port_in_use(tts_port):
        _start_tts()
    chatterbox_url = os.environ.get("CHATTERBOX_URL", "http://localhost:8004")
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        try:
            r = _requests.get(f"{chatterbox_url}/api/model-info", timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        await asyncio.sleep(3)
    return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    _start_tts()
    yield
    _stop_tts()


app = FastAPI(title="Podcast Intelligence Pipeline", docs_url="/api/docs", lifespan=lifespan)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
UPLOAD_DIR = Path(tempfile.gettempdir()) / "podcast_pipeline_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg", "audio/mp3", "audio/wav", "audio/wave",
    "audio/x-wav", "audio/mp4", "audio/m4a", "audio/x-m4a",
    "audio/ogg", "audio/webm", "video/webm",
}


def _serve_page(filename: str) -> HTMLResponse:
    path = FRONTEND_DIR / filename
    if not path.exists():
        return HTMLResponse(f"<h1>{filename} not found</h1>", status_code=404)
    return HTMLResponse(path.read_text(encoding="utf-8"))


@app.get("/", response_class=HTMLResponse)
async def serve_home():
    return _serve_page("index.html")


@app.get("/app", response_class=HTMLResponse)
async def serve_app():
    return _serve_page("app.html")


@app.get("/features", response_class=HTMLResponse)
async def serve_features():
    return _serve_page("features.html")


@app.get("/compliance", response_class=HTMLResponse)
async def serve_compliance():
    return _serve_page("compliance.html")


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

    # Lazy-start: if TTS isn't up, launch it and wait (up to 90s for model load)
    tts_port = int(os.environ.get("CHATTERBOX_PORT", "8004"))
    if not _port_in_use(tts_port):
        ready = await _ensure_tts_ready(timeout=90)
        if not ready:
            raise HTTPException(
                status_code=503,
                detail="Chatterbox TTS server could not start. Check server_err.log.",
            )

    try:
        resp = _requests.post(
            f"{chatterbox_url}/tts",
            json={
                "text": text,
                "voice_mode": "predefined",
                "predefined_voice_id": "Emily.wav",
                "output_format": "wav",
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
            detail="Chatterbox TTS server not running. Check server_err.log for details.",
        )


@app.post("/api/tts/start")
async def tts_start():
    """Manually trigger Chatterbox TTS start and wait for it to become ready."""
    ready = await _ensure_tts_ready(timeout=90)
    if ready:
        return {"status": "ready"}
    raise HTTPException(status_code=503, detail="Chatterbox TTS did not become ready within 90s. Check server_err.log.")


@app.get("/api/health")
async def health():
    chatterbox_url = os.environ.get("CHATTERBOX_URL", "http://localhost:8004")
    tts_status = "unavailable"
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{chatterbox_url}/api/model-info")
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
