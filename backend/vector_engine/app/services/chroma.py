# app/services/chroma.py
import chromadb
from app.config import settings

client = chromadb.PersistentClient(path=settings.chroma_path)

def get_collection(user_id: int):
    return client.get_or_create_collection(name=f"user_{user_id}")