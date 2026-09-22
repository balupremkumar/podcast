# Podcast Intelligence Pipeline

A backend that turns raw podcast or briefing audio into structured content: a speaker-labelled transcript, AI-generated show notes, chapter markers, a short cold open script, and a per-segment quality score. Processing runs locally by default. Text generation can be routed to a local model or to the Claude API, depending on how sensitive the audio is.

## Who it was for

Built for a New Zealand health-sector organisation, delivered May 2026. The client is not named here, at their request.

Health organisations produce a lot of written content that goes unread: clinical guidelines, patient education material, staff briefings. Audio is more accessible, but most cloud audio tools (transcription, editing, voice tools) send the recording to an external server. Under the NZ Health Information Privacy Code 2020, a voice recording is biometric health information, so that is a real compliance problem, not a hypothetical one. This pipeline runs the audio-handling stages on the client's own hardware, so a recorded clinical briefing can be turned into a timestamped, navigable piece of content without the recording leaving the building.

## Pipeline stages

Seven stages, chained by `pipeline/orchestrator.py`, one module per stage:

1. `pipeline/transcribe.py` - faster-whisper speech-to-text, with word-level timestamps.
2. `pipeline/diarize.py` - pyannote.audio speaker diarisation (who said what). Falls back to a silence-gap heuristic if no HuggingFace token is set.
3. `pipeline/guest_research.py` - optional Wikipedia lookup for guest context. Only runs if a guest name is supplied on upload.
4. `pipeline/show_notes.py` - structured show notes: title, themes, notable moments, quotable lines.
5. `pipeline/chapters.py` - chapter markers, detected from topic shifts in the transcript.
6. `pipeline/cold_open.py` - a 30-second spoken hook script to open the episode.
7. `pipeline/quality_score.py` - a per-segment quality score (pacing, clarity, information density) with specific rewrite suggestions, calibrated to be direct rather than just validating.

Job state (current step, progress, results) is tracked in memory in `pipeline/orchestrator.py`, run on a background thread per upload. That is a reasonable choice for a single-user deployment; a multi-user production version would need a proper job queue and a database instead of in-memory state.

Prompt templates for stages 4 to 7 live in `/prompts/` as plain text files, not embedded in code, so they can be read and changed without touching the pipeline logic.

## Dual LLM backend

Stages 4 to 7 call an LLM through `call_llm()` in `pipeline/__init__.py`. The backend is chosen with the `LLM_PROVIDER` environment variable:

- `LLM_PROVIDER=claude` (default) - calls the Claude Sonnet API. Only the transcript text is sent, never the audio file.
- `LLM_PROVIDER=local` - calls a local Qwen2.5-14B model served by LM Studio. Nothing leaves the machine.

Claude is the default because it held the show notes JSON schema reliably on long transcripts during testing. Smaller local models, including Qwen 14B, sometimes dropped fields (`quotable_moments`, `notable_moments`) on longer episodes with no error raised, just incomplete output. The local path exists for audio that cannot be sent anywhere, and accepts a higher chance of format failures needing a retry as the cost of that. See `DECISIONS.md` for the full reasoning.

## Compliance gate

There is no single compliance-gate function in the code. The compliance position is an architecture decision plus the `LLM_PROVIDER` switch, not a hidden runtime check:

- Transcription and diarisation always run locally, in both modes.
- In the default (`claude`) mode, only transcript text is sent to the Claude API for stages 4 to 7. The audio file itself is never sent.
- In `local` mode, nothing leaves the machine at all.
- Uploaded audio is written to a temporary directory and deleted once a job finishes.
- Job results are held in memory for the session, not written to a persistent database.
- `frontend/compliance.html` sets out what's local and what (if anything) leaves the machine, for a client's privacy or legal reviewer, and lists three deployment tiers: default, fully local, and air-gapped.

In short, "the compliance gate" is what you choose to send externally by setting `LLM_PROVIDER`, backed by the fact that the audio-handling stages never call out regardless of that setting. It is a configuration and documentation control, not a startup assertion that refuses to run if misconfigured.

## Architecture

See `architecture.html` for the full diagram. Two deployment modes, one codebase:

- **Cloud-assisted:** faster-whisper + pyannote (local) -> Claude Sonnet API (stages 4-7) -> Chatterbox TTS (local, for cold open audio preview)
- **Fully local:** same, but Claude -> LM Studio + Qwen2.5-14B, and Wikipedia -> an offline Kiwix dump for guest research

Switch with `LLM_PROVIDER=claude` or `LLM_PROVIDER=local` in `.env`.

## How to run

1. `pip install -r requirements_pipeline.txt`
2. Copy `.env.example` to `.env` and set `ANTHROPIC_API_KEY` (get one at console.anthropic.com)
3. `uvicorn api.main:app --reload`
4. Open `http://localhost:8000`

To run fully locally with no external API calls, set `LLM_PROVIDER=local` in `.env` and have LM Studio running Qwen2.5-14B on port 1234.

Optional: set `HF_TOKEN` in `.env` to use full pyannote diarisation instead of the VAD fallback.

## Tests

There is no automated test suite for the seven-stage pipeline. `test_voice_clone.py`, `test_narrator.py`, `test_conversation.py`, and `test_directml.py` are manual scripts for the separate voice-cloning and TTS side of the project (the Chatterbox TTS server). They are run by hand against a local server to check output quality, not run under pytest or CI.

## Repo structure

```
pipeline/          Seven AI stage modules, one file per stage, plus orchestrator.py
api/               FastAPI backend - upload, job status, synthesis endpoint
prompts/           Prompt templates - visible, versioned, not hidden in code
frontend/          Single-file HTML/JS UI (Tailwind CDN, no build step)
architecture.html  Architecture diagrams - cloud-assisted vs fully local
DECISIONS.md       Why each major technical choice was made
```

## Sample audio

The recordings referenced under `voice_samples/` (not committed to this repo; see `.gitignore`) are the owner's own test recordings, made to exercise the voice-cloning and transcription code. They are not client audio.

## How it was built

The code in this repository was written by AI coding agents, directed and reviewed by Balu Premkumar, who owns the architecture, the review, and the merges.

## Licence

MIT. See `LICENSE`.
