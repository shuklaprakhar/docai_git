import fitz


def extract_text_per_page(pdf_path: str):
    """Return a list of page texts for the given PDF file path."""
    texts = []
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            texts.append(page.get_text())
    except Exception:
        # On failure return empty list - caller should handle
        return []
    return texts
