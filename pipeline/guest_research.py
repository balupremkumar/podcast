"""
Stage 3: Guest context injection via Wikipedia.

This is the agentic decision point in the pipeline: if a guest name is
provided, the system decides to fetch external context and weave it into
the show notes generation. The output of this stage becomes an additional
input to Stage 4 (show notes).

Wikipedia is free and requires no API keys — zero friction for demos.
Production would use Tavily or Exa for real-time web search.
The pattern matters more than the data source.
"""


def research_guest(guest_name: str) -> dict:
    """
    Research a podcast guest using Wikipedia.

    Returns:
        {
            "found": True,
            "name": "Guest Name",
            "summary": "Brief context paragraph...",
            "url": "https://..."
        }
        or
        {
            "found": False,
            "name": "Guest Name",
            "summary": ""
        }
    """
    if not guest_name or not guest_name.strip():
        return {"found": False, "name": "", "summary": ""}

    print(f"  [guest_research] Researching: {guest_name}")

    try:
        import wikipediaapi
        wiki = wikipediaapi.Wikipedia(
            user_agent="PodcastIntelligencePipeline/1.0",
            language="en",
        )

        # Try exact match first, then title-cased
        page = wiki.page(guest_name)
        if not page.exists():
            page = wiki.page(guest_name.title())

        if not page.exists():
            print(f"  [guest_research] No Wikipedia page found for: {guest_name}")
            return {"found": False, "name": guest_name, "summary": ""}

        # Take first 3 paragraphs (the intro section is usually the most useful)
        summary = _extract_intro(page.text, max_chars=800)

        print(f"  [guest_research] Found: {page.title} ({len(summary)} chars)")
        return {
            "found": True,
            "name": page.title,
            "summary": summary,
            "url": page.fullurl,
        }

    except ImportError:
        print("  [guest_research] wikipediaapi not installed — skipping")
        return {"found": False, "name": guest_name, "summary": ""}
    except Exception as e:
        print(f"  [guest_research] Error: {e} — skipping")
        return {"found": False, "name": guest_name, "summary": ""}


def _extract_intro(text: str, max_chars: int = 800) -> str:
    """Extract the introductory section from Wikipedia article text."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    result = ""
    for para in paragraphs[:4]:
        if len(result) + len(para) <= max_chars:
            result += para + " "
        else:
            break
    return result.strip()
