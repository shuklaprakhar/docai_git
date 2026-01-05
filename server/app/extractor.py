import os
import re
from typing import List, Dict, Any, Optional
from . import db as _db

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")


def _heuristic_extract(pages: List[str], classes: List[str]) -> Dict[str, Any]:
    result = {"patient": {}, "orders": [], "addresses": {}}
    for text, cls in zip(pages, classes):
        t = text or ""
        if cls in ("chart_note", "demographics", "other"):
            m = re.search(r"Patient[:\s]*([A-Z][A-Za-z ,.'-]{2,})", t)
            if m and not result["patient"].get("name"):
                result["patient"]["name"] = m.group(1).strip()
            m2 = re.search(r"DOB[:\s]*(\d{1,2}/\d{1,2}/\d{2,4})", t, re.I)
            if m2 and not result["patient"].get("dob"):
                result["patient"]["dob"] = m2.group(1)

        if cls == "order":
            item = {}
            code = re.search(r"(?:Item Code|Code|HIPC)[:\s]*([A-Z0-9-]+)", t, re.I)
            price = re.search(r"(?:Price|Amount)[:\s]*\$?([0-9.,]+)", t, re.I)
            desc = re.search(r"(?:Description|Desc)[:\s]*([\w ,.#\-\(\)\/:]+)", t, re.I)
            if code:
                item["item_code"] = code.group(1)
            if price:
                item["price"] = price.group(1)
            if desc:
                item["description"] = desc.group(1).strip()
            if item:
                result["orders"].append(item)

        if cls == "demographics":
            addr = re.search(r"(?:Address|Shipping Address|Billing Address)[:\s]*([\w\d ,.#\-\n]+)", t, re.I)
            if addr:
                result["addresses"]["raw"] = addr.group(1).strip()

    return result


def extract_json_from_pages(pages: List[str], classes: List[str], prefer_llm: bool = False) -> Dict[str, Any]:
    """Extract structured JSON from page texts and classifications. If an Anthropic key is set and
    prefer_llm=True, the function will attempt LLM extraction; otherwise falls back to heuristics.
    """
    if prefer_llm and ANTHROPIC_KEY:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=ANTHROPIC_KEY)
            joined = "\n---PAGE---\n".join(pages)
            prompt = (
                "Extract structured JSON with keys: patient{name,dob}, orders[{item_code,hipc_code,price,description}], addresses{billing,shipping}."
                " Return only JSON. Page classifications are: " + ",".join(classes) + "\n\n" + joined
            )
            resp = client.completions.create(model="claude-2.1", prompt=prompt, max_tokens=800)
            text_out = resp.get("completion") or resp.get("text") or ""
            # Try to parse JSON from result
            import json
            try:
                return json.loads(text_out)
            except Exception:
                pass
        except Exception:
            pass

    result = _heuristic_extract(pages, classes)

    # ENR hook: try to match extracted patient to existing patients in DB
    try:
        name = result.get("patient", {}).get("name")
        if name:
            match = _db.find_patient_by_name(name)
            if match:
                # attach matched patient id and record
                result["patient"]["matched"] = {"id": match.get("id"), "name": match.get("name")}
    except Exception:
        # Non-fatal — ENR is best-effort
        pass

    return result
