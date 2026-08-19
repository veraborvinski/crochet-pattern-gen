import httpx
import os
import re
from bs4 import BeautifulSoup
from data.schema import Pattern, Materials, YarnSpec, Part, Round, Difficulty
from data.normalizer import normalize_to_us

RAVELRY_API = "https://api.ravelry.com"

DIFFICULTY_MAP = [
    (0.0, 1.5, Difficulty.beginner),
    (1.5, 2.5, Difficulty.intermediate),
    (2.5, 5.0, Difficulty.advanced),
]

def _map_difficulty(score: float) -> Difficulty:
    for lo, hi, d in DIFFICULTY_MAP:
        if lo <= score < hi:
            return d
    return Difficulty.intermediate

def _parse_instructions_html(url: str) -> list[Part]:
    try:
        r = httpx.get(url, follow_redirects=True, timeout=10)
        r.raise_for_status()
    except Exception:
        return []
    if "application/pdf" in r.headers.get("content-type", ""):
        print(f"  [skip] PDF at {url} — needs manual processing")
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    for selector in ["div.pattern-instructions", "div.entry-content", "article", "main"]:
        block = soup.select_one(selector)
        if block:
            text = normalize_to_us(block.get_text("\n"))
            return _text_to_parts(text)
    return []

def _text_to_parts(text: str) -> list[Part]:
    rounds = []
    for line in text.splitlines():
        m = re.match(r"[Rr]ound\s*(\d+)[:\s]+(.+?)\((\d+)\)", line.strip())
        if m:
            rounds.append(Round(
                round=int(m.group(1)),
                instruction=m.group(2).strip(),
                stitch_count=int(m.group(3)),
            ))
    if not rounds:
        return []
    return [Part(name="Body", rounds=rounds)]

class RavelryClient:
    def __init__(self, username: str = None, password: str = None):
        self.auth = (
            username or os.environ.get("RAVELRY_USERNAME", ""),
            password or os.environ.get("RAVELRY_PASSWORD", ""),
        )

    def search_free_patterns(
        self, category: str, page: int = 1, page_size: int = 100, fetch_instructions: bool = True
    ) -> list[Pattern]:
        r = httpx.get(
            f"{RAVELRY_API}/patterns/search.json",
            params={
                "craft": "crochet",
                "availability": "free",
                "pc": category,
                "page": page,
                "page_size": page_size,
                "sort": "best",
            },
            auth=self.auth,
        )
        r.raise_for_status()
        patterns = []
        for raw in r.json().get("patterns", []):
            source_url = raw.get("free_download_href") or raw.get("url") or ""
            parts = []
            if fetch_instructions and source_url:
                parts = _parse_instructions_html(source_url)
            hook = ""
            needle_sizes = raw.get("needle_sizes") or []
            if needle_sizes:
                hook = needle_sizes[0].get("us", "")
            patterns.append(Pattern(
                title=raw["name"],
                description=raw.get("notes_plain", raw["name"]),
                source_url=source_url or None,
                author=(raw.get("designer") or {}).get("name"),
                difficulty=_map_difficulty(raw.get("difficulty_average") or 2.0),
                materials=Materials(
                    yarn=[YarnSpec(
                        weight=(raw.get("yarn_weight") or {}).get("name", ""),
                        amount="",
                    )],
                    hook=hook,
                ),
                parts=parts,
                tags=raw.get("tag_names") or [],
            ))
        return patterns
