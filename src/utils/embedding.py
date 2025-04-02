# src/utils/embedding.py
import os
from sentence_transformers import SentenceTransformer

_model = None

def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        model_name = os.getenv("MULTILINGUAL_EMBEDDING", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        _model = SentenceTransformer(model_name)
    return _model
