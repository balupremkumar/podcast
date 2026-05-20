# Architecture Decisions

**faster-whisper over openai-whisper**
faster-whisper runs 4× faster on CPU with identical accuracy. Word-level timestamps are non-negotiable — they're what makes chapter detection point to the actual moment rather than approximating from paragraph boundaries. The base model is ~150MB and handles most podcast audio well; large-v3 would be better for accented speech or noisy environments.

**Claude Sonnet for all generation steps, not a smaller model**
Structured JSON output needs to be consistent across very different episode styles — high-energy interviews, slow solo narration, technical deep-dives. During testing, smaller models (including local Qwen 14B) collapsed the show notes format on long transcripts: the `notable_moments` array would flatten into the description, and `quotable_moments` would disappear entirely. Sonnet maintained the schema reliably. The cost difference is ~$0.02 per episode — trivial against the value. If data sovereignty matters more than reliability (e.g. health sector deployment), set `LLM_PROVIDER=local` and accept occasional format failures with retry logic.

**Dual LLM backend (LLM_PROVIDER=claude|local)**
Same env-var pattern used for the TTS backend in the voice generation side of this project (`TTS_BACKEND=local|azure`). Consistent architectural principle: backend selection via environment, not code changes. Lets you swap in a local Qwen model for air-gapped deployments without touching application code.

**pyannote.audio with VAD fallback, not WhisperX**
pyannote 3.1 gives professional-grade diarisation but requires a HuggingFace token and model licence acceptance — extra friction for a first run. The VAD fallback detects silence gaps > 1.5s and alternates speaker labels. It's primitive: it only works on structured interviews where speakers clearly alternate. WhisperX would be a better production fallback (combines both in one package) but adds a 2GB+ model download. Set `HF_TOKEN` in `.env` for pyannote — the code will use it automatically.

**Wikipedia for guest research, not a search API**
Wikipedia's API is free, requires no key, and adds zero setup friction. The point of this stage isn't the data source — it's the pattern: external context gets injected into the show notes prompt as a structured addition, letting the LLM weave it into the description rather than just appending a bio paragraph. Production would replace Wikipedia with Tavily or Exa for real-time web search. The `research_guest()` function has a clear interface; swapping the source is a one-function change.

**Prompts in /prompts directory, not embedded strings**
The prompt is the highest-leverage engineering in this pipeline. Keeping it in a versioned, readable file treats it like code — not a configuration string. The most significant prompt iteration was in `show_notes.txt`: the first version asked for "key insights" and produced generic summaries. Adding "NOT generic" wasn't enough. What worked: asking for "the most surprising or counterintuitive thing" AND providing a bad example to avoid ("key insights" → bad, "why most X do Y wrong" → good). Explicit negative examples outperform positive instructions for breaking default LLM patterns.

**Threads not Celery for job management**
Celery + Redis is the right production choice for multi-user concurrent jobs (see the TTS generation side of this project). For a single-user demo, threading is simpler, has no additional process to manage, and makes the code readable. The `orchestrator.py` job state is in-memory; a production version would persist to PostgreSQL.
