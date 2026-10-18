"""Document Q&A workspace: isolated uploads, grounded answers and source previews."""
import logging
import os
from pathlib import Path
import tempfile

import streamlit as st
from dotenv import load_dotenv

from storage import SAMPLE_DIR, save_upload

load_dotenv()
st.set_page_config(page_title="Folio · Document Q&A", page_icon="📖", layout="wide")
if not os.getenv("GROQ_API_KEY"):
    try:
        os.environ["GROQ_API_KEY"] = str(st.secrets["GROQ_API_KEY"])
    except (KeyError, FileNotFoundError):
        pass

EXAMPLES = ["What is Python?", "Explain the types of machine learning.",
            "How does retrieval-augmented generation work?", "What are the uses of cloud computing?"]


def initialize_session_state():
    defaults = {"rag_engine": None, "ingested": False, "history": [], "question": "",
                "needs_index": False, "include_samples": True}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if "workspace" not in st.session_state:
        st.session_state.workspace = tempfile.TemporaryDirectory(prefix="folio-")


def select_question(question):
    st.session_state.question = question


def invalidate_index():
    st.session_state.needs_index = True


def show_answer(entry):
    st.markdown("#### Your question")
    st.write(entry["question"])
    st.markdown("#### Matching passages" if entry.get("mode") == "Source search" else "#### Answer")
    st.write(entry["answer"])
    if entry.get("sources"):
        st.caption("RETRIEVED PASSAGES · Review these to check the answer")
    for i, source in enumerate(entry.get("sources", []), 1):
        metadata = source["metadata"]
        filename = Path(metadata.get("source", "Unknown")).name
        page = metadata.get("page")
        label = f"[{i}] {filename}" + (f" · Page {page + 1}" if isinstance(page, int) else "")
        with st.expander(label):
            st.write(source["content"])


