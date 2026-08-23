# 📚 Document Q&A Bot

A Retrieval-Augmented Generation (RAG) powered question answering system that allows users to ask natural language questions about their documents and receive accurate answers with source citations.

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

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Framework | LangChain |
| Vector DB | ChromaDB |
| Embeddings | HuggingFace (free, local) |
| LLM | Groq (allam-2-7b) |
| UI | Streamlit |

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

### Step 3: Create .env File
```bash
cp .env.example .env
```

Edit `.env` and add:
```
GROQ_API_KEY=your-free-key-here
```

### Step 4: Run the App
```bash
streamlit run app.py
```

### Step 5: Use It!
1. Enter API key in sidebar (or use .env)
2. Click "Ingest Documents"
3. Ask questions!

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
├── requirements.txt         # Dependencies
├── .env.example             # API key template
└── README.md                # This file
```

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Invalid API key" | Check key is correct, no extra spaces |
| "Rate limit exceeded" | Wait 1 minute, then retry |
| "Module not found" | Run `pip install -r requirements.txt` |
| "Vector store not found" | Click "Ingest Documents" first |

## 📝 License

MIT License - Free to use and modify.

---

**Built with ❤️ using Free APIs (Groq + HuggingFace)**
