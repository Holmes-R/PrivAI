# document_app/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Document
from .utils import extract_text_from_file, chunk_text
from .vector_store import get_embedding_model, get_user_collection
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Document)
def process_document_for_embeddings(sender, instance, created, **kwargs):
    if not created or not instance.file or instance.file_type not in ["pdf", "docx", "txt"]:
        return  # Only process new local files

    try:
        file_path = instance.file.path
        text = extract_text_from_file(file_path, instance.file_type)
        if not text.strip():
            logger.warning(f"No text extracted from {instance.id}")
            return

        chunks = chunk_text(text)
        model = get_embedding_model()
        embeddings = model.encode(chunks, show_progress_bar=False).tolist()

        collection = get_user_collection(instance.user.id)

        # Add to Chroma
        collection.add(
            ids=[f"doc{instance.id}_chunk{i}" for i in range(len(chunks))],
            embeddings=embeddings,
            documents=chunks,
            metadatas=[{"document_id": instance.id, "title": instance.title} for _ in chunks]
        )

        logger.info(f"Indexed {len(chunks)} chunks for document {instance.id}")
    except Exception as e:
        logger.error(f"Embedding failed for doc {instance.id}: {e}")