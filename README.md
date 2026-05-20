# Podcast Intelligence Pipeline

An AI backend that transforms raw podcast audio into structured content intelligence. Upload any audio file and receive a full pipeline output: speaker-diarised transcript, AI-generated show notes with timestamps and quotable moments, chapter markers, a ready-to-use cold open script, and a per-segment episode quality score — all processed locally, no data sent to external servers unless you opt in.

**AI components (pipeline order):** [1] Whisper via faster-whisper — speech-to-text with word-level timestamps. [2] pyannote.audio — speaker diarisation (who said what). [3] Wikipedia API — guest context injection, an agentic decision step where external knowledge is pulled and woven into downstream generation. [4] Claude Sonnet or local Qwen2.5-14B — structured show notes (title, themes, notable moments, quotable lines). [5] Claude / Qwen — chapter detection via topic-shift analysis. [6] Claude / Qwen — cold open writer (30-second spoken hook, constrained away from default "Welcome to..." patterns). [7] Claude / Qwen — episode quality scoring with per-segment flags for pacing, clarity, and information density. Each LLM stage receives the full diarised, speaker-labelled transcript so context is preserved across speakers. Prompt templates live in `/prompts/` — the engineering there is the core judgment call at each stage.

**To run:** `pip install -r requirements_pipeline.txt` → copy `.env.example` to `.env` and add `ANTHROPIC_API_KEY` → `uvicorn api.main:app --reload` → open `http://localhost:8000`. To run fully locally with no API calls: set `LLM_PROVIDER=local` with LM Studio running Qwen2.5-14B on port 1234.

## Use case: health sector

Health organisations produce large volumes of written content — clinical guidelines, patient education, staff communications — that frequently goes unread. Audio is more accessible and more engaging. The same pipeline that processes a podcast episode can be used to convert a recorded clinical briefing into navigable, timestamped audio content with show notes for staff distribution.

The fully local mode (`LLM_PROVIDER=local`) satisfies the NZ Health Information Privacy Code 2020 requirement that voice recordings — classified as biometric PHI — are not processed by external systems. No transcript, no audio, no guest names leave the device. The architecture diagram in `architecture.html` shows both deployment paths and what changes between them.

## Architecture

See `architecture.html` for the full diagram. Two deployment modes, one codebase:

- **Cloud-assisted:** faster-whisper + pyannote (local) → Claude Sonnet API (LLM stages) → Chatterbox TTS (local)
- **Fully local:** same, but Claude → LM Studio + Qwen2.5-14B, Wikipedia → offline Kiwix dump

Switch with: `LLM_PROVIDER=claude` or `LLM_PROVIDER=local`

## Repo structure

```
pipeline/          Seven AI stage modules (one file per stage)
api/               FastAPI backend — upload, job queue, synthesis endpoint
prompts/           Prompt templates — visible, versioned, not hidden in code
frontend/          Single-file HTML/JS UI (Tailwind CDN, no build step)
architecture.html  Architecture diagrams — current vs fully local
DECISIONS.md       Why each major choice was made
```
