"""
Stage 5: Auto-detect chapter markers by finding topic shifts in the transcript.

Getting this right is harder than it looks. The main failure mode is
over-segmentation — the LLM wants to create a chapter for every paragraph.
The prompt explicitly constrains minimum gap (3 minutes) and total count.
"""

from pathlib import Path
from pipeline import call_llm, parse_json, format_transcript_for_llm

_PROMPT = (Path(__file__).parent.parent / "prompts" / "chapters.txt").read_text()


def detect_chapters(diarised_segments: list) -> list:
    """
    Detect topic-shift chapter markers.

    Returns:
        [
            {
                "timestamp_seconds": 0,
                "timestamp_display": "0:00",
                "title": "Introduction",
                "summary": "..."
            },
            ...
        ]
    """
    print("  [chapters] Detecting chapter markers...")

    transcript_text = format_transcript_for_llm(diarised_segments)
    prompt = _PROMPT.replace("{{TRANSCRIPT}}", transcript_text)

    raw = call_llm(prompt, max_tokens=1500)
    chapters = parse_json(raw)

    if not isinstance(chapters, list):
        chapters = chapters.get("chapters", [])

    # Validate and clean up
    cleaned = []
    for ch in chapters:
        if isinstance(ch, dict) and "title" in ch:
            cleaned.append(
                {
                    "timestamp_seconds": int(ch.get("timestamp_seconds", 0)),
                    "timestamp_display": ch.get("timestamp_display", "0:00"),
                    "title": ch["title"],
                    "summary": ch.get("summary", ""),
                }
            )

    print(f"  [chapters] Found {len(cleaned)} chapters")
    return cleaned
