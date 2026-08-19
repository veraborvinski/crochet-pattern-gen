from data.schema import Pattern, Part, Round, Materials, YarnSpec, Difficulty
from data.validator import validate_pattern

def _make_pattern(**kwargs) -> Pattern:
    defaults = dict(
        title="Test", description="Test", difficulty=Difficulty.beginner,
        materials=Materials(yarn=[YarnSpec(weight="worsted", amount="50g")], hook="4mm"),
        abbreviations={"sc": "single crochet", "inc": "increase", "MR": "magic ring"},
        parts=[Part(name="Body", rounds=[
            Round(round=1, instruction="MR, 6 sc", stitch_count=6),
            Round(round=2, instruction="inc in each sc", stitch_count=12),
        ])],
    )
    defaults.update(kwargs)
    return Pattern(**defaults)

def test_valid_pattern_returns_no_errors():
    assert validate_pattern(_make_pattern()) == []

def test_impossible_stitch_count_jump_flagged():
    p = _make_pattern(parts=[Part(name="Body", rounds=[
        Round(round=1, instruction="MR, 6 sc", stitch_count=6),
        Round(round=2, instruction="inc in each sc", stitch_count=100),
    ])])
    errors = validate_pattern(p)
    assert any("stitch count" in e.lower() for e in errors)

def test_freeform_skips_round_validation():
    p = _make_pattern(freeform=True, parts=[Part(name="Motif", rounds=[])])
    assert validate_pattern(p) == []

def test_empty_rounds_on_non_freeform_flagged():
    p = _make_pattern(parts=[Part(name="Body", rounds=[])])
    errors = validate_pattern(p)
    assert any("no rounds" in e.lower() for e in errors)
