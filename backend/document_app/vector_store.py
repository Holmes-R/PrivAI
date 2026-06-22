# document_app/vector_store.py
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os
from django.conf import settings

_model = None
def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

_client = None
def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=os.path.join(settings.BASE_DIR, "chroma_db"))
    return _client

def get_user_collection(user_id: int):
    collection_name = f"user_{user_id}"
    return _get_client().get_or_create_collection(name=collection_name)
