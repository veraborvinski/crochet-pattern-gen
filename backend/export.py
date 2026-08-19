from pathlib import Path
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from data.schema import Pattern
from data.normalizer import convert_us_to_uk

_env = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"))

def pattern_to_pdf(
    pattern: Pattern,
    uk_terms: bool = False,
    inspiration: list[dict] | None = None,
) -> bytes:
    if uk_terms:
        pattern = pattern.model_copy(deep=True)
        for part in pattern.parts:
            for r in part.rounds:
                r.instruction = convert_us_to_uk(r.instruction)
    template = _env.get_template("pattern.html")
    html = template.render(pattern=pattern, inspiration=inspiration or [])
    return HTML(string=html).write_pdf()
