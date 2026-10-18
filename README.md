# QA Bot Analysis

A Retrieval-Augmented Generation (RAG) powered question answering system that allows users to ask natural language questions about their documents and receive accurate answers with source citations.

🌐 **Live app:** [app-bot-document on Streamlit Community Cloud](https://app-bot-document-f4vzh3ghty7n23j6gmzbse.streamlit.app)

## 🎯 What It Does

This bot reads your documents (PDF, TXT, DOCX), breaks them into searchable chunks, and uses AI to answer your questions while citing the exact source of information.

## 🆓 Free API: Groq

| Feature | Details |
|---------|---------|
| **Provider** | Groq |
| **Cost** | ✅ FREE |
| **Speed** | Ultra-fast (100+ tokens/sec) |
| **Limits** | 30 requests per minute |

### Get Your Free API Key

1. Go to [console.groq.com/keys](https://console.groq.com/keys)
2. Create account (free)
3. Click "Create API Key"
4. Copy the key

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.11+ |
| Framework | LangChain | >=0.3.0 |
| Vector DB | ChromaDB | >=0.2.0 |
| Embeddings | HuggingFace (all-MiniLM-L6-v2) | >=0.1.0 |
| LLM | Groq (openai/gpt-oss-20b) | >=0.2.0 |
| UI | Streamlit | >=1.30.0 |
| Text Splitter | LangChain RecursiveCharacterTextSplitter | >=0.3.0 |
| Document Loaders | PyPDF, Docx2txt | >=4.0.0, >=0.8.0 |

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCUMENT Q&A BOT                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ Documents │───▶│ Loader   │───▶│ Chunker  │              │
│  │ (PDF/TXT) │    │          │    │          │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│                                       │                     │
│                                       ▼                     │
│                              ┌──────────────┐               │
│                              │  Embeddings  │               │
│                              │ (Free, Local)│               │
│                              └──────────────┘               │
│                                       │                     │
│                                       ▼                     │
│                              ┌──────────────┐               │
│                              │  ChromaDB    │               │
│                              │ (Vector DB)  │               │
│                              └──────────────┘               │
│                                       │                     │
│                                       ▼                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  User    │───▶│ Retriever│───▶│  Groq LLM│───▶ Answer   │
│  │  Query   │    │          │    │ (Free)   │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start (5 Minutes)

### Step 1: Clone & Setup
```bash
git clone <your-repo-url>
cd rag-document-qa
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Get Free Groq API Key
```bash
# Go to: https://console.groq.com/keys
# Create free API key (no credit card needed!)
```

### Step 3: Add Your API Key
```bash
cp .env.example .env
```

Edit `.env` and add:
```
GROQ_API_KEY=your-free-key-here
```

> 🔐 **Never hardcode API keys in source code.** Locally they live in `.env` (gitignored); on Streamlit Cloud they live in the app's secret store (see [Deployment](#️-deployment-streamlit-community-cloud)).

### Step 4: Run the App
```bash
streamlit run app.py
```

### Step 5: Use It!
1. Click "Ingest Documents"
2. Ask questions!

## ☁️ Deployment (Streamlit Community Cloud)

The app runs for free on [Streamlit Community Cloud](https://share.streamlit.io), connected to this GitHub repo — every push to `main` auto-redeploys it.

**One-time setup:**

1. Go to [share.streamlit.io](https://share.streamlit.io) → **Create app** → select this repo, branch `main`, main file `app.py`
2. Add the API key: **⚙️ Settings → Secrets** and paste:
   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   ```
3. Deploy (first build ≈ 5–10 min, CPU-only PyTorch download)

**Storage and session isolation:**

Each web session uses its own temporary directory for uploads and its Chroma index. The bundled `data/` library is read without modification. Web uploads are never written into another session's workspace. Temporary workspaces do not survive a server restart; process documents again after restarting or starting a new session.

The command-line interface uses project-relative `data/` and `vector_store/` directories. If the project is read-only, `storage.py` selects a temporary writable base directory for the CLI instead.

## 🧩 Chunking Strategy

**Strategy**: Recursive Character Text Splitting

- **Chunk size**: 1000 characters
- **Chunk overlap**: 200 characters
- **Separators**: `["\n\n", "\n", ". ", " ", ""]`

**Why this choice?**
RecursiveCharacterTextSplitter is the most widely recommended strategy for RAG pipelines. It tries to split on paragraph boundaries first (`\n\n`), then sentence boundaries (`\n`, `. `), then word boundaries — preserving semantic meaning at each level. The 200-character overlap ensures context is not lost at chunk boundaries. This is superior to fixed-size splitting because it respects natural text structure.

**Metadata stored**: source filename and page number for each chunk.

## 🧠 Embedding Model & Vector Database

### Embeddings: HuggingFace `all-MiniLM-L6-v2`

- **Dimensions**: 384
- **Type**: Sentence-BERT, runs locally on CPU
- **Why?** It is one of the fastest and most efficient open-source embedding models. It runs entirely locally (no API calls needed for embeddings), making it completely free and privacy-friendly. It produces high-quality semantic embeddings suitable for document retrieval.

### Vector Database: ChromaDB

- **Persistence**: Stored at `storage.VECTOR_STORE_PATH` — the project directory for the CLI, an isolated temporary workspace for each web session
- **Why?** ChromaDB is lightweight, easy to set up, and integrates natively with LangChain. It persists embeddings to disk so the vector store survives restarts without re-indexing. Unlike FAISS, it provides a simpler API for metadata filtering. Unlike Qdrant/Weaviate, it requires no separate server — it runs in-process.

## 💡 Example Queries

| Query | Expected Source |
|-------|-----------------|
| "What is Python?" | python_programming.txt |
| "Explain machine learning types" | machine_learning.txt |
| "What are the uses of data science?" | data_science.txt |
| "How does RAG work?" | ai_large_language_models.txt |
| "What is web development?" | web_development.txt |

## 💰 Cost

| Use Case | Cost |
|----------|------|
| Demo / Learning | $0.00 (free tier) |
| Production | $0.00 (free tier, 30 req/min) |

## ⚠️ Free Tier Limits

- 30 requests per minute
- Very fast inference (100+ tokens/sec)
- Great for real-time apps

## 📁 Project Structure

```
rag-document-qa/
├── data/                    # Your documents
├── vector_store/            # ChromaDB (auto-created)
├── static/style.css         # Responsive workspace styling
├── tests/                   # Engine, Chroma and Streamlit UI checks
├── app.py                   # Streamlit UI
├── cli.py                   # CLI interface
├── rag_engine.py            # Core RAG pipeline
├── storage.py               # Writable-path resolution (local vs /tmp on cloud)
├── requirements.txt         # Dependencies
├── .env.example             # API key template
└── README.md                # This file
```

## 🔐 Environment Variables

Create a `.env` file from the template:
```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ Yes | Your Groq API key from [console.groq.com/keys](https://console.groq.com/keys) |

> ⚠️ **Never commit your `.env` file.** It is already included in `.gitignore`. On Streamlit Cloud, set the same variable under **⚙️ Settings → Secrets** instead of a `.env` file — never hardcode keys in source (GitHub push protection and GitGuardian will block/alert on committed secrets).

## ⚠️ Known Limitations

| Limitation | Explanation |
|-----------|-------------|
| **Large documents** | Very large PDFs (>50 pages) may take longer to chunk and embed. The current pipeline loads all documents into memory. |
| **Table/image extraction** | PDF tables and images are not extracted — only raw text is processed. Complex layouts may lose structure. |
| **Multi-language** | The `all-MiniLM-L6-v2` embedding model is optimized for English. Non-English documents may have lower retrieval quality. |
| **Chunk size trade-off** | Fixed 1000-character chunks may split mid-sentence or mid-entity. Smaller chunks improve precision but lose context; larger chunks improve context but reduce retrieval precision. |
| **No reranking** | Retrieved chunks are passed directly to the LLM without a reranking step. A cross-encoder reranker could improve answer quality. |
| **Single-session chat** | Each query is independent — there is no conversation memory or follow-up question support. |

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Invalid API key" | Check key is correct, no extra spaces |
| "Rate limit exceeded" | Wait 1 minute, then retry |
| "Module not found" | Run `pip install -r requirements.txt` |
| "Vector store not found" | Click "Ingest Documents" first |
| "attempt to write a readonly database" | Fixed automatically by `storage.py` (`/tmp` on Streamlit Cloud) — make sure the latest code is deployed |
| Worked, then broke after a while | Streamlit Cloud wiped `/tmp` after a sleep/restart — click "Ingest Documents" again |

## 📝 License

MIT License - Free to use and modify.

---

**Built with ❤️ using Free APIs (Groq + HuggingFace)**


## QA Bot Analysis workspace

The working application is `app.py` (Streamlit). `index.html` is an older standalone demo and is not the deployed UI.

- Responsive green and cream workspace with document counts, processing status, and source previews.
- Each web session has its own temporary upload directory and vector index. Bundled samples are optional; uploaded files with the same filename take precedence. Session workspaces are temporary and are removed when their session state is released; they do not survive server restarts.
- PDF, UTF-8 TXT and DOCX uploads are limited to 20 MB each. Scanned PDFs require OCR before uploading.
- Process documents after changing the library. Re-indexing builds a new collection before switching to it, preserving the previous index on failure.
- Choose **Source search** to read matching document passages without an API key, or **AI answer** for a generated answer with citations. Ingestion and retrieval do not require a Groq key. Answer generation requires `GROQ_API_KEY`; `GROQ_MODEL` optionally overrides the default `openai/gpt-oss-20b`.
- Example questions fill the editor. The latest 20 answers and their full retrieved passages remain visible across interactions and can be downloaded. Questions are independent; earlier conversation turns are not sent to the model.
- Relevant document passages are sent to Groq for answer generation. Embeddings run locally.

Run from any location with `./start_server.sh` (the script resolves the project directory). Python 3.11+ is recommended; create `.venv`, install `requirements.txt`, then optionally add a Groq key to `.env` for AI answers. Source search works without a key.

### Verification

```sh
.venv/bin/python -m unittest discover -s tests -v
```

UI tests use Streamlit AppTest, and provider responses are mocked. Vector-store integration tests use real Chroma with deterministic local test embeddings, so they require no model download or API credentials. A full live-provider check additionally needs a valid Groq key and the HuggingFace embedding model download.


To run the complete browser workflow, start `./start_server.sh --server.port 8503`, make Playwright available to Node.js, and run `node tests/browser.cjs`. The test uploads a TXT document, creates a real index, searches its passages, downloads the result, clears history, and checks mobile, tablet and desktop widths. The first indexing run downloads the embedding model. `QA_TEST_URL` and `PLAYWRIGHT_EXECUTABLE_PATH` optionally override the server and browser paths.

Source-file watching is disabled because scanning Transformers modules can import optional vision dependencies. Restart the preview after editing Python source files during development.


### Explore without a prepared question

You can type any question about your documents; the example buttons are optional. **Source search** finds matching original passages for a question or keywords without writing an AI answer. **Browse documents** previews the first indexed passages in a selected file without a question or API key. Process documents first, then choose the file and select **Preview document**. The passage slider controls the preview length (up to ten passages). Your draft question is preserved when switching modes.
