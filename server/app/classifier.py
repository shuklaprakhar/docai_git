import os
from typing import Optional

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")


def _heuristic_classify(text: str) -> str:
    t = (text or "").lower()
    if "prescription" in t or "rx" in t:
        return "prescription"
    if "chart note" in t or "progress note" in t or "clinical" in t:
        return "chart_note"
    if "order" in t or "hipc" in t or "item code" in t:
        return "order"
    if "dob" in t or "date of birth" in t or "address" in t or "patient" in t:
        return "demographics"
    return "other"


def classify_page_text(text: str, prefer_llm: bool = False) -> str:
    """Classify a page into categories. If `ANTHROPIC_API_KEY` is set and prefer_llm=True,
    an LLM can be used (optional). Otherwise uses heuristics.
    """
    if prefer_llm and ANTHROPIC_KEY:
        try:
            # Use anthropic if available — keep call optional and tolerant of errors
            from anthropic import Anthropic
            client = Anthropic(api_key=ANTHROPIC_KEY)
            prompt = (
                "Classify the following page text into one of: chart_note, prescription, demographics, order, other.\n\n"
                f"Page text:\n{text[:2000]}"
            )
            resp = client.completions.create(model="claude-2.1", prompt=prompt, max_tokens=20)
            out = resp.get("completion") or resp.get("text") or ""
            out_low = out.lower()
            for cat in ("chart_note", "prescription", "demographics", "order", "other"):
                if cat in out_low:
                    return cat
        except Exception:
            pass

    return _heuristic_classify(text)
