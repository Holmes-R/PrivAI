# document_app/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Document
from .utils import extract_text_from_file, chunk_text
from .vector_store import get_embedding_model, get_user_collection
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)

RAG_URL ="http://localhost:8001/api/embed"
JWT_SECRET = "24139ba3293ed808dfcd2f01619579bb129418d6c13976f0f1e9a65ebb33da03"

@receiver(post_save, sender=Document)
def send_to_rag_service(sender, instance, created, **kwargs):
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

        # === PREPARE PAYLOAD ===
        payload = {
            "user_id": instance.user.id,
            "document_id": instance.id,
            "title": instance.title,
            "chunks": [
                {
                    "text": chunk,
                    "title": instance.title,
                    "document_id": instance.id
                }
                for chunk in chunks
            ]
        }

        # === GENERATE JWT ===
        token = jwt.encode(
            {"user_id": instance.user.id},
            JWT_SECRET,
            algorithm="HS256"
        )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # === SEND TO FASTAPI ===
        response = requests.post(RAG_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"Document {instance.id} indexed in RAG service")
        else:
            logger.error(f"RAG sync failed: {response.status_code} {response.text}")

    except Exception as e:
        logger.error(f"RAG indexing failed for doc {instance.id}: {e}")