"""
Pipeline orchestrator — chains all seven AI stages and manages job state.

Uses threading for async execution (no Celery needed for single-user demo).
Job state is held in memory — production would use Redis or PostgreSQL.

Pipeline order:
  1. transcribe     — faster-whisper speech-to-text
  2. diarize        — speaker identification
  3. guest_research — Wikipedia context injection (optional)
  4. show_notes     — Claude structured show notes
  5. chapters       — Claude chapter detection
  6. cold_open      — Claude 30-second hook writer
  7. quality_score  — Claude episode quality scoring
"""

import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pipeline.transcribe import transcribe
from pipeline.diarize import diarize, merge_with_transcript
from pipeline.guest_research import research_guest
from pipeline.show_notes import generate_show_notes
from pipeline.chapters import detect_chapters
from pipeline.cold_open import generate_cold_open
from pipeline.quality_score import score_quality

_jobs: dict = {}
_lock = threading.Lock()

STEP_LABELS = {
    "transcribing": "Transcribing audio",
    "diarising": "Identifying speakers",
    "researching_guest": "Researching guest",
    "generating_show_notes": "Generating show notes",
    "detecting_chapters": "Detecting chapters",
    "writing_cold_open": "Writing cold open",
    "scoring_quality": "Scoring quality",
}


class PodcastJob:
    def __init__(self, job_id: str, audio_path: str, guest_name: Optional[str]):
        self.job_id = job_id
        self.audio_path = audio_path
        self.guest_name = guest_name
        self.status = "queued"           # queued | processing | done | failed
        self.current_step: Optional[str] = None
        self.steps_completed: list = []
        self.steps_total: int = 0
        self.results: dict = {}
        self.error: Optional[str] = None
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.completed_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "current_step": self.current_step,
            "current_step_label": STEP_LABELS.get(self.current_step, ""),
            "steps_completed": self.steps_completed,
            "steps_total": self.steps_total,
            "progress_pct": int(
                len(self.steps_completed) / self.steps_total * 100
            ) if self.steps_total else 0,
            "results": self.results,
            "error": self.error,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


def create_job(audio_path: str, guest_name: Optional[str] = None) -> str:
    """Create a new job and start it in a background thread."""
    job_id = str(uuid.uuid4())
    job = PodcastJob(job_id, audio_path, guest_name)

    with _lock:
        _jobs[job_id] = job

    thread = threading.Thread(target=_run, args=(job_id,), daemon=True)
    thread.start()

    return job_id


def get_job(job_id: str) -> Optional[PodcastJob]:
    with _lock:
        return _jobs.get(job_id)


def list_jobs() -> list:
    with _lock:
        return [j.to_dict() for j in _jobs.values()]


def _run(job_id: str) -> None:
    job = _jobs[job_id]
    job.status = "processing"

    steps = [
        ("transcribing", _do_transcribe),
        ("diarising", _do_diarize),
        ("researching_guest", _do_guest_research),
        ("generating_show_notes", _do_show_notes),
        ("detecting_chapters", _do_chapters),
        ("writing_cold_open", _do_cold_open),
        ("scoring_quality", _do_quality_score),
    ]

    # Count active steps (skip guest research if no guest name)
    active = [
        (name, fn) for name, fn in steps
        if not (name == "researching_guest" and not job.guest_name)
    ]
    job.steps_total = len(active)

    # Shared state passed between stages
    ctx: dict = {}

    for step_name, step_fn in active:
        job.current_step = step_name
        print(f"\n[pipeline] Step: {STEP_LABELS[step_name]}")
        try:
            step_fn(job, ctx)
            job.steps_completed.append(step_name)
        except Exception as exc:
            import traceback
            job.error = f"{step_name}: {exc}"
            job.status = "failed"
            print(f"[pipeline] FAILED at {step_name}: {exc}")
            traceback.print_exc()
            return

    job.status = "done"
    job.current_step = None
    job.completed_at = datetime.now(timezone.utc).isoformat()
    print(f"\n[pipeline] Done — job {job_id[:8]}")


def _do_transcribe(job: PodcastJob, ctx: dict) -> None:
    result = transcribe(job.audio_path)
    ctx["transcription"] = result
    job.results["transcription"] = {
        "language": result["language"],
        "duration": result["duration"],
        "segment_count": len(result["segments"]),
        # Include first 5 segments for the UI transcript preview
        "segments_preview": result["segments"][:5],
    }


def _do_diarize(job: PodcastJob, ctx: dict) -> None:
    speaker_segments = diarize(job.audio_path)
    transcript_segs = ctx["transcription"]["segments"]
    merged = merge_with_transcript(transcript_segs, speaker_segments)
    ctx["diarised"] = merged

    # Build readable transcript for the UI
    from pipeline import seconds_to_mmss
    transcript_lines = [
        {
            "timestamp": seconds_to_mmss(seg["start"]),
            "speaker": seg["speaker"],
            "text": seg["text"],
        }
        for seg in merged
    ]
    job.results["transcript"] = {
        "lines": transcript_lines,
        "speaker_count": len(set(s["speaker"] for s in merged)),
    }


def _do_guest_research(job: PodcastJob, ctx: dict) -> None:
    result = research_guest(job.guest_name)
    ctx["guest_context"] = result
    job.results["guest_research"] = result


def _do_show_notes(job: PodcastJob, ctx: dict) -> None:
    result = generate_show_notes(
        ctx["diarised"],
        guest_context=ctx.get("guest_context"),
    )
    job.results["show_notes"] = result


def _do_chapters(job: PodcastJob, ctx: dict) -> None:
    result = detect_chapters(ctx["diarised"])
    job.results["chapters"] = result


def _do_cold_open(job: PodcastJob, ctx: dict) -> None:
    result = generate_cold_open(ctx["diarised"])
    job.results["cold_open"] = result


def _do_quality_score(job: PodcastJob, ctx: dict) -> None:
    result = score_quality(ctx["diarised"])
    job.results["quality_score"] = result
