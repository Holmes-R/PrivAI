# app/routes/ask.py
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.models import AskRequest, AskResponse
from app.services.chroma import get_collection
from app.services.embedder import Embedder
from app.services.llm import answer
from app.auth import verify_token

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, token=Depends(verify_token)):
    if payload.user_id != token["user_id"]:
        raise HTTPException(403, "Forbidden")

    coll = get_collection(payload.user_id)
    q_emb = Embedder.get().encode([payload.question]).tolist()

    results = coll.query(
        query_embeddings=q_emb,
        n_results=payload.n_results,
        include=["documents", "metadatas", "distances"]
    )

    sources = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        sources.append({
            "text": doc,
            "title": meta["title"],
            "document_id": meta["document_id"],
            "score": round(1 - dist, 4)
        })

    if not sources:
        return AskResponse(answer="I don't know.", sources=[])

    answer_text = answer(payload.question, sources)
    return AskResponse(answer=answer_text, sources=sources)