"""
Document Q&A Bot - Streamlit Web Interface
Powered by Groq AI (Free) + HuggingFace Embeddings (Free)
"""

import os
import sys
import warnings

# Patch importlib to prevent transformers from crashing on missing torchvision
import importlib.util
_orig_find_spec = importlib.util.find_spec
def _safe_find_spec(name, *args, **kwargs):
    if isinstance(name, str) and (name == "torchvision" or name.startswith("torchvision.")):
        return None
    return _orig_find_spec(name, *args, **kwargs)
importlib.util.find_spec = _safe_find_spec

warnings.filterwarnings("ignore", category=DeprecationWarning)
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Document Q&A Bot",
    page_icon="🤖",
    layout="wide"
)


def initialize_session_state():
    """Initialize session state variables."""
    if "rag_engine" not in st.session_state:
        st.session_state.rag_engine = None
    if "ingested" not in st.session_state:
        st.session_state.ingested = False
    if "query_history" not in st.session_state:
        st.session_state.query_history = []


def main():
    """Main Streamlit application."""
    initialize_session_state()

    st.title("📚 Document Q&A Bot")

    # Sidebar
    with st.sidebar:
        # Groq API Key (auto-loaded from .env)
        default_key = os.getenv("GROQ_API_KEY", "")
        api_key = st.text_input(
            "🔑 Groq API Key",
            value=default_key,
            type="password",
        )
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key

        st.divider()

        # Document Ingestion
        uploaded_files = st.file_uploader(
            "📤 Upload documents",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True
        )

        if uploaded_files:
            os.makedirs("data", exist_ok=True)
            for file in uploaded_files:
                file_path = os.path.join("data", file.name)
                existing = b""
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        existing = f.read()
                new_content = file.getbuffer().tobytes()
                if existing != new_content:
                    with open(file_path, "wb") as f:
                        f.write(new_content)
            st.success(f"✅ Uploaded {len(uploaded_files)} file(s)")

        if st.button("📥 Ingest Documents", type="primary"):
            if not api_key:
                st.error("Please enter your Groq API key first!")
            else:
                with st.spinner("Processing..."):
                    try:
                        from rag_engine import RAGEngine
                        engine = RAGEngine()
                        engine.ingest()
                        st.session_state.rag_engine = engine
                        st.session_state.ingested = True
                        st.success("✅ Ready!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        if st.session_state.ingested:
            st.success("✅ Documents ready")
        else:
            st.warning("⚠️ Ingest documents first")

        st.divider()

        k_value = st.slider("Chunks (k)", 1, 10, 3)

        if st.session_state.query_history:
            st.caption("📜 Recent:")
            for i, (q, _) in enumerate(reversed(st.session_state.query_history[-5:]), 1):
                st.caption(f"{i}. {q[:40]}...")

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("💬 Ask a Question")

        question = st.text_area(
            "Enter your question:",
            placeholder="e.g., What are the main types of machine learning?",
            height=100
        )

        if st.button("🔍 Get Answer", type="primary", disabled=not st.session_state.ingested):
            if not question.strip():
                st.warning("Please enter a question!")
            else:
                if st.session_state.rag_engine is None:
                    from rag_engine import RAGEngine
                    st.session_state.rag_engine = RAGEngine()

                with st.spinner("Searching and generating answer..."):
                    try:
                        result = st.session_state.rag_engine.generate_answer(
                            question,
                            k=k_value
                        )

                        st.session_state.query_history.append(
                            (question, result["answer"])
                        )

                        st.markdown("### 📝 Answer")
                        st.write(result["answer"])

                        # Only show sources if the bot found relevant information
                        answer_lower = result["answer"].lower()
                        not_found_phrases = [
                            "don't have enough information",
                            "i don't have enough",
                            "not enough information",
                            "cannot answer",
                            "unable to answer",
                            "not available in the context",
                            "not mentioned in the context",
                            "no information about"
                        ]
                        is_not_found = any(phrase in answer_lower for phrase in not_found_phrases)

                        if not is_not_found and result.get("sources"):
                            st.markdown("### 📚 Sources")
                            for i, source in enumerate(result["sources"], 1):
                                filename = source["metadata"].get("source", "Unknown")
                                page = source["metadata"].get("page", "N/A")

                                with st.expander(f"Source {i}: {os.path.basename(filename)} (Page {page})"):
                                    st.write(source["content"])

                    except Exception as e:
                        st.error(f"Error generating answer: {str(e)}")

    with col2:
        st.caption("💡 **Try asking:**")
        examples = [
            "What is Python?",
            "Explain machine learning",
            "What is quantum computing?",
            "How does RAG work?",
            "Cloud computing uses?"
        ]
        for example in examples:
            if st.button(example, key=f"example_{example}"):
                st.session_state.query_history.append((example, ""))
                st.rerun()

        st.divider()
        st.caption("Groq AI + HuggingFace + ChromaDB")


if __name__ == "__main__":
    main()
