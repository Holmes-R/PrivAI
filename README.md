# PrivAI — Private Document RAG

> **Live Link:** [https://privai-qt3n.onrender.com/](https://privai-qt3n.onrender.com/)

A privacy-first Retrieval-Augmented Generation (RAG) system that lets you upload documents (PDF, DOCX, TXT) and ask questions about them using AI — **your data stays under your control**.

---
### Situation
Users needed a way to extract insights from their private documents without sending sensitive data to public AI services like ChatGPT or NotebookLM. Existing solutions either required uploading data to third-party servers or lacked per-document Q&A with persistent chat history.

### Task
Build a self-hosted document Q&A platform where users can upload documents, get AI-generated answers grounded in their content, and maintain a searchable history — with the entire pipeline running on their own infrastructure.

### Action
- Built a **Django + DRF** backend with JWT-based authentication and per-user ChromaDB vector stores
- Integrated **Google Gemini** as the primary LLM with automatic fallback through 4 model variants, plus a local HuggingFace fallback (`flan-t5-small`) when API quota is exhausted
- Added **sentence-transformers** (`all-MiniLM-L6-v2`) for local embedding generation, keeping all vector data in a local ChromaDB instance
- Designed a **glassmorphism UI** with per-document Ask pages, cross-document search, suggested questions, document preview with AI summarization, and chat export
- Implemented **file signature validation** (magic bytes) on both frontend and backend to reject non-document files (images, binaries)
- Deployed on **Render** using Gunicorn with memory-optimized settings

### Result
A fully functional private RAG system deployed and accessible online. Users can upload documents, receive AI-synthesized answers with inline source citations, view chat history per document, and export Q&A conversations — all while keeping embeddings and data on their own instance.

---

## Features

### 📄 Document Management
- Upload PDF, DOCX, and TXT files
- Preview document content with word count and chunk status
- AI-generated document summaries (one-click)
- Delete documents with automatic vector cleanup
- File signature validation — rejects images/binary files at upload time

### 🔍 Cross-Document Q&A
- Ask questions across all your documents at once
- AI suggests 6 contextual questions based on your uploaded content
- Answers synthesized from multiple sources with inline citations (`[Source 1]`, `[Source 2]`)
- Markdown-formatted responses with headings, lists, and bold terms

### 📑 Per-Document Chat
- Dedicated Ask page for each document
- Persistent chat history per user per document
- Follow-up question context (last 3 Q&As included automatically)
- Export chat history as Markdown file

### 🔐 Authentication & Security
- JWT-based authentication (access + refresh tokens)
- Per-user vector collections — no data leakage between users
- All embeddings stored locally in ChromaDB
- Session-free API design (no cookies, no CSRF)

### 🎨 UI/UX
- Glassmorphism design with gradient backgrounds
- Responsive card layout for documents
- Loading states, fade-in animations, smooth transitions
- Light theme (dark mode removed on request)

### 🛡️ Error Resilience
- Gemini API retry with exponential backoff (3 attempts per model)
- Automatic fallback through 4 model variants
- Local HuggingFace model as last resort
- Binary/garbage chunk detection — corrupt chunks filtered before reaching the LLM

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.1, Django REST Framework |
| Auth | SimpleJWT (access + refresh tokens) |
| Vector DB | ChromaDB (persistent, per-user collections) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | Google Gemini (1.5-flash, 2.0-flash-lite, etc.) |
| Local Fallback | HuggingFace (flan-t5-small) |
| Frontend | Django Templates, Bootstrap 5, marked.js |
| Deployment | Render (Gunicorn) |

---

## Quick Start

```bash
# Clone
git clone https://github.com/Holmes-R/PrivAI.git
cd PrivAI

# Set up venv
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Linux/Mac

# Install
pip install -r backend\requirements.txt

# Environment
copy .env.example .env   # Add GEMINI_API_KEY

# Run
python backend\manage.py migrate
python backend\manage.py runserver
```

> **Note:** First start takes ~30s due to sentence-transformers model download.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | — | Google Gemini API key |
| `DJANGO_SECRET_KEY` | No | auto-generated | Django secret |
| `DEBUG` | No | True | Debug mode |
| `ALLOWED_HOSTS` | No | `.onrender.com` | Allowed hosts |

---

## Project Structure

```
backend/
├── document_app/        # Document CRUD, RAG, vector store
│   ├── rag.py           # LLM calls, prompt engineering, fallback
│   ├── vector_store.py  # ChromaDB client, embeddings
│   ├── signals.py       # Auto-index documents on upload
│   └── utils.py         # Text extraction & chunking
├── feedback_app/        # ChatHistory model & API
├── frontend_app/        # Template rendering views
├── auth_app/            # Custom user model & JWT auth
├── privai_django/       # Django settings & URLs
├── templates/           # HTML templates
├── static/              # CSS, JS
└── requirements.txt
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register/` | Register |
| POST | `/auth/login/` | Login |
| GET | `/api/documents/` | List documents |
| POST | `/api/documents/` | Upload document |
| GET | `/api/documents/<id>/preview/` | Preview document |
| GET | `/api/documents/<id>/summarize/` | AI summary |
| GET | `/api/documents/<id>/suggest/` | Per-doc question suggestions |
| POST | `/api/documents/ask/` | Ask question (cross-doc or per-doc) |
| GET | `/api/documents/suggest-global/` | Cross-doc question suggestions |
| POST | `/api/documents/search/` | Semantic search |
| DELETE | `/api/documents/<id>/` | Delete document |
| GET | `/api/history/chat/` | Chat history |

---
