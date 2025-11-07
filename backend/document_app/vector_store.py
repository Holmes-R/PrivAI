# document_app/vector_store.py
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os
from django.conf import settings

# One model per app (cached)
_model = None
def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')  # 384-dim, fast
    return _model

# Chroma client (persistent)
_client = chromadb.PersistentClient(path=os.path.join(settings.BASE_DIR, "chroma_db"))

def get_user_collection(user_id: int):
    """Each user gets their own collection: user_{id}"""
    collection_name = f"user_{user_id}"
    return _client.get_or_create_collection(name=collection_name)