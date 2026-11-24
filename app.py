"""Streamlit presentation; retrieval, generation, and upload work live in src/."""
import streamlit as st
from src.ingest.embed_store import get_model
from src.orchestrator import answer_query
from src.ui.sidebar import render_sidebar
from src.ui.messages import render_result

st.set_page_config(page_title="UniHybrid AI", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")


@st.cache_resource(show_spinner=False)
def embedding_resource():
    return get_model()


st.session_state.setdefault("messages", [])
student, offline, student_count, document_count = render_sidebar()
st.title("UniHybrid AI")
st.caption("University answers, backed by your records and policy documents.")
st.info("SYNTHETIC — DEMO ONLY. All student records and included policies are fictional.")
left, middle, right = st.columns(3)
left.metric("Synthetic students", student_count)
middle.metric("Indexed documents", document_count)
right.metric("Answer mode", "Evidence only" if offline else "Grounded AI")
st.divider()

example = None
if not st.session_state.messages:
    st.subheader("What would you like to know?")
    st.write("Choose a student for personal questions, or ask about university policies.")
    for column, label, question in zip(st.columns(3),
        ("My GPA & fees", "Attendance policy", "Scholarship eligibility"),
        ("What is my GPA and fee status?", "What is the minimum attendance?",
         "Am I eligible for a merit scholarship and what is the deadline?")):
        if column.button(label, width="stretch"):
            example = question

for message in st.session_state.messages:
    with st.chat_message("user"):
        st.write(message["query"])
    with st.chat_message("assistant"):
        render_result(message["result"])

query = st.chat_input("Ask about records, fees, policies, or scholarships…", max_chars=2000)
if query or example:
    question = query or example
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Finding supporting evidence…"):
            if document_count:
                try:
                    embedding_resource()
                except Exception:
                    st.warning("Document search model unavailable. Structured records can still be queried.")
            result = answer_query(question, student, use_llm=not offline)
        render_result(result)
    st.session_state.messages.append({"query": question, "result": result})
