"""
Stage 7: Episode quality scoring — the second surprise feature.

This is what a producer would tell the host after listening: where did the
energy drop, which segments should be cut, what worked well.

The prompt is calibrated to be direct rather than validating. Default LLM
behaviour is too positive. "Be honest, the host wants to improve" consistently
produces more useful output than "provide constructive feedback".
"""

from pathlib import Path
from pipeline import call_llm, parse_json, format_transcript_for_llm

_PROMPT = (Path(__file__).parent.parent / "prompts" / "quality_score.txt").read_text()


def score_quality(diarised_segments: list) -> dict:
    """
    Score the episode across four dimensions and flag weak segments.

    Returns:
        {
            "scores": {
                "information_density": 7,
                "pacing": 6,
                "clarity": 8,
                "memorable_moments": 5
            },
            "overall": 6.5,
            "flags": [
                {
                    "timestamp": "MM:SS",
                    "duration_seconds": 45,
                    "issue": "...",
                    "severity": "high|medium|low",
                    "suggestion": "..."
                }
            ],
            "top_strength": "...",
            "top_improvement": "..."
        }
    """
    print("  [quality_score] Scoring episode quality...")

    transcript_text = format_transcript_for_llm(diarised_segments)
    prompt = _PROMPT.replace("{{TRANSCRIPT}}", transcript_text)

    raw = call_llm(prompt, max_tokens=1500)
    result = parse_json(raw)

    overall = result.get("overall")
    if overall is None:
        scores = result.get("scores", {})
        if scores:
            result["overall"] = round(sum(scores.values()) / len(scores), 1)

    flags = result.get("flags", [])
    print(f"  [quality_score] Score: {result.get('overall', '?')}/10, {len(flags)} flags")
    return result
