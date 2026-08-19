from unittest.mock import patch, MagicMock
from data.scraper.ravelry import RavelryClient

MOCK_SEARCH = {
    "patterns": [{
        "id": 123,
        "name": "Strawberry Amigurumi",
        "designer": {"name": "TestUser"},
        "difficulty_average": 1.5,
        "free": True,
        "free_download_href": "https://example.com/pattern",
        "pattern_categories": [{"name": "Toys"}],
        "yarn_weight": {"name": "Worsted"},
        "needle_sizes": [{"us": "G-6 (4.0 mm)"}],
        "tag_names": ["amigurumi", "fruit"],
        "notes_plain": "A cute strawberry",
    }]
}

def test_search_returns_patterns():
    client = RavelryClient("user", "pass")
    with patch("httpx.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_SEARCH
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        results = client.search_free_patterns("amigurumi", page=1, fetch_instructions=False)
    assert len(results) == 1
    assert results[0].title == "Strawberry Amigurumi"
    assert results[0].author == "TestUser"
    assert results[0].source_url == "https://example.com/pattern"
    assert results[0].tags == ["amigurumi", "fruit"]
