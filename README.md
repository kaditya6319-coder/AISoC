# AISoC — AI-Powered Research Assistant

AISoC is a full-stack AI-powered research assistant that allows users to upload research papers, perform semantic search, and ask questions about selected documents using a Retrieval-Augmented Generation (RAG) pipeline.

The application combines **React.js, FastAPI, PostgreSQL, ChromaDB, Sentence Transformers, and Ollama** to provide document-based AI assistance while keeping LLM inference local.

---

## Features

* Upload research papers in PDF format
* Store document metadata in PostgreSQL
* Extract and process PDF text
* Split documents into searchable chunks
* Generate semantic embeddings using Sentence Transformers
* Store embeddings in ChromaDB
* Perform semantic similarity search
* Retrieve relevant document context
* Generate answers using a locally hosted Ollama LLM
* Ask questions about a selected research paper
* Display retrieved source content
* Select between multiple uploaded documents
* Delete uploaded documents
* REST API communication between frontend and backend
* Local AI processing without relying on an external LLM API

---

## Tech Stack

### Frontend

* React.js
* Vite
* JavaScript
* CSS

### Backend

* Python
* FastAPI
* Uvicorn
* SQLAlchemy
* Pydantic

### Database

* PostgreSQL

Used for:

* Document metadata
* File information
* Upload timestamps
* Document processing status

### Vector Database

* ChromaDB

Used for:

* Storing document embeddings
* Semantic similarity search
* Retrieving relevant document chunks

### AI / Machine Learning

* Sentence Transformers
* `all-MiniLM-L6-v2`
* Ollama
* Llama 3.2 3B

### PDF Processing

* PyPDF

---

## Architecture

```text
                    ┌─────────────────────┐
                    │    React Frontend   │
                    │      Vite + CSS     │
                    └──────────┬──────────┘
                               │
                               │ REST API
                               ▼
                    ┌─────────────────────┐
                    │   FastAPI Backend   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌────────────┐   ┌────────────┐   ┌────────────┐
       │ PostgreSQL │   │  ChromaDB  │   │   Ollama   │
       │            │   │            │   │    LLM     │
       │ Metadata   │   │ Embeddings │   │ Local AI   │
       └────────────┘   └────────────┘   └────────────┘
                               ▲
                               │
                     ┌─────────┴─────────┐
                     │ Sentence         │
                     │ Transformers     │
                     │ Embeddings       │
                     └──────────────────┘
```

---

## RAG Pipeline

AISoC uses a Retrieval-Augmented Generation architecture.

```text
             Research PDF
                  │
                  ▼
          PDF Text Extraction
                  │
                  ▼
             Text Cleaning
                  │
                  ▼
          Text Chunking
                  │
                  ▼
      Sentence Transformer Model
          all-MiniLM-L6-v2
                  │
                  ▼
          Generate Embeddings
                  │
                  ▼
              ChromaDB
          Vector Storage
                  │
                  ▼
          Semantic Search
                  │
                  ▼
       Relevant Document Chunks
                  │
                  ▼
             Context
                  │
                  ▼
          Ollama Local LLM
          Llama 3.2 3B
                  │
                  ▼
          Generated Answer
```

The system retrieves relevant information from the selected research document before sending the retrieved context to the local language model.

This reduces the need for the LLM to rely on information outside the selected document.

---

## Document Processing

When a PDF is uploaded, AISoC performs the following operations:

1. Receives the PDF through the FastAPI upload endpoint.
2. Saves the physical file locally.
3. Creates a document record in PostgreSQL.
4. Extracts text from the PDF using PyPDF.
5. Cleans the extracted text.
6. Splits the text into overlapping chunks.
7. Generates embeddings using Sentence Transformers.
8. Stores embeddings and metadata in ChromaDB.
9. Marks the document as processed.

Each stored chunk contains metadata such as:

```text
document_id
filename
page
chunk_index
```

This allows search results to remain associated with their original research document.

---

## Semantic Search

When a user asks a question:

```text
User Question
      │
      ▼
Question Embedding
      │
      ▼
ChromaDB Similarity Search
      │
      ▼
Relevant Chunks
      │
      ▼
Ranking / Filtering
      │
      ▼
Top Retrieved Context
```

AISoC searches only within the selected document.

The retrieval process also considers:

* Semantic similarity
* Page position
* Research-paper-related keywords
* Bibliography/reference filtering
* Duplicate or highly similar chunks

---

## Local AI Generation

After retrieving relevant context, AISoC sends the context and user question to Ollama.

The application currently uses:

```text
Model: llama3.2:3b
```

The model is instructed to:

* Use only the supplied research context
* Avoid inventing information
* Answer questions directly
* Indicate when the provided context is insufficient
* Provide concise answers

The LLM runs locally through Ollama.

---

## Backend API

The FastAPI backend provides REST endpoints for document management and AI interaction.

### Status

```text
GET /api/status
```

Returns the current backend status.

### Database Status

```text
GET /api/database-status
```

