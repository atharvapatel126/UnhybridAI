"""Student selection, answer mode, and document management presentation."""
import streamlit as st
from config import settings
from src.db.queries import list_students
from src.ingest.embed_store import list_documents
from src.ingest.uploads import ingest_upload


def clear_history():
    st.session_state.messages = []


def render_sidebar():
    with st.sidebar:
        st.subheader("Your university workspace")
        records = list_students()
        if records["error"]:
            st.warning("Student database unavailable. Run the documented initialization step.")
        students = {row["student_id"]: row["name"] for row in records["rows"]}
        student = st.selectbox("Synthetic student", [None, *students], key="student_id",
            format_func=lambda sid: f"{sid} · {students[sid]}" if sid else "Select a student",
            on_change=clear_history)
        offline = st.checkbox("Use local evidence only", value=not bool(settings.api_key), key="offline_mode",
                              help="Show records and policy excerpts without generated answers.")
        if not settings.api_key:
            st.info("Gemini key not configured. Local evidence mode is available.")
        st.divider()
        st.subheader("Policy documents")
        uploaded = st.file_uploader("Add a PDF or text document", type=["pdf", "txt", "md"], key="document_upload")
        if st.button("Index document", disabled=uploaded is None, width="stretch"):
            with st.spinner("Extracting and indexing document…"):
                result = ingest_upload(uploaded.name, uploaded.getvalue())
            if result["ok"]:
                st.success(f"Indexed {uploaded.name}: {result['chunks']} chunks.")
                clear_history()
            for error in result["errors"]:
                st.warning(error)
        try:
            documents = list_documents()
            for document in documents:
                st.caption(f"{document['source_file']} · {document['chunks']} chunks")
            if not documents:
                st.info("No documents indexed. Upload a synthetic policy or initialize the demo.")
        except Exception:
            documents = []
            st.warning("Document index unavailable. Check storage access.")
        st.divider()
        if st.button("Clear conversation", width="stretch"):
            clear_history()
        st.caption("Synthetic demo. Student selection is not authentication.")
    return student, offline, len(students), len(documents)
