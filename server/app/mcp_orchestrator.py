from typing import List, Dict, Any
from .ocr import extract_text_per_page
from .classifier import classify_page_text
from .extractor import extract_json_from_pages
from .models import IngestResult, PageClassification


class Orchestrator:
    """Simple orchestrator coordinating OCR -> classification -> extraction.

    This is a minimal MCP-style orchestrator (no external MCP library required for the prototype).
    Agents are synchronous function calls that could be replaced with async workers or MCP agents.
    """

    def __init__(self, prefer_llm: bool = False):
        self.prefer_llm = prefer_llm

    def process_documents(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        results = []
        for path in file_paths:
            pages = extract_text_per_page(path)
            classifications = []
            for i, page_text in enumerate(pages):
                cat = classify_page_text(page_text, prefer_llm=self.prefer_llm)
                classifications.append(PageClassification(page_index=i, category=cat))

            # Extract structured JSON
            classes_list = [c.category for c in classifications]
            extracted = extract_json_from_pages(pages, classes_list, prefer_llm=self.prefer_llm)

            results.append(
                IngestResult(
                    file=path,
                    pages=len(pages),
                    classifications=classifications,
                    extracted=extracted,
                ).dict()
            )

        return results
