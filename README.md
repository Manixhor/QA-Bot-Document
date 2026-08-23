# 📚 Document Q&A Bot

A Retrieval-Augmented Generation (RAG) powered question answering system that allows users to ask natural language questions about their documents and receive accurate answers with source citations.

## 🎯 What It Does

This bot reads your documents (PDF, TXT, DOCX), breaks them into searchable chunks, and uses AI to answer your questions while citing the exact source of information.

## 🆓 Free API Options

| Provider | Cost | Speed | Quality | Setup |
|----------|------|-------|---------|-------|
| **Google Gemini** | ✅ FREE | Fast | Excellent | Easy |
| **Groq** | ✅ FREE | Ultra-fast | Great | Easy |
| **OpenAI** | 💰 Paid | Fast | Excellent | Easy |

### Get Your Free API Key

#### Option 1: Google Gemini (Recommended)
1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

**Free Limits**: 15 requests/minute, 1M tokens/day

#### Option 2: Groq (Fastest)
1. Go to [console.groq.com/keys](https://console.groq.com/keys)
2. Create account (free)
3. Click "Create API Key"
4. Copy the key

**Free Limits**: 30 requests/minute

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Framework | LangChain |
| Vector DB | ChromaDB |
| Embeddings | Gemini / Groq / OpenAI |
| LLM | Gemini 1.5 Flash / Llama 3.3 / GPT-3.5 |
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
│                              │ (Free API)   │               │
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
│  │  User    │───▶│ Retriever│───▶│   LLM    │───▶ Answer   │
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

### Step 2: Get Free API Key
```bash
# Go to: https://aistudio.google.com/app/apikey
# Create free API key (no credit card needed!)
```

### Step 3: Create .env File
```bash
cp .env.example .env
```

Edit `.env` and add:
```
LLM_PROVIDER=gemini
EMBEDDING_PROVIDER=gemini
GOOGLE_API_KEY=your-free-key-here
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

## 💰 Cost Comparison

| Provider | Cost for Demo | Cost for Production |
|----------|---------------|---------------------|
| Gemini | $0.00 | $0.00 (free tier) |
| Groq | $0.00 | $0.00 (free tier) |
| OpenAI | ~$0.10 | ~$10-100/month |

## ⚠️ Free Tier Limits

### Google Gemini
- 15 requests per minute
- 1 million tokens per day
- Perfect for demos and learning

### Groq
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

**Built with ❤️ using Free APIs**
