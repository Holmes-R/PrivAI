import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

GEMINI_MODELS = [
    "gemini-1.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash-8b",
    "gemini-2.0-flash",
]


def _get_client():
    from google import genai
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def _local_fallback(prompt: str) -> str:
    try:
        from transformers import pipeline
        gen = pipeline("text2text-generation", model="google/flan-t5-small")
        result = gen(prompt, max_new_tokens=200, temperature=0.3)
        return result[0]["generated_text"]
    except Exception as e:
        logger.warning(f"Local fallback failed: {e}")
        return None


def _call_llm(prompt: str) -> str:
    client = _get_client()
    for model_name in GEMINI_MODELS:
        for attempt in range(3):
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return resp.text
            except Exception as e:
                err = str(e)
                if "429" in err or "RESOURCE_EXHAUSTED" in err:
                    delay = 2 ** attempt
                    logger.warning(f"429 on {model_name}, retry {attempt+1} in {delay}s")
                    time.sleep(delay)
                elif "404" in err or "not found" in err.lower() or "not supported" in err:
                    break
                else:
                    logger.error(f"LLM error: {e}")
                    return None
    return _local_fallback(prompt)


def answer_question(user_id: int, question: str, n_results: int = 5, document_id: int = None, history: list = None) -> dict:
    from .vector_store import get_embedding_model, get_user_collection

    if not settings.GEMINI_API_KEY:
        return {"answer": "Gemini API key not configured.", "sources": []}

    model = get_embedding_model()
    query_emb = model.encode([question]).tolist()
    collection = get_user_collection(user_id)
    where_filter = {"document_id": document_id} if document_id is not None else None

    results = collection.query(
        query_embeddings=query_emb,
        n_results=n_results,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )

    sources = []
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        sources.append({
            "text": doc,
            "title": meta.get("title", ""),
            "document_id": meta.get("document_id", ""),
            "score": round(1 - dist, 4)
        })

    if not sources:
        return {"answer": "I don't have enough information to answer that question.", "sources": []}

    context = "\n\n".join([f"[{s['title']}]: {s['text']}" for s in sources])

    history_block = ""
    if history:
        history_block = "\n\nPrevious conversation:\n" + "\n".join(
            [f"User: {h['question']}\nAssistant: {h['answer']}" for h in history[-3:]]
        )

    prompt = f"""You are a precise document analyst. Answer the question using ONLY the context below. If the context doesn't contain enough information, say so.{history_block}

Context:
{context}

Question: {question}
Answer:"""

    answer_text = _call_llm(prompt)
    if not answer_text:
        answer_text = _local_fallback(prompt) or "AI temporarily unavailable."

    return {"answer": answer_text, "sources": sources}


def summarize_document(text: str) -> str:
    prompt = f"""Summarize the following document in 3-5 bullet points. Be concise and factual.

Document:
{text[:8000]}

Summary:
"""
    return _call_llm(prompt) or "Summary unavailable."


def suggest_questions(text: str) -> list:
    prompt = f"""Based on this document, suggest 4 specific questions a user might want to ask. Return them as a simple numbered list.

Document:
{text[:6000]}

Suggested questions:"""
    result = _call_llm(prompt)
    if not result:
        return ["What is this document about?", "What are the key points?", "Who is this relevant to?", "What actions are needed?"]
    questions = [q.split(". ", 1)[1] if ". " in q else q for q in result.strip().split("\n") if q.strip()]
    return questions[:4]
