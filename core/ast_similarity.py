import tokenize
import io

def ast_similarity(code_a, code_b):
    if not code_a or not code_b:
        return 0.0

    def normalize(code):
        tokens = []
        try:
            for tok in tokenize.generate_tokens(io.StringIO(code).readline):
                tok_type = tok.type
                tok_val = tok.string

                # ignore whitespace, comments, newlines
                if tok_type in (
                    tokenize.NL,
                    tokenize.NEWLINE,
                    tokenize.INDENT,
                    tokenize.DEDENT,
                    tokenize.COMMENT
                ):
                    continue

                # normalize identifiers & literals
                if tok_type == tokenize.NAME:
                    tokens.append("VAR")
                elif tok_type == tokenize.NUMBER:
                    tokens.append("NUM")
                elif tok_type == tokenize.STRING:
                    tokens.append("STR")
                else:
                    tokens.append(tok_val)
        except Exception:
            return []

        return tokens

    a_tokens = normalize(code_a)
    b_tokens = normalize(code_b)

    if not a_tokens or not b_tokens:
        return 0.0

    # multiset similarity
    matches = 0
    b_used = [False] * len(b_tokens)

    for tok in a_tokens:
        for i, bt in enumerate(b_tokens):
            if not b_used[i] and tok == bt:
                matches += 1
                b_used[i] = True
                break

    return round((matches / max(len(a_tokens), len(b_tokens))) * 100, 2)
