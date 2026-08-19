from fpdf import FPDF
from data.schema import Pattern
from data.normalizer import convert_us_to_uk


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

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, pattern.title, ln=True)

    # Meta
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    diff = pattern.difficulty.value.capitalize()
    pdf.cell(0, 6, f"Difficulty: {diff}  |  Hook: {pattern.materials.hook}  |  Gauge: {pattern.gauge or 'Not specified'}", ln=True)

    # Attribution
    if pattern.author or pattern.source_url:
        attr = f"Pattern by {pattern.author or 'Unknown'}"
        if pattern.source_url:
            attr += f"  -  {pattern.source_url}"
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(0, 5, attr, ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    def section(title: str) -> None:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_font("Helvetica", "", 10)

    # Materials
    section("Materials")
    for yarn in pattern.materials.yarn:
        line = f"  * {yarn.weight.capitalize()} weight yarn"
        if yarn.color:
            line += f", {yarn.color}"
        if yarn.amount:
            line += f" ({yarn.amount})"
        pdf.cell(0, 5, line, ln=True)
    pdf.cell(0, 5, f"  * Crochet hook: {pattern.materials.hook}", ln=True)
    for notion in pattern.materials.notions:
        pdf.cell(0, 5, f"  * {notion}", ln=True)

    # Abbreviations
    if pattern.abbreviations:
        section("Abbreviations")
        abbr_line = ", ".join(f"{k}: {v}" for k, v in pattern.abbreviations.items())
        pdf.multi_cell(0, 5, abbr_line)

    # Parts
    for part in pattern.parts:
        heading = part.name
        if part.make > 1:
            heading += f" (make {part.make})"
        section(heading)
        for r in part.rounds:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(18, 5, f"Rnd {r.round}")
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 5, r.instruction, ln=True)

    # Assembly
    if pattern.assembly:
        section("Assembly")
        pdf.multi_cell(0, 5, pattern.assembly)

    # Inspiration
    if inspiration:
        pdf.ln(4)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(120, 120, 120)
        sources = ", ".join(
            f"{s['title']}{(' by ' + s['author']) if s.get('author') else ''}"
            for s in inspiration
        )
        pdf.multi_cell(0, 5, f"Inspired by: {sources}")

    return bytes(pdf.output())
