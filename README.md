# AISoC — AI-Powered Research Assistant

AISoC is an AI-powered research assistant designed to help users manage and analyze research documents using semantic search, Retrieval-Augmented Generation (RAG), and large language models.

## Features

* Research document upload and management
* Document metadata storage
* Semantic search across research documents
* Retrieval-Augmented Generation (RAG)
* AI-powered question answering
* Document summarization
* Research paper comparison
* Literature review assistance
* Vector-based document retrieval
* REST APIs for frontend-backend communication
* Local LLM integration through Ollama

## Tech Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* ChromaDB
* Sentence Transformers
* Ollama

### Frontend

* React.js

### Database & Storage

* PostgreSQL — structured application data
* ChromaDB — vector embeddings and semantic retrieval

## Project Structure

```text
AISoC/
│
├── backend/
│   ├── api/
│   ├── database/
│   ├── models/
│   ├── rag/
│   ├── services/
│   ├── utilstype/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│
├── .gitignore
└── README.md
```

> Note: `.env` contains local environment configuration and should not be committed to GitHub.

## Architecture

The application follows a full-stack architecture:

```text
React.js Frontend
        │
        ▼
FastAPI REST API
        │
        ├── PostgreSQL
        │
        ├── Document Processing
        │
        ├── ChromaDB
        │
        ├── Sentence Transformers
        │
        └── Ollama LLM
```

## Backend API

The backend provides REST endpoints for application functionality.

### Available Endpoints

```text
GET  /
GET  /health
GET  /api/status
GET  /api/database-status
POST /api/documents/upload
GET  /api/documents
```

FastAPI automatically provides interactive API documentation through Swagger UI.

## Database

PostgreSQL is used to store structured application information and document metadata.

The application uses SQLAlchemy for database connectivity and ORM-based database operations.

## AI / RAG Pipeline

The intended research workflow is:

```text
Research Document
       │
       ▼
Document Processing
       │
       ▼
Text Extraction / Chunking
       │
       ▼
Sentence Transformer Embeddings
       │
       ▼
ChromaDB Vector Storage
       │
       ▼
Semantic Retrieval
       │
       ▼
Relevant Context
       │
       ▼
Ollama Local LLM
       │
       ▼
AI-Generated Response
```

This approach allows the application to retrieve relevant information from research documents before generating an AI response.

## Local Development

### Backend

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the required environment variables in a `.env` file.

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

FastAPI interactive documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server using the project's configured npm script.

## Security

Environment variables and sensitive credentials should be excluded from version control using `.gitignore`.

**Never commit database passwords, API keys, or other sensitive credentials to the repository.**

## Project Status

The project is under active development.

Current implementation includes:

* FastAPI backend
* PostgreSQL database connectivity
* SQLAlchemy database integration
* Document model
* Document upload API
* Document listing API
* Backend health and status endpoints
* Initial frontend structure

Additional AI/RAG functionality is being developed.

## Future Development

Planned functionality includes:

* Document text extraction
* Document chunking
* Embedding generation
* ChromaDB vector storage
* Semantic document search
* RAG-based question answering
* Document summarization
* Research paper comparison
* Literature review generation
* Ollama-based local LLM responses

## Author

**Kaditya**

GitHub: https://github.com/kaditya6319-coder