def main():
    initialize_session_state()
    css = Path(__file__).with_name('static').joinpath('style.css').read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    workspace = Path(st.session_state.workspace.name)
    upload_dir = workspace / 'uploads'
    with st.sidebar:
        st.markdown("## ◈ folio")
        st.caption("YOUR DOCUMENT WORKSPACE")
        st.divider()
        st.subheader("1. Add your documents")
        uploads = st.file_uploader("Upload documents", type=['pdf', 'txt', 'docx'],
                                   accept_multiple_files=True, help="PDF, TXT or DOCX · Up to 20 MB each")
        selected_names = {upload.name for upload in uploads or []}
        if upload_dir.exists():
            for saved in upload_dir.iterdir():
                if saved.is_file() and saved.name not in selected_names:
                    saved.unlink()
                    st.session_state.needs_index = True
        for upload in uploads or []:
            try:
                if save_upload(upload_dir, upload.name, upload.getvalue()):
                    st.session_state.needs_index = True
            except (ValueError, OSError) as error:
                st.error(str(error) if isinstance(error, ValueError) else "Could not save this upload. Please retry.")
        include_samples = st.checkbox("Include sample library", key="include_samples", on_change=invalidate_index)
        files = {p.name: p for p in SAMPLE_DIR.iterdir() if p.suffix.lower() in {'.txt', '.pdf', '.docx'}} if include_samples else {}
        if upload_dir.exists():
            files.update({p.name: p for p in upload_dir.iterdir() if p.is_file()})
        with st.expander(f"Document library · {len(files)} {'file' if len(files) == 1 else 'files'}"):
            if not files:
                st.caption("Add a document to get started.")
            for name in sorted(files):
                st.text(name)
        if st.button("Process documents", type="primary", disabled=not files, use_container_width=True):
            with st.spinner("Reading documents and building your search index…"):
                try:
                    from rag_engine import RAGEngine
                    engine = st.session_state.rag_engine or RAGEngine(persist_directory=workspace / 'index')
                    paths = [str(upload_dir)] + ([str(SAMPLE_DIR)] if include_samples else [])
                    engine.ingest(paths)
                    st.session_state.rag_engine = engine
                    st.session_state.ingested = True
                    st.session_state.needs_index = False
                    st.success("Documents are ready. Ask a question.")
                except Exception as error:
                    logging.exception("Document processing failed")
                    if isinstance(error, (ValueError, FileNotFoundError)):
                        st.error(str(error))
                    else:
                        st.error("Could not process documents. Check dependencies and your connection, then retry.")
        if st.session_state.rag_engine and st.session_state.rag_engine.load_errors:
            with st.expander("Some documents could not be read", expanded=True):
                for warning in st.session_state.rag_engine.load_errors:
                    st.warning(warning)
        st.divider()
        st.subheader("Search settings")
        k = st.slider("Source passages per answer", 1, 10, 3)
        st.caption("More passages add context but may take longer.")
        st.caption("Uploads and search indexes are isolated to this browser session. Relevant passages are sent to Groq when you ask a question.")

    st.markdown('<div class="eyebrow">DOCUMENT INTELLIGENCE / FOLIO</div>', unsafe_allow_html=True)
    st.markdown("<h1>Your documents.<br>Clearer answers.</h1>", unsafe_allow_html=True)
    st.markdown("Find the details that matter. Ask a question, get a grounded answer, and explore the source.")
    ready = st.session_state.ingested and not st.session_state.needs_index
    with st.container(border=True):
        a, b, c = st.columns(3)
        a.metric("Library documents", len(files))
        b.metric("Search passages", getattr(st.session_state.rag_engine, 'chunk_count', 0))
        c.metric("Workspace", "Ready" if ready else "Needs processing")
    if st.session_state.needs_index:
        st.info("Your library has changed. Process documents to search the latest files.")
    elif not ready:
        st.info("Start with the sample library, or add your own files. Then select Process documents in the sidebar.")
    if not os.getenv("GROQ_API_KEY"):
        st.info("Source search works without an API key. For AI-written answers, add GROQ_API_KEY to .env or Streamlit secrets.")
    st.subheader("2. Ask your documents")
    mode = st.radio("Response type", ["AI answer", "Source search"],
                    index=0 if os.getenv("GROQ_API_KEY") else 1, horizontal=True,
                    help="AI answer writes a response with Groq. Source search shows document passages locally.")
    st.caption("Get an answer with citations." if mode == "AI answer" else
               "Find the closest document passages. Your question and passages stay on this server.")
    st.text_area("Your question", key="question", height=110, max_chars=4000,
                 placeholder="What are the key ideas in these documents?")
    action = "Find my answer ↗" if mode == "AI answer" else "Search documents ↗"
    if st.button(action, type="primary", disabled=not ready or (mode == "AI answer" and not os.getenv("GROQ_API_KEY"))):
        question = st.session_state.question.strip()
        if not question:
            st.warning("Enter a question first.")
        else:
            with st.spinner("Searching your documents…" if mode == "Source search" else "Finding passages and writing your answer…"):
                try:
                    engine = st.session_state.rag_engine
                    if mode == "Source search":
                        documents = engine.retrieve(question, k=k)
                        result = {
                            "answer": f"Found {len(documents)} matching passages. Expand the sources below to read them. These are search results, not an AI-generated answer." if documents else "No passages found. Try another question or process your documents again.",
                            "sources": [{"content": doc.page_content, "metadata": doc.metadata} for doc in documents],
                        }
                    else:
                        result = engine.generate_answer(question, k=k)
                    st.session_state.history.append({"question": question, "mode": mode, **result})
                    st.session_state.history = st.session_state.history[-20:]
                except Exception as error:
                    logging.exception("Answer generation failed")
                    if isinstance(error, (ValueError, FileNotFoundError)):
                        st.error(str(error))
                    elif mode == "Source search":
                        st.error("Could not search the index. Process documents again and retry.")
                    else:
                        st.error("Could not generate an answer. Check your API key, connection and provider limits, then retry. You can also switch to Source search.")
    if not st.session_state.history:
        st.caption("NEED A STARTING POINT?")
        for example in EXAMPLES:
            st.button(example, on_click=select_question, args=(example,), use_container_width=True)
    else:
        st.divider()
        st.subheader("3. Answer & evidence")
        show_answer(st.session_state.history[-1])
        transcript = '\n\n'.join(f"Question: {entry['question']}\nMode: {entry.get('mode', 'AI answer')}\n\n{entry['answer']}\n\nSources:\n" +
                                 '\n'.join(f"[{i}] {Path(s['metadata'].get('source', 'Unknown')).name}\n{s['content']}"
                                           for i, s in enumerate(entry.get('sources', []), 1))
                                 for entry in st.session_state.history)
        st.download_button("Download conversation", transcript, file_name="folio-answers.txt", mime="text/plain", on_click="ignore")
        if st.button("Clear conversation"):
            st.session_state.history = []
            st.rerun()
        if len(st.session_state.history) > 1:
            with st.expander(f"Previous answers · {len(st.session_state.history) - 1}"):
                for entry in reversed(st.session_state.history[:-1]):
                    show_answer(entry)
                    st.divider()
    st.divider()
    st.caption("FOLIO · Search locally. Generate answers with Groq. Check source passages for important details.")


if __name__ == '__main__':
    main()
