import streamlit as st
import os
import itertools
import pandas as pd
import matplotlib.pyplot as plt
import sys


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

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- UI ----------------
st.set_page_config(layout="wide")
st.title("Hybrid Code Plagiarism Detection System")
st.caption("Similarity + AI-assisted plagiarism pattern detection")

# ---------------- SESSION STATE ----------------
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
    st.session_state.df = None
    st.session_state.explanation_map = None

uploaded_files = st.file_uploader(
    "Upload Python files (minimum 2)",
    type=["py"],
    accept_multiple_files=True
)

# ---------------- ANALYSIS ----------------
if st.button("Analyze"):
    if not uploaded_files or len(uploaded_files) < 2:
        st.warning("Please upload at least two Python files.")
    else:
        code_map = {}

        for file in uploaded_files:
            content = file.read().decode("utf-8", errors="ignore")
            clean_code = preprocess_code(content)

            path = os.path.join(UPLOAD_DIR, file.name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(clean_code)

            code_map[file.name] = clean_code

        summary_rows = []
        explanation_map = {}

        for a, b in itertools.combinations(code_map.keys(), 2):
            # -------- Similarity --------
            lex = lexical_similarity(code_map[a], code_map[b])
            ast = ast_similarity(code_map[a], code_map[b])

            # -------- AI Signals (per file A) --------
            id_div = identifier_diversity(code_map[a])
            fmt = formatting_consistency(code_map[a])
            logic = logic_density(code_map[a])

            ai_score = ai_assistance_score(
                lexical=lex,
                structural=ast,
                id_div=id_div,
                fmt=fmt,
                logic=logic
            )

            verdict = classify_plagiarism(lex, ast, ai_score)

            explanation = generate_explanation(
                a,
                b,
                lex,
                ast,
                ai_score,
                id_div,
                fmt,
                logic
            )

            summary_rows.append([
                a,
                b,
                round(lex, 2),
                round(ast, 2),
                round(ai_score, 2),
                verdict
            ])

            explanation_map[(a, b)] = explanation

        st.session_state.df = pd.DataFrame(
            summary_rows,
            columns=[
                "File A",
                "File B",
                "Lexical Similarity (%)",
                "Structural Similarity (%)",
                "AI-Assistance Score",
                "Verdict"
            ]
        )

        st.session_state.explanation_map = explanation_map
        st.session_state.analysis_done = True

# ---------------- RESULTS ----------------
if st.session_state.analysis_done:
    df = st.session_state.df
    explanation_map = st.session_state.explanation_map

    st.subheader("Similarity & AI Analysis Summary")
    st.dataframe(df, use_container_width=True)

    # -------- EXPLANATION --------
    st.subheader("Why was this result given?")

    explain_pair = st.selectbox(
        "Select file pair for explanation",
        list(explanation_map.keys()),
        key="explain_pair"
    )

    for line in explanation_map[explain_pair]:
        st.write("•", line)

    # -------- GRAPH --------
    st.subheader("Visual Comparison")

    graph_pair = st.selectbox(
        "Select file pair for graph",
        list(explanation_map.keys()),
        key="graph_pair"
    )

    row = df[
        (df["File A"] == graph_pair[0]) &
        (df["File B"] == graph_pair[1])
    ].iloc[0]

    fig, ax = plt.subplots()
    ax.bar(
        ["Lexical", "Structural", "AI Score"],
        [
            row["Lexical Similarity (%)"],
            row["Structural Similarity (%)"],
            row["AI-Assistance Score"] * 100
        ]
    )
    ax.set_ylim(0, 100)
    ax.set_ylabel("Percentage")
    ax.set_title(f"{graph_pair[0]} vs {graph_pair[1]}")

    st.pyplot(fig)
