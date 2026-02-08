import re
import ast
from collections import Counter

def identifier_diversity(code):
    names = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", code)
    if not names:
        return 0
    return len(set(names)) / len(names)

def formatting_consistency(code):
    lines = [l for l in code.splitlines() if l.strip()]
    if not lines:
        return 0
    lengths = [len(l) for l in lines]
    return 1 - (max(lengths) - min(lengths)) / max(lengths)

def logic_density(code):
    try:
        tree = ast.parse(code)
    except:
        return 0

    logic_nodes = (
        ast.If, ast.For, ast.While,
        ast.Try, ast.With, ast.FunctionDef
    )

    logic_count = sum(isinstance(n, logic_nodes) for n in ast.walk(tree))
    line_count = max(len(code.splitlines()), 1)

    return logic_count / line_count
