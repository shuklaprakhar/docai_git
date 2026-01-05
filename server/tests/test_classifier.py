from rferral_agent.server.app.classifier import _heuristic_classify, classify_page_text


def test_heuristic_prescription():
    text = "This is an Rx: prescription for medication"
    assert _heuristic_classify(text) == "prescription"


def test_heuristic_demographics():
    text = "Patient: John Doe\nDOB: 01/02/1980\nAddress: 123 Main St"
    assert _heuristic_classify(text) == "demographics"


def test_classify_fallback():
    # When no anthropic key is set, classify_page_text should fall back to heuristics
    text = "Order: Item Code 123-ABC"
    assert classify_page_text(text, prefer_llm=False) == "order"
