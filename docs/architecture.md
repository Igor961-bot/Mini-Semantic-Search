# Architecture overview

## Project idea

The project is a lightweight semantic-search system over scientific documents.
It is inspired by the retrieval part of RAG, but it intentionally does not use an LLM
generation layer because the target environment is a student laptop with limited hardware.

The system supports:

- ingestion from two external open-data sources: `OpenAlex` and `Europe PMC`
- optional upload of a local TXT file
- text extraction from PDF/XML
- chunking into smaller passages
- embeddings stored in `ChromaDB`
- semantic search through a REST API and a web frontend

## Layered architecture

### 1. Presentation layer

- static web frontend in `HTML/CSS/JS`
- FastAPI automatically generated Swagger documentation at `/docs`

### 2. Application layer

- REST API endpoints
- ingestion orchestration
- search orchestration
- validation of requests and error handling

### 3. Processing layer

- adapters for external data sources
- PDF text extraction with `pypdf`
- XML full-text extraction for Europe PMC
- chunking with overlap
- metadata preparation before storage

### 4. Data layer

- persistent `ChromaDB` collection with chunk text and metadata
- local filesystem logs

## Deployment assumption

The target deployment is a single virtual machine.
The whole application stack lives on that VM:

- FastAPI backend
- static frontend served by the backend
- ChromaDB persistence directory
- log files
- Docker runtime

The user connects from another machine through the VM network address, for example:

- `http://<VM_IP>:8000`

This is why the project keeps the frontend and backend together in one deployable service.
It is simpler to present and easier to run on a university VM.

## Main components and responsibilities

- `app/api/`
  - HTTP endpoints
- `app/services/ingestion_service.py`
  - imports documents, runs chunking and writes to the vector database
- `app/services/search_service.py`
  - handles semantic search and statistics
- `app/services/vector_store.py`
  - encapsulates all ChromaDB operations
- `app/sources/openalex_source.py`
  - fetches academic works from OpenAlex, prefers PDF, falls back to abstract
- `app/sources/europepmc_source.py`
  - fetches open-access biomedical articles from Europe PMC and reads XML full text
- `static/`
  - simple student-level frontend

## Data flow

1. The user starts ingestion from the frontend or API.
2. The selected adapter downloads metadata and content from OpenAlex or Europe PMC.
3. The processing layer extracts readable text from PDF or XML.
4. The text is split into overlapping chunks.
5. Each chunk is embedded and stored in ChromaDB.
6. The user submits a search query.
7. ChromaDB returns the most similar chunks.
8. The backend returns ranked results with document metadata and source links.

## Why there is no LLM answer generation

The original idea came from RAG, but the project stops at the retrieval layer.
This is a deliberate design choice:

- lower hardware requirements
- easier deployment on CPU-only machines
- simpler debugging and testing
- still demonstrates a full data pipeline and semantic retrieval

## UML diagrams

- component diagram: [component-diagram.puml](/C:/Users/igorw/Desktop/studia/sem6/ASI/docs/component-diagram.puml)
- deployment diagram: [deployment-diagram.puml](/C:/Users/igorw/Desktop/studia/sem6/ASI/docs/deployment-diagram.puml)
