import re

def preprocess_code(code_text):
    code_text = re.sub(r"#.*", "", code_text)
    code_text = re.sub(r'""".*?"""', "", code_text, flags=re.S)
    code_text = re.sub(r"'''.*?'''", "", code_text, flags=re.S)
    code_text = re.sub(r"\s+", " ", code_text)
    return code_text.strip()
