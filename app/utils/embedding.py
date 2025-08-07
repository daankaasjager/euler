import os
from sentence_transformers import SentenceTransformer
from typing import List

_model = None

def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        model_name = os.getenv("MULTILINGUAL_EMBEDDING", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        _model = SentenceTransformer(model_name)
    return _model

async def get_embedding(text: str) -> List[float]:
    try:
        return get_embedding_model().encode(text).tolist()
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        return [0.0] * 384