"""
Podcast Intelligence Pipeline
Shared utilities for LLM calls and JSON parsing.
"""

import json
import os
import re


def call_llm(prompt: str, system: str = "", max_tokens: int = 2000) -> str:
    """
    Call the configured LLM. Set LLM_PROVIDER=claude (default) or local.

    Claude is the default because structured JSON output needs to be consistent
    across very different episode styles. Smaller models (including local Qwen 14B)
    collapsed the show notes format on long transcripts during testing.
    """
    provider = os.environ.get("LLM_PROVIDER", "claude")

    if provider == "claude":
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6"),
            max_tokens=max_tokens,
            system=system or "You are a helpful assistant. Output valid JSON exactly as requested.",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    elif provider == "local":
        import requests as _requests
        payload = {
            "model": os.environ.get("LM_STUDIO_MODEL", "qwen2.5-14b-instruct"),
            "messages": [
                {
                    "role": "system",
                    "content": system or "You are a helpful assistant. Output valid JSON exactly as requested.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": max_tokens,
        }
        r = _requests.post(
            f"{os.environ.get('LM_STUDIO_URL', 'http://localhost:1234')}/v1/chat/completions",
            json=payload,
            timeout=180,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider!r}. Set to 'claude' or 'local'.")


def parse_json(text: str) -> dict:
    """Extract JSON from LLM response, stripping markdown fences if present."""
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {e}\n\nRaw output:\n{text[:500]}")


def seconds_to_mmss(seconds: float) -> str:
    """Convert float seconds to MM:SS display string."""
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"


def format_transcript_for_llm(segments: list, max_words: int = 6000) -> str:
    """
    Format diarised transcript segments as readable text for LLM input.
    Speaker labels are preserved so the LLM understands conversational structure.
    """
    lines = []
    word_count = 0
    for seg in segments:
        ts = seconds_to_mmss(seg["start"])
        speaker = seg.get("speaker", "SPEAKER")
        text = seg["text"].strip()
        lines.append(f"[{ts}] {speaker}: {text}")
        word_count += len(text.split())
        if word_count >= max_words:
            lines.append(f"\n[Transcript truncated at {max_words} words for processing]")
            break
    return "\n".join(lines)
