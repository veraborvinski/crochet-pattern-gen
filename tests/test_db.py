import os
import tempfile
import pytest

# Use temp DB for tests — set before importing db
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["SQLITE_PATH"] = _tmp.name

from data.schema import Pattern, Materials, YarnSpec, Part, Round, Difficulty
from backend.db import store_pattern, search_patterns, get_pattern_by_id

def _pattern(title="Bear"):
    return Pattern(
        title=title,
        description=f"A small {title.lower()} amigurumi",
        difficulty=Difficulty.beginner,
        materials=Materials(yarn=[YarnSpec(weight="worsted", amount="50g")], hook="4mm"),
        parts=[Part(name="Body", rounds=[Round(round=1, instruction="MR, 6 sc", stitch_count=6)])],
        tags=["amigurumi"],
    )

def test_store_and_retrieve():
    p = _pattern("TestBear")
    pid = store_pattern(p)
    retrieved = get_pattern_by_id(pid)
    assert retrieved is not None
    assert retrieved.title == "TestBear"

def test_store_returns_consistent_id():
    p = _pattern("ConsistentBear")
    pid1 = store_pattern(p)
    pid2 = store_pattern(p)
    assert pid1 == pid2

def test_search_returns_stored_pattern():
    p = _pattern("Strawberry")
    store_pattern(p)
    results = search_patterns("strawberry amigurumi", k=5)
    assert any(r.title == "Strawberry" for r in results)

def test_get_missing_returns_none():
    assert get_pattern_by_id("doesnotexist") is None
