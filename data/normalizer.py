import re

_UK_TO_US_TERMS: list[tuple[str, str]] = [
    ("half treble crochet", "half double crochet"),
    ("half treble", "half double crochet"),
    ("double treble crochet", "treble crochet"),
    ("double treble", "treble crochet"),
    ("triple treble", "double treble crochet"),
    ("treble crochet", "double crochet"),
    ("treble", "double crochet"),
    ("double crochet", "single crochet"),
]

_UK_TO_US_ABBR: list[tuple[str, str]] = [
    (r"\bhtr\b", "hdc"),
    (r"\bdc\b", "sc"),
    (r"\btr\b", "dc"),
    (r"\bttr\b", "dtr"),
    (r"\bdtr\b", "tr"),
]

_US_TO_UK_TERMS = [(us, uk) for uk, us in _UK_TO_US_TERMS]
_US_TO_UK_ABBR = [
    (r"\bhdc\b", "htr"),
    (r"\bdtr\b", "ttr"),
    (r"\btr\b", "dtr"),
    (r"\bdc\b", "tr"),
    (r"\bsc\b", "dc"),
]

def _apply(text: str, terms: list[tuple[str, str]], abbr: list[tuple[str, str]]) -> str:
    for uk, us in terms:
        text = re.sub(uk, us, text, flags=re.IGNORECASE)
    for pattern, replacement in abbr:
        text = re.sub(pattern, replacement, text)
    return text

def normalize_to_us(text: str) -> str:
    return _apply(text, _UK_TO_US_TERMS, _UK_TO_US_ABBR)

def convert_us_to_uk(text: str) -> str:
    return _apply(text, _US_TO_UK_TERMS, _US_TO_UK_ABBR)
