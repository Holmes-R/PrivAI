import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        logger.info("Loading embedding model...")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        _model.max_seq_length = 256
        logger.info("Embedding model loaded")
    return _model


_client = None

def _get_client():
    global _client
    if _client is None:
        import chromadb
        from chromadb.config import Settings
        _client = chromadb.PersistentClient(
            path=os.path.join(settings.BASE_DIR, "chroma_db"),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=False,
                is_persistent=True,
            )
        )
    return _client


def get_user_collection(user_id: int):
    collection_name = f"user_{user_id}"
    return _get_client().get_or_create_collection(name=collection_name)
