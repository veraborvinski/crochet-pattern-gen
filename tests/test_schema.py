from data.schema import Pattern, Part, Round, Materials, YarnSpec, Difficulty

def test_pattern_round_trip():
    p = Pattern(
        title="Test Bear",
        description="A small bear",
        difficulty=Difficulty.beginner,
        materials=Materials(
            yarn=[YarnSpec(weight="worsted", amount="100g", color="brown")],
            hook="4.0mm",
        ),
        parts=[Part(
            name="Head",
            make=1,
            rounds=[Round(round=1, instruction="MR, 6 sc", stitch_count=6)],
        )],
    )
    assert p.title == "Test Bear"
    assert p.parts[0].rounds[0].stitch_count == 6
    assert p.freeform is False

def test_pattern_optional_fields_default():
    p = Pattern(
        title="X", description="X", difficulty=Difficulty.beginner,
        materials=Materials(yarn=[], hook="4mm"),
        parts=[],
    )
    assert p.source_url is None
    assert p.author is None
    assert p.tags == []
    assert p.abbreviations == {}
