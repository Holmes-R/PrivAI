# app/services/embedder.py
from sentence_transformers import SentenceTransformer

class Embedder:
    _model = None
    @classmethod
    def get(cls):
        if cls._model is None:
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
        return cls._model