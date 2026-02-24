import streamlit as st
import os
import itertools
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
import docx
import time

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

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="PRISM - Plagiarism Detection",
    layout="wide",
    page_icon="🔎"
)

# ================= SIDEBAR =================
with st.sidebar:
    st.header("📂 Upload Files")

    uploaded_files = st.file_uploader(
        "Upload minimum 2 files",
        type=SUPPORTED_EXTENSIONS,
        accept_multiple_files=True
    )

    st.markdown("---")
    st.subheader("⚙ Detection Settings")

    lex_threshold = st.slider("Lexical Threshold (%)", 0, 100, 50)
    ai_threshold = st.slider("AI Sensitivity", 0.0, 1.0, 0.65)

    st.markdown("---")
    st.caption("PRISM v1.0")
    st.caption("Hybrid Plagiarism Intelligence Engine")


# ================= HERO =================
st.markdown("# 🔎 PRISM")
st.markdown("### Plagiarism Recognition & Integrated Similarity Mapping")
st.markdown(
    "Detect similarity across **Code and Documents** using lexical, structural, and AI-assisted behavioral analysis."
)
st.divider()


# ================= WHAT IS PLAGIARISM =================
with st.expander("📘 What is Plagiarism?"):
    st.markdown("""
Plagiarism is presenting someone else's work as your own without attribution.

Common forms include:

• Direct copying  
• Renamed variables but identical logic  
• Structural refactoring  
• AI-assisted rewriting  
• Document copying without citation  

PRISM evaluates:

✔ Lexical Similarity  
✔ Structural Similarity (Python)  
✔ AI Behavioral Heuristics  
""")


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


# ================= SESSION STATE =================
if "done" not in st.session_state:
    st.session_state.done = False
    st.session_state.df = None
    st.session_state.explanations = None


# ================= ANALYZE =================
if st.sidebar.button("🚀 Analyze Files"):

    if not uploaded_files or len(uploaded_files) < 2:
        st.warning("Please upload at least two files.")
        st.stop()

    file_names = [f.name for f in uploaded_files]
    if len(file_names) != len(set(file_names)):
        st.error("Duplicate file detected.")
        st.stop()

    content_map = {}
    ext_map = {}

    progress = st.progress(0)
    status = st.empty()

    # ---------- LOAD ----------
    for i, file in enumerate(uploaded_files):
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

        progress.progress((i + 1) / len(uploaded_files))
        status.text(f"Processing {file.name}...")
        time.sleep(0.2)

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

    if not rows:
        st.error("No valid comparisons found.")
        st.stop()

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

    st.success("Analysis Complete 🎉")
    st.balloons()


# ================= RESULTS =================
if st.session_state.done:

    df = st.session_state.df
    explanations = st.session_state.explanations

    st.subheader("📊 Quick Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Comparisons", len(df))
    col2.metric("Highest Lexical Similarity",
                f"{df['Lexical Similarity (%)'].max()}%")
    col3.metric("Highest AI Score",
                f"{round(df['AI Assistance Score'].max()*100,2)}%")

    st.divider()

    st.subheader("📋 Similarity Summary")
    df_sorted = df.sort_values(
        by="Lexical Similarity (%)",
        ascending=False
    )
    st.dataframe(df_sorted, width="stretch")

    st.divider()

    st.subheader("🔍 Detailed Analysis")

    if explanations:
        pair = st.selectbox(
            "Select file pair",
            options=list(explanations.keys())
        )

        if pair:
            st.markdown(f"### {pair[0]}  ↔  {pair[1]}")
            for line in explanations[pair]:
                st.markdown(f"- {line}")

            st.divider()
            st.subheader("📈 Visual Comparison")

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
            ax.set_title("Similarity Breakdown")

            st.pyplot(fig)

            # ---------- Heatmap without seaborn ----------
            st.subheader("🔥 Similarity Heatmap")

            pivot = df.pivot(
                index="File A",
                columns="File B",
                values="Lexical Similarity (%)"
            ).fillna(0)

            fig2, ax2 = plt.subplots()
            cax = ax2.imshow(pivot, cmap="coolwarm")
            plt.colorbar(cax)

            ax2.set_xticks(range(len(pivot.columns)))
            ax2.set_yticks(range(len(pivot.index)))
            ax2.set_xticklabels(pivot.columns, rotation=45)
            ax2.set_yticklabels(pivot.index)

            st.pyplot(fig2)


# ================= FAQ =================
st.divider()
st.subheader("❓ Frequently Asked Questions")

with st.expander("Does PRISM detect AI-generated content?"):
    st.write("""
PRISM evaluates behavioral patterns such as identifier diversity,
formatting consistency, and logic density to estimate AI assistance.
""")

with st.expander("Why is structural similarity zero for non-Python files?"):
    st.write("""
Structural comparison is currently supported only for Python.
Other file types use lexical similarity.
""")

with st.expander("What score indicates plagiarism?"):
    st.write("""
Above 80% → High similarity  
50–80% → Moderate similarity  
Below 50% → Low similarity  
Context always matters.
""")


# ================= FOOTER =================
st.markdown("""
---
© 2026 PRISM  
Developed by **Ujjwal**  
Hybrid Plagiarism Intelligence Engine
""")
