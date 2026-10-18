# 📚 Document Q&A Bot

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
| LLM | Groq (allam-2-7b) | >=0.2.0 |
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

**Read-only filesystem handling (`storage.py`):**

Streamlit Cloud's app directory is read-only (only `/tmp` is writable). `storage.py` detects this at startup and redirects all writes:

| Host | Base dir | Vector store | Uploads |
|------|----------|--------------|---------|
| Local | project dir | `./vector_store/` | `./data/` |
| Streamlit Cloud | `/tmp` | `/tmp/vector_store/` | `/tmp/data/` |

This prevents the SQLite `attempt to write a readonly database` error.

**⚠️ Ephemeral storage:** `/tmp` is wiped on every restart, redeploy, or sleep. After any restart, click **"Ingest Documents"** again — it takes just a few seconds since the sample documents ship with the repo.

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

- **Persistence**: Stored at `storage.VECTOR_STORE_PATH` — `./vector_store/` locally, `/tmp/vector_store/` on Streamlit Cloud
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
