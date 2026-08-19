"""
Converts collected patterns into instruction-tuning pairs for fine-tuning.
Run: python training/prepare_dataset.py --input data/patterns --output training/dataset.json
Cost: ~$0.01 per 100 patterns (Claude Haiku for description generation)
"""
import json
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import anthropic
from data.schema import Pattern

_client = anthropic.Anthropic()

def _generate_description(pattern: Pattern) -> str:
    """Generate a natural-language request someone might type."""
    msg = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        messages=[{"role": "user", "content":
            f"Write 1-2 sentences describing what someone would type to request this crochet pattern. "
            f"Sound natural, like you're describing what you want to make.\n"
            f"Title: {pattern.title}\nTags: {', '.join(pattern.tags)}\n"
            f"Difficulty: {pattern.difficulty.value}"
        }],
    )
    text = msg.content[0].text if hasattr(msg.content[0], 'text') else next(b.text for b in msg.content if b.type == "text")
    return text.strip()

def prepare(input_dir: str, output_path: str):
    examples = []
    pattern_files = list(Path(input_dir).rglob("*.json"))
    print(f"Processing {len(pattern_files)} patterns...")
    for i, f in enumerate(pattern_files):
        try:
            pattern = Pattern.model_validate_json(f.read_text(encoding="utf-8"))
            desc = _generate_description(pattern)
            examples.append({
                "instruction": "Generate a crochet pattern for the following description.",
                "input": desc,
                "output": pattern.model_dump_json(),
            })
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(pattern_files)} done")
        except Exception as e:
            print(f"  [skip] {f.name}: {e}")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(examples, indent=2), encoding="utf-8")
    print(f"Dataset saved: {len(examples)} examples → {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/patterns")
    parser.add_argument("--output", default="training/dataset.json")
    args = parser.parse_args()
    prepare(args.input, args.output)
