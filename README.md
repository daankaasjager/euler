## Euler: AI-Powered Dutch High School Math Tutor

**Status**: 🚧 In Development

---

### Overview

Euler is an intelligent tutoring system designed specifically for Dutch high school students. Leveraging advanced AI techniques and Retrieval-Augmented Generation (RAG), Euler transforms educational PDFs into structured knowledge chunks stored in a Supabase database, enabling a conversational agent that guides students through math concepts via an intuitive Streamlit interface.

### Key Features

* **Automated Content Ingestion**: Upload PDF textbooks or worksheets; Euler parses, segments, and indexes content for efficient retrieval.
* **Knowledge Chunking**: Breaks down complex topics into digestible, curriculum-aligned modules (definitions, theorems, worked examples).
* **Supabase Integration**: Securely stores vector embeddings and metadata, ensuring scalable, real-time access.
* **RAG-Powered Q\&A**: Combines retrieved context with generative responses for accurate, coherent tutoring.
* **Interactive Streamlit UI**: User-friendly chat interface supporting follow-up queries and step-by-step explanations.

### Architecture

1. **PDF Parser**: Converts source documents into raw text.
2. **Chunker & Embedding**: Splits text into logical segments and computes vector embeddings.
3. **Supabase Vector Store**: Indexes embeddings and maintains metadata for quick similarity searches.
4. **RAG Agent**: Retrieves top-k relevant chunks and feeds them to a language model for response generation.
5. **Frontend**: Streamlit app provides chat-based interaction with real-time visualization of referenced materials.

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/euler-tutor.git
   cd euler-tutor
   ```
2. **Create a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your Supabase URL, API key, and ollam urls
   ```

### Usage

1. **Ingest Documents**

   ```bash
   python ingest.py --source ./materials/math_textbook.pdf
   ```
2. **Start the Streamlit UI**

   ```bash
   streamlit run app.py
   ```
3. **Chat with Euler**

   * Ask questions like: *"Leg de stelling van Pythagoras uit met een voorbeeld."*
   * Request step-by-step solutions or ask for additional practice problems.

### Roadmap

* [ ] Make the chat interaction a button interface

### License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.
