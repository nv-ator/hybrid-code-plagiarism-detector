import streamlit as st
import os
import itertools
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
import docx

from core.preprocessing import preprocess_code
from core.ast_similarity import ast_similarity
from core.lexical_similarity import lexical_similarity
from core.rules import classify_plagiarism
from core.explanation import generate_explanation

from core.ai_signals import (
    identifier_diversity,
    formatting_consistency,
    logic_density
)
from core.ai_detector import ai_assistance_score


# ================= CONFIG =================
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

SUPPORTED_EXTENSIONS = [
    "py", "java", "c", "cpp", "js", "ts", "cs",
    "txt", "pdf", "docx"
]


# ================= HELPERS =================
def get_extension(filename):
    return filename.rsplit(".", 1)[-1].lower()


def read_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def read_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text


def read_docx(path):
    document = docx.Document(path)
    return "\n".join(p.text for p in document.paragraphs)


# ================= UI =================
st.set_page_config(layout="wide")
st.title("Hybrid Code & Document Plagiarism Detection System")
st.caption("Supports Code (Python, Java, C/C++) + Documents (PDF, DOCX, TXT)")


# ================= SESSION =================
if "done" not in st.session_state:
    st.session_state.done = False
    st.session_state.df = None
    st.session_state.explanations = None


# ================= FILE UPLOAD =================
uploaded_files = st.file_uploader(
    "Upload files (minimum 2)",
    type=SUPPORTED_EXTENSIONS,
    accept_multiple_files=True
)


# ================= ANALYSIS =================
if st.button("Analyze"):
    if not uploaded_files or len(uploaded_files) < 2:
        st.warning("Please upload at least two files.")
    else:
        content_map = {}
        ext_map = {}

        # ---------- LOAD FILES ----------
        for file in uploaded_files:
            ext = get_extension(file.name)
            save_path = os.path.join(UPLOAD_DIR, file.name)

            with open(save_path, "wb") as f:
                f.write(file.read())

            if ext == "py":
                raw = read_txt(save_path)
                content = preprocess_code(raw)

            elif ext in ["java", "c", "cpp", "js", "ts", "cs", "txt"]:
                content = read_txt(save_path)

            elif ext == "pdf":
                content = read_pdf(save_path)

            elif ext == "docx":
                content = read_docx(save_path)

            else:
                content = ""

            content_map[file.name] = content
            ext_map[file.name] = ext

        rows = []
        explanations = {}

        # ---------- COMPARE ----------
        for a, b in itertools.combinations(content_map.keys(), 2):
            ext_a = ext_map[a]
            ext_b = ext_map[b]

            lex = lexical_similarity(content_map[a], content_map[b])

            if ext_a == "py" and ext_b == "py":
                ast = ast_similarity(content_map[a], content_map[b])
                id_div = identifier_diversity(content_map[a])
                fmt = formatting_consistency(content_map[a])
                logic = logic_density(content_map[a])
            else:
                ast = 0.0
                id_div = fmt = logic = 0.5

            ai_score = ai_assistance_score(
                lexical=lex,
                structural=ast,
                id_div=id_div,
                fmt=fmt,
                logic=logic
            )

            verdict = classify_plagiarism(lex, ast, ai_score)

            explanation = generate_explanation(
                a, b, lex, ast, ai_score, id_div, fmt, logic
            )
            explanation.append(
                f"File types compared: {ext_a.upper()} vs {ext_b.upper()}"
            )

            rows.append([
                a, b,
                round(lex, 2),
                round(ast, 2),
                round(ai_score, 2),
                verdict
            ])

            explanations[(a, b)] = explanation

        st.session_state.df = pd.DataFrame(
            rows,
            columns=[
                "File A",
                "File B",
                "Lexical Similarity (%)",
                "Structural Similarity (%)",
                "AI Assistance Score",
                "Verdict"
            ]
        )

        st.session_state.explanations = explanations
        st.session_state.done = True


# ================= RESULTS =================
if st.session_state.done:
    df = st.session_state.df
    explanations = st.session_state.explanations

    st.subheader("Similarity Summary")
    st.dataframe(df, use_container_width=True)

    st.subheader("Explanation")
    pair = st.selectbox("Select file pair", list(explanations.keys()))
    for line in explanations[pair]:
        st.write("•", line)

    st.subheader("Visual Comparison")
    row = df[
        (df["File A"] == pair[0]) &
        (df["File B"] == pair[1])
    ].iloc[0]

    fig, ax = plt.subplots()
    ax.bar(
        ["Lexical", "Structural", "AI Score"],
        [
            row["Lexical Similarity (%)"],
            row["Structural Similarity (%)"],
            row["AI Assistance Score"] * 100
        ]
    )
    ax.set_ylim(0, 100)
    ax.set_ylabel("Percentage")
    ax.set_title(f"{pair[0]} vs {pair[1]}")

    st.pyplot(fig)
