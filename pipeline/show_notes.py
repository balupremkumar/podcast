"""
Stage 4: AI-generated show notes using structured prompt engineering.

The prompt engineering here is the core judgment call:
- Ask for specific fields (title, description, themes, timestamps, quotes)
- Tell it what NOT to do (don't list every topic, don't be generic)
- Give it a bad example to avoid
- Inject guest context from Stage 3 if available

This is where the pipeline becomes useful rather than just functional.
"""

from pathlib import Path
from pipeline import call_llm, parse_json, format_transcript_for_llm

_PROMPT = (Path(__file__).parent.parent / "prompts" / "show_notes.txt").read_text()


def generate_show_notes(diarised_segments: list, guest_context: dict = None) -> dict:
    """
    Generate structured show notes from diarised transcript.

    Args:
        diarised_segments: Output from diarize.merge_with_transcript()
        guest_context: Optional output from guest_research.research_guest()

    Returns:
        {
            "title": "...",
            "description": "...",
            "key_themes": [...],
            "notable_moments": [{"timestamp": "MM:SS", "description": "..."}, ...],
            "quotable_moments": [{"timestamp": "MM:SS", "quote": "...", "context": "..."}, ...],
            "guest_background": "..."  # optional
        }
    """
    print("  [show_notes] Generating show notes...")

    transcript_text = format_transcript_for_llm(diarised_segments)

    guest_section = ""
    if guest_context and guest_context.get("found"):
        guest_section = (
            f"GUEST CONTEXT (from research, weave into the description naturally):\n"
            f"Name: {guest_context['name']}\n"
            f"Summary: {guest_context['summary']}\n"
        )

    prompt = (
        _PROMPT
        .replace("{{TRANSCRIPT}}", transcript_text)
        .replace("{{GUEST_CONTEXT}}", guest_section)
    )

    raw = call_llm(prompt, max_tokens=2000)
    result = parse_json(raw)

    print(f"  [show_notes] Generated: title='{result.get('title', '?')[:50]}'")
    return result
