def ai_assistance_score(lexical, structural, id_div, fmt, logic):
    score = 0

    # Strong AI paraphrasing pattern
    if structural > 70 and lexical < 40:
        score += 0.4

    # AI naming behavior
    if id_div < 0.35:
        score += 0.2

    # AI formatting uniformity
    if fmt > 0.85:
        score += 0.2

    # Dense logic compression
    if logic > 0.15:
        score += 0.2

    return min(score, 1.0)
