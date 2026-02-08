# Hybrid Code Plagiarism Detection System

A lightweight, explainable system to detect **code plagiarism and AI-assisted plagiarism patterns** using a hybrid approach that combines lexical similarity, structural similarity, and rule-based AI heuristics.

🚀 **Live Demo:**  
👉 https://hybrid-code-plagiarism-detector-ujj-th.streamlit.app/

---

## 📌 Project Overview

With the rise of AI-assisted coding tools, traditional plagiarism detection methods based only on text similarity are no longer sufficient. This project addresses that gap by identifying **structural reuse and AI-assisted paraphrasing patterns**, rather than claiming direct AI detection.

The system is designed to be:
- Explainable
- Lightweight (no ML models or LLMs)
- Suitable for educational environments

---

## 🧠 Key Features

### 1. Lexical Similarity
- Token-based similarity
- Measures surface-level similarity between source codes

### 2. Structural Similarity
- Normalized token-sequence comparison
- Ignores variable names and literals
- Preserves operators, keywords, and control flow

### 3. AI-Assisted Plagiarism Detection
A rule-based AI-assistance score is computed using:
- Structural vs lexical divergence
- Identifier diversity
- Formatting consistency
- Logic density

⚠️ **Note:**  
This system does **not** claim to definitively detect AI-generated code.  
Instead, it detects **AI-assisted plagiarism patterns** in an explainable manner.

### 4. Explainable Results
- Human-readable explanations for every comparison
- Clear reasoning behind verdicts

### 5. Interactive Visualization
- Tabular similarity report
- Dynamic bar charts comparing:
  - Lexical similarity
  - Structural similarity
  - AI-assistance score

---

## 🖥️ Tech Stack

- **Python**
- **Streamlit** (UI & deployment)
- **Pandas** (data handling)
- **Matplotlib** (visualization)

---

## 📊 Verdict Categories

- **Likely Original**
- **Moderate Similarity**
- **Direct Copy**
- **AI-Assisted Plagiarism**

Each verdict is derived from a transparent, rule-based decision process.

---

## 🧪 How It Works (High Level)

1. User uploads two or more Python files
2. Code is preprocessed and normalized
3. Similarity metrics are computed:
   - Lexical similarity
   - Structural similarity
4. AI-assisted heuristics are evaluated
5. Final verdict and explanation are generated
6. Results are visualized interactively

---

## ⚠️ Limitations

- Does not guarantee detection of all AI-generated code
- Rule-based heuristics may produce false positives in rare cases
- Best suited for academic and educational plagiarism analysis

---

## 🎓 Academic Positioning

This project focuses on **explainability and reliability** rather than black-box AI models, making it well-suited for:
- University projects
- Demonstrations of software design thinking
- Ethical AI discussions





