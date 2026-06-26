"""
app.py — Streamlit UI for SmartSQL.
Ask a question in plain English and get SQL + results from the ecommerce database.
"""

import streamlit as st
import pandas as pd
from agent import generate_sql
from db import run_query

st.set_page_config(page_title="SmartSQL", page_icon="🧠", layout="centered")

# ── Custom CSS ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global font */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hero title */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    /* Sample question chips */
    .sample-questions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 1.5rem;
    }

    /* Style the sample question buttons */
    div[data-testid="stColumns"] button {
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 20px !important;
        padding: 6px 16px !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        background: linear-gradient(135deg, rgba(102,126,234,0.08), rgba(118,75,162,0.08)) !important;
        color: #667eea !important;
        transition: all 0.3s ease !important;
        white-space: normal !important;
        text-align: left !important;
        height: auto !important;
        min-height: 42px !important;
    }
    div[data-testid="stColumns"] button:hover {
        background: linear-gradient(135deg, rgba(102,126,234,0.18), rgba(118,75,162,0.18)) !important;
        border-color: rgba(102, 126, 234, 0.6) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15) !important;
    }

    /* Primary button styling */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 28px !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px;
        transition: all 0.3s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.35) !important;
    }

    /* SQL code block */
    code {
        border-radius: 10px !important;
    }

    /* Results section */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Subtle divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102,126,234,0.3), transparent);
        margin: 1.5rem 0;
    }

    /* Input field */
    .stTextInput input {
        border-radius: 10px !important;
        border: 1.5px solid rgba(102, 126, 234, 0.3) !important;
        padding: 12px 16px !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.12) !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ──────────────────────────────────────────────────
st.title("🧠 SmartSQL")
st.caption("Ask questions about the ecommerce database in plain English — powered by AI.")
st.markdown("---")

# ── Sample Questions ────────────────────────────────────────
SAMPLE_QUESTIONS = [
    "Which city has the highest total revenue in 2024?",
    "Show me top 10 customers by lifetime value",
    "What is the month-over-month revenue trend?",
    "Which product category has the most cancellations?",
    "List all customers who haven't ordered in 90 days",
    "What is the average order value by city?",
]

# Initialize session state for the query input
if "query_input" not in st.session_state:
    st.session_state.query_input = ""


def set_question(q):
    """Callback to set the selected question into the text input."""
    st.session_state.query_input = q


st.markdown("##### 💡 Try a sample question")

# Render as 2 columns x 3 rows of clickable buttons
for row_idx in range(0, len(SAMPLE_QUESTIONS), 2):
    cols = st.columns(2)
    for col_idx, col in enumerate(cols):
        q_idx = row_idx + col_idx
        if q_idx < len(SAMPLE_QUESTIONS):
            with col:
                st.button(
                    SAMPLE_QUESTIONS[q_idx],
                    key=f"sample_{q_idx}",
                    on_click=set_question,
                    args=(SAMPLE_QUESTIONS[q_idx],),
                )

st.markdown("---")

# ── Query Input ─────────────────────────────────────────────
question = st.text_input(
    "Your question",
    placeholder="e.g. Show me the top 3 customers by total spending",
    key="query_input",
)

# ── Generate & Run ──────────────────────────────────────────
if st.button("🚀 Generate & Run", type="primary") and question:
    with st.spinner("✨ Generating SQL..."):
        try:
            sql = generate_sql(question)
        except Exception as e:
            st.error(f"Error generating SQL: {e}")
            st.stop()

    st.subheader("📝 Generated SQL")
    st.code(sql, language="sql")

    with st.spinner("⚡ Running query..."):
        try:
            columns, rows = run_query(sql)
        except Exception as e:
            st.error(f"Query execution error: {e}")
            st.stop()

    st.subheader("📊 Results")
    if rows:
        # Show row count
        st.caption(f"{len(rows)} rows returned")
        df = pd.DataFrame(rows, columns=columns)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Query returned no results.")

# ── Footer ──────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#888; font-size:0.8rem;'>"
    "SmartSQL &mdash; Natural language to SQL, powered by OpenAI"
    "</p>",
    unsafe_allow_html=True,
)
