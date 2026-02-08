def classify_plagiarism(lexical, structural, ai_score):
    if lexical > 80 and structural > 80:
        return "Direct Copy"

    if ai_score >= 0.7:
        return "AI-Assisted Plagiarism"

    if lexical < 35 and structural < 35:
        return "Likely Original"

    return "Moderate Similarity"
