import streamlit as st
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


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="PRISM",
    layout="wide",
    page_icon="🔎"
)

# ================= PREMIUM CSS =================
st.markdown("""
<style>
.main {
    background: linear-gradient(180deg,#f9fbff,#ffffff);
}

.hero {
    padding: 2rem;
    border-radius: 16px;
    background: linear-gradient(135deg,#0066ff,#00c6ff);
    color: white;
    text-align: center;
    animation: fadeIn 1.2s ease-in;
}

.metric-box {
    background: white;
    padding: 1.2rem;
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
    text-align: center;
    animation: fadeUp 0.8s ease-in-out;
}

.footer {
    text-align:center;
    color:gray;
    padding-top:3rem;
    font-size:0.9rem;
}

@keyframes fadeIn {
    from {opacity:0; transform: translateY(-10px);}
    to {opacity:1; transform: translateY(0);}
}

@keyframes fadeUp {
    from {opacity:0; transform: translateY(15px);}
    to {opacity:1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

SUPPORTED_EXTENSIONS = [
    "py", "java", "c", "cpp", "js", "ts", "cs",
    "txt", "pdf", "docx"
]

# ================= HERO =================
st.markdown("""
<div class="hero">
<h1>🔎 PRISM</h1>
<h3>Plagiarism Recognition & Integrated Similarity Mapping</h3>
<p>AI-Assisted Similarity Detection for Code & Documents</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ================= TABS =================
tab1, tab2, tab3, tab4 = st.tabs([
    "📂 Upload & Analyze",
    "📊 Results",
    "📘 Knowledge",
    "❓ FAQ"
])

# ================= SESSION =================
if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.explanations = None


# ================= TAB 1 =================
with tab1:

    uploaded_files = st.file_uploader(
        "Upload minimum 2 files",
        type=SUPPORTED_EXTENSIONS,
        accept_multiple_files=True
    )

    if st.button("🚀 Run Analysis"):

        if not uploaded_files or len(uploaded_files) < 2:
            st.warning("Please upload at least two files.")
            st.stop()

        file_names = [f.name for f in uploaded_files]
        if len(file_names) != len(set(file_names)):
            st.error("Duplicate files detected.")
            st.stop()

        content_map = {}
        ext_map = {}

        for file in uploaded_files:

            ext = file.name.rsplit(".", 1)[-1].lower()
            file.seek(0)

            if ext == "py":
                raw = file.read().decode("utf-8", errors="ignore")
                content = preprocess_code(raw)
            elif ext in ["java", "c", "cpp", "js", "ts", "cs", "txt"]:
                content = file.read().decode("utf-8", errors="ignore")
            elif ext == "pdf":
                text = ""
                with pdfplumber.open(file) as pdf:
                    for page in pdf.pages:
                        if page.extract_text():
                            text += page.extract_text()
                content = text
            elif ext == "docx":
                document = docx.Document(file)
                content = "\n".join(p.text for p in document.paragraphs)
            else:
                content = ""

            content_map[file.name] = content
            ext_map[file.name] = ext

        rows = []
        explanations = {}

        for a, b in itertools.combinations(content_map.keys(), 2):

            lex = lexical_similarity(content_map[a], content_map[b])

            if ext_map[a] == "py" and ext_map[b] == "py":
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
                "File A", "File B",
                "Lexical %", "Structural %",
                "AI %", "Verdict"
            ]
        )

        st.session_state.df = df
        st.session_state.explanations = explanations

        st.success("Analysis Complete 🎉")


# ================= TAB 2 =================
with tab2:

    if st.session_state.df is not None:

        df = st.session_state.df
        explanations = st.session_state.explanations

        col1, col2, col3 = st.columns(3)

        col1.markdown(f"""
        <div class="metric-box">
        <h4>Total Comparisons</h4>
        <h2>{len(df)}</h2>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div class="metric-box">
        <h4>Highest Similarity</h4>
        <h2>{df['Lexical %'].max()}%</h2>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div class="metric-box">
        <h4>Highest AI Score</h4>
        <h2>{df['AI %'].max()}%</h2>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        st.dataframe(df, width="stretch")

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

    else:
        st.info("Run analysis from the Upload tab.")


# ================= TAB 3 =================
with tab3:
    st.markdown("""
### What is Plagiarism?

Plagiarism is presenting someone else's work as your own.

PRISM detects:

• Direct copying  
• Structural similarity  
• AI-assisted rewriting patterns  
• Document duplication  

It combines lexical similarity with structural and behavioral analysis.
""")


# ================= TAB 4 =================
with tab4:

    with st.expander("Does PRISM detect AI content?"):
        st.write("PRISM estimates AI assistance through behavioral signals.")

    with st.expander("What score indicates plagiarism?"):
        st.write("Above 80% usually indicates high similarity.")

    with st.expander("Why structural similarity only for Python?"):
        st.write("AST-based structural parsing currently supports Python.")


# ================= FOOTER =================
st.markdown("""
<div class="footer">
© 2026 PRISM | Developed by Ujjwal
</div>
""", unsafe_allow_html=True)
