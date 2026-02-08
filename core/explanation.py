def generate_explanation(
    file_a,
    file_b,
    lexical,
    structural,
    ai_score,
    id_div,
    fmt,
    logic
):
    lines = []

    # Header
    lines.append(f"Comparison between `{file_a}` and `{file_b}`.")

    # Structural reasoning
    if structural >= 80:
        lines.append(
            f"Very high structural similarity ({structural}%) indicates reused program logic."
        )
    elif structural >= 60:
        lines.append(
            f"Moderate structural similarity ({structural}%) suggests similar control flow."
        )
    else:
        lines.append(
            f"Low structural similarity ({structural}%) indicates different program structures."
        )

    # Lexical reasoning
    if lexical >= 80:
        lines.append(
            f"High lexical similarity ({lexical}%) suggests direct copying."
        )
    elif lexical >= 40:
        lines.append(
            f"Moderate lexical similarity ({lexical}%) suggests partial reuse of identifiers."
        )
    else:
        lines.append(
            f"Low lexical similarity ({lexical}%) suggests renaming or rewriting of identifiers."
        )

    # -------- AI-SPECIFIC SIGNALS --------
    lines.append("AI-assisted pattern analysis:")

    if structural > 70 and lexical < 40:
        lines.append(
            "• High structural but low lexical similarity is a common AI paraphrasing pattern."
        )

    if id_div < 0.35:
        lines.append(
            f"• Low identifier diversity ({round(id_div, 2)}) indicates generic naming behavior."
        )
    else:
        lines.append(
            f"• Identifier diversity ({round(id_div, 2)}) appears human-like."
        )

    if fmt > 0.85:
        lines.append(
            f"• High formatting consistency ({round(fmt, 2)}) suggests automated code styling."
        )
    else:
        lines.append(
            f"• Formatting consistency ({round(fmt, 2)}) appears natural."
        )

    if logic > 0.15:
        lines.append(
            f"• High logic density ({round(logic, 2)}) indicates compact, AI-style logic generation."
        )
    else:
        lines.append(
            f"• Logic density ({round(logic, 2)}) is within normal human range."
        )

    # Final AI inference
    if ai_score >= 0.7:
        lines.append(
            f"Overall AI-assistance score is high ({round(ai_score, 2)}), indicating AI-assisted plagiarism."
        )
    elif ai_score >= 0.4:
        lines.append(
            f"Overall AI-assistance score is moderate ({round(ai_score, 2)}), suggesting possible AI assistance."
        )
    else:
        lines.append(
            f"Overall AI-assistance score is low ({round(ai_score, 2)}), indicating likely human-written code."
        )

    return lines
