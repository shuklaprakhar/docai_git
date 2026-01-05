from rferral_agent.server.app.extractor import _heuristic_extract, extract_json_from_pages


def test_heuristic_extract_basic():
    pages = [
        "Patient: Jane Smith\nDOB: 05/10/1975\nAddress: 500 Elm St",
        "Order:\nItem Code: ABC-123\nPrice: $125.00\nDescription: Knee brace",
    ]
    classes = ["demographics", "order"]
    result = _heuristic_extract(pages, classes)
    assert result["patient"]["name"] == "Jane Smith"
    assert any(o.get("item_code") == "ABC-123" for o in result["orders"]) 


def test_extract_json_from_pages_fallback():
    pages = ["Some text without keys"]
    classes = ["other"]
    res = extract_json_from_pages(pages, classes, prefer_llm=False)
    assert isinstance(res, dict)
