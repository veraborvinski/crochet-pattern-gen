from data.schema import Pattern, Materials, YarnSpec, Part, Round, Difficulty
from backend.export import pattern_to_pdf

def _bear():
    return Pattern(
        title="Test Bear", description="A small bear", difficulty=Difficulty.beginner,
        materials=Materials(yarn=[YarnSpec(weight="worsted", amount="50g", color="brown")], hook="4mm"),
        abbreviations={"sc": "single crochet", "MR": "magic ring"},
        parts=[Part(name="Head", make=1, rounds=[
            Round(round=1, instruction="MR, 6 sc", stitch_count=6),
        ])],
        source_url="https://example.com", author="Alice",
    )

def test_pdf_export_returns_bytes():
    pdf = pattern_to_pdf(_bear())
    assert isinstance(pdf, bytes)
    assert pdf[:4] == b"%PDF"

def test_uk_pdf_does_not_crash():
    pdf = pattern_to_pdf(_bear(), uk_terms=True)
    assert pdf[:4] == b"%PDF"

def test_inspiration_included():
    inspiration = [{"title": "Source Bear", "author": "Bob", "source_url": "https://x.com"}]
    pdf = pattern_to_pdf(_bear(), inspiration=inspiration)
    assert pdf[:4] == b"%PDF"
