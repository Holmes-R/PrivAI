import logging
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Document
from .utils import extract_text_from_file, chunk_text
from .vector_store import get_embedding_model, get_user_collection, _get_client

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Document)
def embed_document(sender, instance, created, **kwargs):
    if not created or not instance.file or instance.file_type not in ["pdf", "docx", "txt"]:
        return

    try:
        file_path = instance.file.path
        text = extract_text_from_file(file_path, instance.file_type)
        if not text.strip():
            logger.warning(f"No text in doc {instance.id}")
            return

        chunks = chunk_text(text)
        if not chunks:
            return

        title = instance.title
        titled_chunks = [f"[{title}]: {c}" for c in chunks]

        model = get_embedding_model()
        embeddings = model.encode(titled_chunks, normalize_embeddings=True).tolist()
        collection = get_user_collection(instance.user.id)

        collection.add(
            ids=[f"doc{instance.id}_c{i}" for i in range(len(chunks))],
            embeddings=embeddings,
            documents=titled_chunks,
            metadatas=[{
                "document_id": instance.id,
                "title": title
            } for _ in chunks]
        )

        logger.info(f"Document {instance.id} indexed with {len(chunks)} chunks")

    except Exception as e:
        logger.error(f"Indexing failed for doc {instance.id}: {e}")
