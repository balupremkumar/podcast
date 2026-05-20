"""
Stage 1: Speech-to-text transcription using faster-whisper.

faster-whisper runs 4x faster than openai-whisper on CPU with identical accuracy.
Word-level timestamps are critical — they're what makes chapter detection point
to the right place in the audio rather than approximating.
"""

import os
from pathlib import Path


def transcribe(audio_path: str) -> dict:
    """
    Transcribe audio to text with word-level timestamps.

    Returns:
        {
            "language": "en",
            "duration": 180.5,
            "segments": [
                {
                    "start": 0.0,
                    "end": 4.5,
                    "text": "Welcome to the show.",
                    "words": [{"word": "Welcome", "start": 0.0, "end": 0.6}, ...]
                },
                ...
            ]
        }
    """
    from faster_whisper import WhisperModel

    model_size = os.environ.get("WHISPER_MODEL", "base")
    print(f"  [transcribe] Loading Whisper model: {model_size}")

    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print(f"  [transcribe] Transcribing: {Path(audio_path).name}")
    raw_segments, info = model.transcribe(
        audio_path,
        word_timestamps=True,
        language=None,  # auto-detect
        beam_size=5,
        vad_filter=True,  # skip silence
        vad_parameters={"min_silence_duration_ms": 500},
    )

    segments = []
    for seg in raw_segments:
        words = []
        if seg.words:
            words = [
                {"word": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2)}
                for w in seg.words
            ]
        segments.append(
            {
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": seg.text.strip(),
                "words": words,
            }
        )

    print(f"  [transcribe] Done: {len(segments)} segments, {info.duration:.1f}s, lang={info.language}")

    return {
        "language": info.language,
        "duration": round(info.duration, 2),
        "segments": segments,
    }
