import streamlit as st
import itertools
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
import docx
import io

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


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="PRISM",
    layout="wide",
    page_icon="🔎"
)

# ================= PREMIUM LIGHT THEME CSS =================
st.markdown("""
<style>
.main {
    background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
}
.hero {
    padding: 2rem;
    border-radius: 12px;
    background: linear-gradient(135deg, #007BFF, #00C6FF);
    color: white;
    text-align: center;
}
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}
.footer {
    text-align: center;
    color: gray;
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)


SUPPORTED_EXTENSIONS = [
    "py", "java", "c", "cpp", "js", "ts", "cs",
    "txt", "pdf", "docx"
]


# ================= SIDEBAR =================
with st.sidebar:
    st.header("📂 Upload Files")

    uploaded_files = st.file_uploader(
        "Upload minimum 2 files",
        type=SUPPORTED_EXTENSIONS,
        accept_multiple_files=True
    )

    st.markdown("---")
    st.caption("PRISM v2.0")
    st.caption("Hybrid Plagiarism Intelligence Engine")


# ================= HERO =================
st.markdown("""
<div class="hero">
<h1>🔎 PRISM</h1>
<h3>Plagiarism Recognition & Integrated Similarity Mapping</h3>
<p>AI-assisted similarity detection for Code & Documents</p>
</div>
""", unsafe_allow_html=True)

st.divider()


# ================= HELPERS =================
def get_extension(filename):
    return filename.rsplit(".", 1)[-1].lower()


def read_txt(file):
    return file.read().decode("utf-8", errors="ignore")


def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text


def read_docx(file):
    document = docx.Document(file)
    return "\n".join(p.text for p in document.paragraphs)


# ================= ANALYSIS =================
if uploaded_files and len(uploaded_files) >= 2:

    file_names = [f.name for f in uploaded_files]
    if len(file_names) != len(set(file_names)):
        st.error("Duplicate files detected.")
        st.stop()

    content_map = {}
    ext_map = {}

    for file in uploaded_files:

        ext = get_extension(file.name)

        file.seek(0)

        if ext == "py":
            raw = read_txt(file)
            content = preprocess_code(raw)
        elif ext in ["java", "c", "cpp", "js", "ts", "cs", "txt"]:
            content = read_txt(file)
        elif ext == "pdf":
            content = read_pdf(file)
        elif ext == "docx":
            content = read_docx(file)
        else:
            content = ""

        content_map[file.name] = content
        ext_map[file.name] = ext

    rows = []
    explanations = {}

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

        rows.append([
            a, b,
            round(lex, 2),
            round(ast, 2),
            round(ai_score * 100, 2),
            verdict
        ])

        explanations[(a, b)] = explanation

    df = pd.DataFrame(
        rows,
        columns=[
            "File A",
            "File B",
            "Lexical %",
            "Structural %",
            "AI %",
            "Verdict"
        ]
    )

    st.success("Analysis Complete")

    # ================= METRICS =================
    col1, col2, col3 = st.columns(3)

    col1.markdown(f"""
    <div class="metric-card">
    <h4>Total Comparisons</h4>
    <h2>{len(df)}</h2>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="metric-card">
    <h4>Highest Similarity</h4>
    <h2>{df['Lexical %'].max()}%</h2>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="metric-card">
    <h4>Highest AI Score</h4>
    <h2>{df['AI %'].max()}%</h2>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.dataframe(df, width="stretch")

    # ================= VISUAL =================
    pair = st.selectbox("Select file pair", list(explanations.keys()))

    if pair:
        row = df[
            (df["File A"] == pair[0]) &
            (df["File B"] == pair[1])
        ].iloc[0]

        fig, ax = plt.subplots()
        ax.bar(
            ["Lexical", "Structural", "AI"],
            [
                row["Lexical %"],
                row["Structural %"],
                row["AI %"]
            ]
        )
        ax.set_ylim(0, 100)
        ax.set_ylabel("Percentage")
        st.pyplot(fig)


# ================= FAQ =================
st.divider()
with st.expander("What similarity indicates plagiarism?"):
    st.write("Above 80% generally indicates high similarity.")

with st.expander("Does PRISM detect AI content?"):
    st.write("PRISM estimates AI assistance through behavioral metrics.")


# ================= FOOTER =================
st.markdown("""
<div class="footer">
© 2026 PRISM | Developed by Ujjwal
</div>
""", unsafe_allow_html=True)
