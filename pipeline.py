"""
Usage: python pipeline.py --target 500
Scrapes crochet patterns from Ravelry, validates, and stores as JSON files.
Requires RAVELRY_USERNAME and RAVELRY_PASSWORD in environment (see .env).
"""
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from data.scraper.ravelry import RavelryClient
from data.validator import validate_pattern

OUTPUT_DIR = Path("data/patterns")

# (name, search_kwargs, fraction)
CATEGORIES = [
    ("amigurumi",  {"query": "amigurumi"},    0.25),
    ("clothing",   {"pc": "clothing"},         0.20),
    ("home",       {"pc": "home"},             0.15),
    ("motifs",     {"query": "granny square"}, 0.15),
    ("lace",       {"query": "lace"},          0.15),
    ("freeform",   {"query": "irish crochet"}, 0.10),
]

def run_pipeline(target: int = 500) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    client = RavelryClient()

    for name, search_kwargs, pct in CATEGORIES:
        cat_target = int(target * pct)
        cat_dir = OUTPUT_DIR / name
        cat_dir.mkdir(exist_ok=True)
        have = len(list(cat_dir.glob("*.json")))
        need = cat_target - have
        if need <= 0:
            print(f"[{name}] already at target ({have})")
            continue
        print(f"[{name}] need {need} more patterns...")
        page = 1
        while need > 0:
            patterns = client.search_free_patterns(
                page=page, page_size=min(need, 100), **search_kwargs
            )
            if not patterns:
                break
            for p in patterns:
                if not p.parts:
                    continue
                errors = validate_pattern(p)
                if errors:
                    print(f"  [skip] {p.title}: {errors[:1]}", flush=True)
                    continue
                fname = cat_dir / f"{abs(hash(p.title + (p.source_url or '')))}.json"
                fname.write_text(p.model_dump_json(indent=2))
                need -= 1
                if need <= 0:
                    break
            page += 1

    total = len(list(OUTPUT_DIR.rglob("*.json")))
    print(f"Done. Total patterns: {total}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect crochet patterns from Ravelry")
    parser.add_argument("--target", type=int, default=500,
                        help="Total number of patterns to collect")
    args = parser.parse_args()
    run_pipeline(args.target)