Checks the PostgreSQL database connection.

### Upload Document

```text
POST /api/documents/upload
```

Uploads a PDF and starts document processing and indexing.

### Get Documents

```text
GET /api/documents
```

Returns all uploaded documents.

### Get Single Document

```text
GET /api/documents/{document_id}
```

Returns information about a specific document.

### Delete Document

```text
DELETE /api/documents/{document_id}
```

Deletes the selected document and its physical file.

### Ask AI

```text
POST /api/chat
```

Accepts:

```json
{
  "question": "What is the main topic of this research paper?",
  "document_id": 8
}
```

Returns:

* User question
* Selected document
* AI-generated answer
* Retrieved sources

---

## Example RAG Request

Example request:

```json
{
  "question": "What is the main topic of this research paper?",
  "document_id": 8
}
```

The backend:

```text
Question
   ↓
Embedding
   ↓
ChromaDB Search
   ↓
Relevant PDF Chunks
   ↓
Context Construction
   ↓
Ollama
   ↓
AI Answer
```

Example response structure:

```json
{
  "question": "What is the main topic of this research paper?",
  "document_id": 8,
  "document": "Automated_Testing_of_AI_Models.pdf",
  "answer": "...",
  "sources": []
}
```

---

## Project Structure

```text
AISoC/
│
├── backend/
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   ├── database/
│   │   └── connection.py
│   │
│   ├── models/
│   │   └── document.py
│   │
│   ├── rag/
│   │   ├── service.py
│   │   └── document_processor.py
│   │
│   ├── services/
│   │   └── ollama_service.py
│   │
│   ├── uploads/
│   │
│   ├── chroma_db/
│   │
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   │
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── data/
│
├── .gitignore
└── README.md
```

---

## Database Design

PostgreSQL is used for structured application data.

The document information includes fields such as:

```text
id
filename
file_type
file_path
upload_date
status
```

SQLAlchemy provides the ORM layer between the FastAPI backend and PostgreSQL.

ChromaDB is used separately for vector-based semantic retrieval.

---

## Local Development

### 1. Clone the Repository

```bash
git clone https://github.com/kaditya6319-coder/AISoC.git
cd AISoC
```

---

### 2. Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

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

Configure the required environment variables in:

```text
backend/.env
```

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Ollama Setup

Install Ollama and make sure the required model is available locally.

Pull the model:

```bash
ollama pull llama3.2:3b
```

Start Ollama if it is not already running.

AISoC communicates with:

```text
http://localhost:11434
```

The backend uses the Ollama `/api/generate` endpoint for local AI generation.

---

## Frontend Setup

Open another terminal and navigate to:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

## Application Workflow

```text
1. Start PostgreSQL
        ↓
2. Start Ollama
        ↓
3. Start FastAPI backend
        ↓
4. Start React frontend
        ↓
5. Upload research PDF
        ↓
6. PDF is processed
        ↓
7. Text is chunked
        ↓
8. Embeddings are generated
        ↓
9. Chunks are stored in ChromaDB
        ↓
10. Select a research document
        ↓
11. Ask a question
        ↓
12. Semantic search retrieves relevant chunks
        ↓
13. Retrieved context is sent to Ollama
        ↓
14. Local LLM generates the answer
        ↓
15. Answer and retrieved sources are displayed
```

---

## Security

Sensitive configuration should not be committed to GitHub.

The `.env` file should remain excluded through `.gitignore`.

Do not commit:

* Database passwords
* API keys
* Authentication credentials
* Local secrets
* Private configuration values

---

## Current Project Status

AISoC currently includes:

* React frontend
* FastAPI backend
* PostgreSQL integration
* SQLAlchemy ORM
* Document upload
* Document listing
* Document deletion
* PDF text extraction
* Text cleaning
* Text chunking
* Sentence Transformer embeddings
* ChromaDB vector storage
* Semantic document retrieval
* Document-specific search
* Retrieval-Augmented Generation
* Ollama local LLM integration
* AI-powered document question answering
* Retrieved source display
* Local development workflow

---

## Future Improvements

Potential future improvements include:

* Improved document chunking strategies
* Hybrid keyword + semantic search
* Better citation and page-level source display
* Streaming LLM responses
* Conversation history
* Multi-document research
* Automatic document summarization
* Research paper comparison
* Literature review generation
* Authentication and user accounts
* Background document processing
* Improved ranking and reranking
* Production deployment
* Cloud hosting
* Automated testing

---

## Why AISoC?

AISoC demonstrates the integration of several modern software and AI technologies into a single full-stack application.

The project combines:

```text
Frontend Development
        +
REST API Development
        +
Database Management
        +
Vector Search
        +
Natural Language Processing
        +
Retrieval-Augmented Generation
        +
Local Large Language Models
```

The project is designed as a practical demonstration of how research documents can be processed, searched semantically, and used as context for AI-generated responses.

---

## Author

**Kaditya**

GitHub:

https://github.com/kaditya6319-coder
