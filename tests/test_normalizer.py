from data.normalizer import normalize_to_us, convert_us_to_uk

def test_uk_double_crochet_becomes_us_single_crochet():
    assert "sc" in normalize_to_us("dc into next stitch")

def test_uk_treble_becomes_us_double_crochet():
    result = normalize_to_us("3 tr in magic ring")
    assert "dc" in result
    assert "tr" not in result

def test_us_single_crochet_becomes_uk_double_crochet():
    assert "dc" in convert_us_to_uk("6 sc in magic ring")

def test_normalize_is_idempotent_on_us_text():
    us_text = "Round 1: MR, 6 sc (6)"
    assert normalize_to_us(us_text) == us_text

def test_half_double_crochet():
    assert "hdc" in normalize_to_us("2 htr into next st")
