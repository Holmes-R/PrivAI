# app/routes/embed.py
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.models import EmbedRequest
from app.services.chroma import get_collection
from app.services.embedder import Embedder
from app.auth import verify_token

router = APIRouter()

@router.post("/embed")
def embed(payload: EmbedRequest, token=Depends(verify_token)):
    if payload.user_id != token["user_id"]:
        raise HTTPException(403, "Forbidden")

    coll = get_collection(payload.user_id)
    texts = [c.text for c in payload.chunks]
    embeddings = Embedder.get().encode(texts, normalize_embeddings=True).tolist()

    coll.add(
        ids=[f"doc{payload.document_id}_c{i}" for i in range(len(texts))],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{
            "document_id": payload.document_id,
            "title": payload.title
        } for _ in texts]
    )
    return {"status": "indexed"}