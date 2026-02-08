import re

def tokenize(code):
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", code)
    return set(tokens)

def lexical_similarity(code_a, code_b):
    tokens_a = tokenize(code_a)
    tokens_b = tokenize(code_b)

    if not tokens_a or not tokens_b:
        return 0.0

    score = len(tokens_a & tokens_b) / len(tokens_a | tokens_b)
    return round(score * 100, 2)
