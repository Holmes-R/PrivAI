# app/services/chroma.py
import chromadb
from app.config import settings

_client = None
def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_path)
    return _client

def get_collection(user_id: int):
    return _get_client().get_or_create_collection(name=f"user_{user_id}")
