# Euler: AI-Powered Dutch High School Math Tutor

### Status: In Development

---

## Overview
Euler is an intelligent tutoring system tailored for Dutch high school mathematics. It ingests PDFs (textbooks, worksheets), breaks them into curriculum-aligned “knowledge chunks,” stores embeddings in Supabase, and exposes a conversational Streamlit UI powered by Retrieval-Augmented Generation (RAG).

Key components:
- Ingestion & Chunking via app/ingestion
- Vector store in Supabase
- RAG Agent for context-aware Q&A
- Streamlit frontend for chat & step-by-step walkthroughs



## Key Features
- Automated PDF Ingestion:
  Parse PDFs → segment content → generate embeddings
- Structured Knowledge Chunks:
  Definitions, theorems, examples aligned to Dutch math curriculum
- Supabase Vector Store:
  Secure, scalable similarity search
- RAG-Powered Q&A:
  Combines retrieved chunks with LLM generation for precise explanations
- Interactive Streamlit UI:
  Natural chat interface, follow-ups, optional practice problem generation

---

## Architecture

1. PDF Parser (app/ingestion/pdf2md)
2. Chunker & Embedding (app/ingestion/process_and_store_md)
3. Supabase Vector Store (app/utils/supabase_client.py)
4. RAG Agent (app/agents/wiskunde_expert_agent.py)
5. Streamlit Frontend (frontend/streamlit_app.py)

---

## Setup

1. Clone the repo

   git clone https://github.com/daankaasjager/euler.git
   cd euler

2. Install dependencies with Poetry

   if you don’t already have Poetry:
   ```
   curl -sSL https://install.python-poetry.org | python3 -
    ```

   install & activate virtualenv
   ```
   poetry install
   poetry shell
   ```

3. Configure environment

   cp .env.example .env

   Edit `.env` and fill in:
   - SUPABASE_URL
   - SUPABASE_SERVICE_KEY
   - OLLAM_URL  (or your LLM endpoint)
   - any other credentials

4. Explore workflows via Hydra https://hydra.cc/docs/intro/

   Current moodes:
     split_pdf       # split PDF into chapters or pages
     parse_and_store # parse → markdown → embed & upload
     test_agent      # one-shot “Wat is een kwadraat?”
     delete_data     # clear vector table
     serve_api       # launch Streamlit UI



## Usage Examples
### Split pages 4–5 into a chunk named “bewerkingen”
```
python main.py mode=split_pdf page_range.start=4 page_range.end=5 page_range.name=bewerkingen
```

### Parse & store all PDFs
```
python main.py mode=parse_and_store
```
### Test the RAG agent
```
python main.py mode=test_agent
```

### Serve the Streamlit UI
```
python main.py mode=serve_api
```
→ browse to http://localhost:8501


## Dockerization

Dockerfile (two-stage build):

    # Stage 1: Builder
    FROM python:3.11-slim AS builder
    WORKDIR /app
    RUN pip install poetry
    COPY pyproject.toml poetry.lock ./
    RUN poetry config virtualenvs.create false \
     && poetry install --no-dev --no-root
    COPY . .

    # Stage 2: Runtime
    FROM python:3.11-slim
    WORKDIR /app
    COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
    COPY --from=builder /app /app
    EXPOSE 8501
    ENTRYPOINT ["python", "main.py", "mode=serve_api"]

Build & run:

    docker build -t euler-tutor:latest .
    docker run --env-file .env -p 8501:8501 euler-tutor:latest

## Roadmap
[ ] Button-based chat interface
[ ] Authentication & role-based access
[ ] CI/CD for automated ingestion → indexing
[ ] More practice-problem generators


License
MIT License. See LICENSE for details.
