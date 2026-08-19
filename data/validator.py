from data.schema import Pattern, Part

def _check_stitch_counts(part: Part) -> list[str]:
    errors = []
    for i in range(1, len(part.rounds)):
        prev = part.rounds[i - 1].stitch_count
        curr = part.rounds[i].stitch_count
        if prev > 0 and (curr > prev * 2 + 6 or curr < prev // 2 - 6):
            errors.append(
                f"Part '{part.name}' round {part.rounds[i].round}: "
                f"stitch count {curr} after {prev} looks wrong"
            )
    return errors

def validate_pattern(pattern: Pattern) -> list[str]:
    errors = []
    for part in pattern.parts:
        if not pattern.freeform and not part.rounds:
            errors.append(f"Part '{part.name}' has no rounds")
            continue
        errors.extend(_check_stitch_counts(part))
    return errors
