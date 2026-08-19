import json
import os
import anthropic
from data.schema import Pattern
from backend.db import search_patterns

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client

_SYSTEM = (
    "You are a crochet pattern designer. Generate complete, accurate crochet patterns as JSON. "
    "Use US crochet terminology only. Ensure stitch counts are mathematically correct per round. "
    "Return ONLY valid JSON — no markdown, no explanation."
)

_SCHEMA_HINT = """{
  "title": "string", "description": "string", "difficulty": "beginner|intermediate|advanced",
  "materials": {"yarn": [{"weight":"string","amount":"string","color":"string"}], "hook":"string", "notions":[]},
  "gauge": "string", "abbreviations": {"sc":"single crochet"}, "assembly": "string",
  "tags": [], "freeform": false,
  "parts": [{"name":"string","make":1,"rounds":[{"round":1,"instruction":"string","stitch_count":6}]}]
}"""

def _llm_generate(description: str, examples: list[Pattern]) -> str:
    example_text = "\n\n".join(
        f"Example:\n{json.dumps(p.model_dump(exclude={'id'}), indent=2)}"
        for p in examples[:3]
    )
    msg = _get_client().messages.create(
        model="claude-sonnet-5",
        max_tokens=4096,
        system=_SYSTEM,
        messages=[{"role": "user", "content":
            f"Generate a crochet pattern for: {description}\n\n"
            f"Return JSON matching this schema:\n{_SCHEMA_HINT}\n\n"
            f"Reference patterns:\n{example_text}"
        }],
    )
    return next(b.text for b in msg.content if b.type == "text")

def generate_pattern(description: str) -> tuple[Pattern, list[dict]]:
    similar = search_patterns(description, k=5)
    raw_json = _llm_generate(description, similar)
    pattern = Pattern.model_validate_json(raw_json)
    inspiration = [
        {"title": p.title, "author": p.author, "source_url": p.source_url}
        for p in similar
    ]
    return pattern, inspiration
