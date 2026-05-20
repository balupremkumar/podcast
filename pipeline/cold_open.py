"""
Stage 6: Cold open generator — the surprise feature.

A cold open is a 30-second spoken hook that plays before any music or intro.
Professional podcasters write these manually after listening to the whole episode.
This stage automates it by finding the most compelling moment and scripting around it.

The constraint "do NOT start with Welcome to..." exists because every LLM
defaults to it. Explicit negative instructions outperform positive instructions
for breaking default patterns.
"""

from pathlib import Path
from pipeline import call_llm, parse_json, format_transcript_for_llm

_PROMPT = (Path(__file__).parent.parent / "prompts" / "cold_open.txt").read_text()


def generate_cold_open(diarised_segments: list) -> dict:
    """
    Write a 30-second cold open hook from the transcript.

    Returns:
        {
            "cold_open": "The spoken text...",
            "hook_moment": "MM:SS",
            "estimated_words": 75
        }
    """
    print("  [cold_open] Writing cold open hook...")

    transcript_text = format_transcript_for_llm(diarised_segments)
    prompt = _PROMPT.replace("{{TRANSCRIPT}}", transcript_text)

    raw = call_llm(prompt, max_tokens=500)
    result = parse_json(raw)

    text = result.get("cold_open", "")
    word_count = len(text.split())
    result["estimated_words"] = word_count

    print(f"  [cold_open] Generated {word_count}-word hook (hook at {result.get('hook_moment', '?')})")
    return result
