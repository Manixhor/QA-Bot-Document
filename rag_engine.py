"""
RAG Engine - Core retrieval-augmented generation pipeline.
Uses Groq AI (free) + HuggingFace Embeddings (free, local)
"""

import os
import sys
import warnings
from pathlib import Path
from typing import List, Tuple

# Patch importlib to prevent transformers from crashing on missing torchvision
import importlib.util
_orig_find_spec = importlib.util.find_spec
def _safe_find_spec(name, *args, **kwargs):
    if isinstance(name, str) and (name == "torchvision" or name.startswith("torchvision.")):
        return None
    return _orig_find_spec(name, *args, **kwargs)
importlib.util.find_spec = _safe_find_spec

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from dotenv import load_dotenv

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

# Load environment variables
load_dotenv()

# Constants
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
VECTOR_STORE_PATH = "./vector_store"
COLLECTION_NAME = "document_qa"


def get_embeddings():
    """Get HuggingFace embedding model (free, runs locally)."""
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": False}
    )


def get_llm():
    """Get Groq LLM (free API)."""
    from langchain_groq import ChatGroq
    return ChatGroq(
        model="allam-2-7b",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3
    )


class RAGEngine:
    """Main RAG pipeline engine."""

    def __init__(self):
        """Initialize the RAG engine with Groq + HuggingFace."""
        self.embeddings = get_embeddings()
        self.llm = get_llm()
        self.vector_store = None

    def load_documents(self, data_path: str = "./data") -> List:
        """Load documents from the data directory."""
        documents = []
        data_dir = Path(data_path)

        if not data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {data_path}")

        for file_path in sorted(data_dir.glob("*")):
            try:
                if file_path.suffix.lower() == ".pdf":
                    loader = PyPDFLoader(str(file_path))
                    documents.extend(loader.load())
                    print(f"  ✓ PDF: {file_path.name}")
                elif file_path.suffix.lower() == ".txt":
                    loader = TextLoader(str(file_path))
                    documents.extend(loader.load())
                    print(f"  ✓ TXT: {file_path.name}")
                elif file_path.suffix.lower() == ".docx":
                    loader = Docx2txtLoader(str(file_path))
                    documents.extend(loader.load())
                    print(f"  ✓ DOCX: {file_path.name}")
            except Exception as e:
                print(f"  ✗ Error loading {file_path.name}: {str(e)}")

        print(f"\n  Total: {len(documents)} documents loaded")
        return documents

    def chunk_documents(self, documents: List) -> List:
        """Split documents into chunks with overlap."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        chunks = text_splitter.split_documents(documents)
        print(f"  Created {len(chunks)} chunks")
        return chunks

    def create_vector_store(self, chunks: List) -> Chroma:
        """Create and populate the vector store."""
        import shutil
        import time

        # Remove old store to avoid readonly DB errors
        if os.path.exists(VECTOR_STORE_PATH):
            shutil.rmtree(VECTOR_STORE_PATH, ignore_errors=True)
            time.sleep(0.5)

        os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection_name=COLLECTION_NAME,
            persist_directory=VECTOR_STORE_PATH
        )

        print(f"  Vector store created with {len(chunks)} chunks")
        return self.vector_store

    def load_vector_store(self) -> Chroma:
        """Load existing vector store from disk."""
        if not os.path.exists(VECTOR_STORE_PATH):
            raise FileNotFoundError("Vector store not found. Run ingest first.")

        try:
            self.vector_store = Chroma(
                collection_name=COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=VECTOR_STORE_PATH
            )
            count = self.vector_store._collection.count()
            print(f"  Loaded vector store with {count} chunks")
        except Exception as e:
            if "readonly" in str(e).lower() or "locked" in str(e).lower():
                print("  ⚠️ Database locked, re-ingesting documents...")
                self.ingest()
            else:
                raise

        return self.vector_store

    def ingest(self, data_path: str = "./data") -> None:
        """Full ingestion pipeline: load → chunk → embed → store."""
        print("\n" + "=" * 50)
        print("📥 Document Ingestion")
        print("=" * 50)

        print("\n📄 Loading documents...")
        documents = self.load_documents(data_path)

        if not documents:
            raise ValueError("No documents found in the data directory")

        print("\n✂️  Chunking documents...")
        chunks = self.chunk_documents(documents)

        print("\n💾 Creating vector store...")
        self.create_vector_store(chunks)

        print("\n" + "=" * 50)
        print("✅ Ingestion complete!")
        print("=" * 50)

    def generate_answer(self, query: str, k: int = 3) -> dict:
        """Generate an answer using RAG pipeline."""
        if self.vector_store is None:
            self.load_vector_store()

        prompt_template = """You are a helpful assistant that answers questions based on the provided context.
If the answer is not in the context, say "I don't have enough information to answer this question."
Always cite your sources by mentioning the filename.

Context:
{context}

Question: {question}

Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": k}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )

        result = qa_chain.invoke({"query": query})

        answer = {
            "answer": result["result"],
            "sources": []
        }

        for doc in result["source_documents"]:
            source_info = {
                "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                "metadata": doc.metadata
            }
            answer["sources"].append(source_info)

        return answer

    def query(self, question: str, k: int = 3) -> Tuple[str, List]:
        """Simple query interface."""
        result = self.generate_answer(question, k)

        sources_text = []
        for i, source in enumerate(result["sources"], 1):
            filename = source["metadata"].get("source", "Unknown")
            page = source["metadata"].get("page", "N/A")
            sources_text.append(f"Source {i}: {filename} (Page {page})")

        return result["answer"], sources_text, result["sources"]


if __name__ == "__main__":
    print("Testing RAG Engine...\n")
    engine = RAGEngine()
    engine.ingest()

    print("\n\nTesting query...")
    answer, sources, _ = engine.query("What is Python?")
    print(f"\nAnswer: {answer}")
    print(f"\nSources: {sources}")
