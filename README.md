# Corporate AI Assistant Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?style=for-the-badge&logo=openai&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Production-ready RAG-based AI Assistant that lets you chat with your documents using LLMs.**

[Features](#features) · [Architecture](#architecture) · [Quick Start](#quick-start) · [API Reference](#api-reference) · [Docker](#docker-deployment)

</div>

---

## Features

| Feature | Description |
|---------|-------------|
| **Document Upload** | Upload PDF, TXT, LOG files — auto-parsed, chunked & embedded |
| **RAG Pipeline** | Semantic search over your documents with context-aware answers |
| **Real-time Chat** | ChatGPT-like streaming via WebSocket |
| **Source Citations** | See exactly which document/page each answer comes from |
| **Multi-user** | JWT auth with per-user isolated documents & chat history |
| **Model Switching** | Switch between GPT-3.5 Turbo, GPT-4, GPT-4 Turbo on the fly |
| **Docker Ready** | One command deploy with docker-compose |

## Architecture

```
┌──────────────────┐     ┌──────────────────────────────────────────────────┐
│                  │     │                   Backend (FastAPI)              │
│   React/Vite     │     │                                                  │
│   Frontend       │────▶│  API Layer ──▶ Service Layer ──▶ AI Pipeline     │
│                  │HTTP │  (REST+WS)     (Business)        │               │
│  - TailwindCSS   │     │                                  ├── Embeddings  │
│  - Zustand       │ WS  │  Auth (JWT)    Repository        │   (OpenAI)    │
│  - React Query   │────▶│  Middleware     (SQLAlchemy)      ├── VectorDB   │
│                  │     │                                  │   (FAISS)     │
└──────────────────┘     │                 SQLite DB         └── LLM        │
                         │                                      (OpenAI)    │
                         └──────────────────────────────────────────────────┘
```

### How RAG Works

```
User Question
     │
     ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│  Embed the  │───▶│  Search in   │───▶│  Build      │───▶│  Stream LLM  │
│  Question   │    │  FAISS Index │    │  Prompt +   │    │  Response    │
│  (OpenAI)   │    │  (Top-K)     │    │  Context    │    │  (GPT-4)     │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy (async), Pydantic v2 |
| **Frontend** | React 18, Vite 5, TailwindCSS, Zustand, React Router |
| **AI/ML** | OpenAI GPT-3.5/4, text-embedding-ada-002, FAISS |
| **Database** | SQLite (async via aiosqlite) |
| **Auth** | JWT (python-jose), bcrypt |
| **Real-time** | WebSocket (native FastAPI) |
| **PDF Parsing** | PyMuPDF (fitz) |
| **DevOps** | Docker, docker-compose, Nginx |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- OpenAI API Key ([get one here](https://platform.openai.com/api-keys))

### 1. Clone & Configure

```bash
git clone https://github.com/furkanbaskurthub-lgtm/corporate-ai-assistant.git
cd corporate-ai-assistant

# Copy and edit environment variables
cp .env.example backend/.env
```

Edit `backend/.env` and set your **OPENAI_API_KEY**:

```env
OPENAI_API_KEY="sk-proj-your-actual-key-here"
SECRET_KEY="generate-a-random-secret-key"
```

> **Tip:** Generate a secret key with: `python -c "import secrets; print(secrets.token_hex(32))"`

### 2. Start Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Open in Browser

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **API Docs** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/health |

## Docker Deployment

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost |
| **Backend API** | http://localhost:8000 |

## Project Structure

```
corporate-ai-assistant/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py           # Register, Login, Me
│   │   │       ├── chat.py           # Sessions, Messages, WebSocket
│   │   │       ├── documents.py      # Upload, List, Delete
│   │   │       └── users.py          # Stats, Models
│   │   ├── ai/
│   │   │   ├── document_processor.py # PDF/TXT parsing & chunking
│   │   │   ├── embeddings.py         # OpenAI embedding manager
│   │   │   ├── rag_pipeline.py       # Query → Retrieve → Generate
│   │   │   └── vector_store.py       # FAISS index management
│   │   ├── core/
│   │   │   ├── config.py             # Pydantic Settings
│   │   │   ├── security.py           # JWT + bcrypt
│   │   │   └── logging_config.py     # Structured logging
│   │   ├── db/
│   │   │   ├── database.py           # Async SQLAlchemy engine
│   │   │   └── repositories/         # Data access layer
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   ├── schemas/                  # Pydantic request/response
│   │   ├── services/                 # Business logic layer
│   │   └── main.py                   # FastAPI app entry point
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Auth/                 # LoginForm, RegisterForm
│   │   │   ├── Chat/                 # ChatWindow, MessageList, Input
│   │   │   ├── Documents/            # Upload, DocumentList
│   │   │   └── Layout/               # Sidebar, Header
│   │   ├── pages/                    # Route pages
│   │   ├── hooks/                    # useAuth, useDocuments
│   │   ├── services/                 # API & WebSocket clients
│   │   └── stores/                   # Zustand state management
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Register new user |
| `POST` | `/api/v1/auth/login` | Login (returns JWT) |
| `GET` | `/api/v1/auth/me` | Get current user info |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/documents/upload` | Upload a document (multipart) |
| `GET` | `/api/v1/documents/` | List user's documents |
| `DELETE` | `/api/v1/documents/{id}` | Delete a document |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chat/sessions` | Create chat session |
| `GET` | `/api/v1/chat/sessions` | List chat sessions |
| `GET` | `/api/v1/chat/sessions/{id}/messages` | Get message history |
| `DELETE` | `/api/v1/chat/sessions/{id}` | Delete a session |
| `WS` | `/api/v1/chat/ws/{session_id}?token=JWT` | Real-time streaming chat |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/users/stats` | User statistics |
| `GET` | `/api/v1/users/models` | Available AI models |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | **Required.** Your OpenAI API key | — |
| `SECRET_KEY` | JWT signing secret | `change-this...` |
| `DATABASE_URL` | SQLAlchemy DB connection | `sqlite+aiosqlite:///./ai_assistant.db` |
| `OPENAI_MODEL` | Default LLM model | `gpt-3.5-turbo` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | `text-embedding-ada-002` |
| `CHUNK_SIZE` | Document chunk size (chars) | `1000` |
| `CHUNK_OVERLAP` | Overlap between chunks | `200` |
| `TOP_K_RESULTS` | Number of context chunks | `5` |
| `MAX_FILE_SIZE` | Max upload size (bytes) | `52428800` (50MB) |
| `DEBUG` | Enable /docs endpoint | `true` |

## Usage Guide

1. **Register** — Create an account at the login page
2. **Upload Documents** — Go to Documents page, drag & drop PDF/TXT/LOG files
3. **Wait for Processing** — Files are parsed, chunked, and embedded automatically
4. **Start Chatting** — Open a new chat session and ask questions about your documents
5. **View Sources** — Each AI response shows which document/page the information came from

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

---

<div align="center">

**Built with FastAPI + React + OpenAI + FAISS**

</div>
