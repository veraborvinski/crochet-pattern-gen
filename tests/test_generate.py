import json
from unittest.mock import patch, MagicMock

def test_generate_returns_pattern_and_inspiration():
    mock_pattern_json = json.dumps({
        "title": "Mini Bear", "description": "A tiny bear",
        "difficulty": "beginner",
        "materials": {"yarn": [{"weight": "worsted", "amount": "50g", "color": "brown"}], "hook": "4mm"},
        "parts": [{"name": "Head", "make": 1, "rounds": [
            {"round": 1, "instruction": "MR, 6 sc", "stitch_count": 6}
        ]}],
    })
    mock_similar = [MagicMock(title="Bear", author="Alice",
                              source_url="http://example.com", tags=["amigurumi"])]

    with patch("backend.generate.search_patterns", return_value=mock_similar), \
         patch("backend.generate._llm_generate", return_value=mock_pattern_json):
        from backend.generate import generate_pattern
        pattern, inspiration = generate_pattern("a tiny brown amigurumi bear")

    assert pattern.title == "Mini Bear"
    assert len(inspiration) == 1
    assert inspiration[0]["title"] == "Bear"
    assert inspiration[0]["author"] == "Alice"

def test_generate_inspiration_handles_no_similar():
    mock_pattern_json = json.dumps({
        "title": "Bear", "description": "A bear",
        "difficulty": "beginner",
        "materials": {"yarn": [{"weight": "worsted", "amount": "50g", "color": "brown"}], "hook": "4mm"},
        "parts": [{"name": "Head", "make": 1, "rounds": [
            {"round": 1, "instruction": "MR, 6 sc", "stitch_count": 6}
        ]}],
    })

    with patch("backend.generate.search_patterns", return_value=[]), \
         patch("backend.generate._llm_generate", return_value=mock_pattern_json):
        from backend.generate import generate_pattern
        pattern, inspiration = generate_pattern("bear")

    assert pattern.title == "Bear"
    assert inspiration == []
