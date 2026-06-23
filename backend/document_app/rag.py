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
        words = prompt.split()
        truncated = " ".join(words[:400])
        gen = pipeline("text2text-generation", model="google/flan-t5-small")
        result = gen(truncated, max_new_tokens=100)
        text = result[0]["generated_text"]
        if not text or len(text.strip()) < 10:
            return None
        stripped = text.strip()
        if stripped.startswith("I don") or stripped.startswith("Sorry"):
            return None
        if len(set(stripped.split())) < 3:
            return None
        return text
    except Exception as e:
        logger.warning(f"Local fallback failed: {e}")
        return None


def _extract_text_safe(resp) -> str:
    """Safely extract text from a Gemini response, avoiding ValueError on blocked content."""
    try:
        return resp.text
    except ValueError:
        if resp.candidates:
            reason = resp.candidates[0].finish_reason
            logger.warning(f"Response blocked by Gemini (finish_reason={reason})")
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
                text = _extract_text_safe(resp)
                if text:
                    return text
                logger.warning(f"Empty/blocked response from {model_name}, trying next model")
                break
            except Exception as e:
                err = str(e)
                if "429" in err or "RESOURCE_EXHAUSTED" in err:
                    delay = 2 ** attempt
                    logger.warning(f"429 on {model_name}, retry {attempt+1} in {delay}s")
                    time.sleep(delay)
                elif "404" in err or "not found" in err.lower() or "not supported" in err:
                    break
                elif "image" in err.lower():
                    logger.warning(f"Image data in input: {e}")
                    break
                else:
                    logger.error(f"LLM error: {e}")
                    return None
    return _local_fallback(prompt)


def _is_binary_chunk(text: str) -> bool:
    """Detect if a chunk contains binary/image data (garbage from wrongly uploaded files)."""
    if not text or len(text) < 10:
        return True
    printable = sum(1 for c in text if c.isprintable() or c in "\n\r\t")
    return printable / len(text) < 0.8


def answer_question(user_id: int, question: str, n_results: int = 10, document_id: int = None, history: list = None) -> dict:
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
        if _is_binary_chunk(doc):
            logger.warning(f"Skipping binary chunk from doc {meta.get('document_id')}")
            continue
        sources.append({
            "text": doc,
            "title": meta.get("title", ""),
            "document_id": meta.get("document_id", ""),
            "score": round(1 - dist, 4)
        })

    if not sources:
        return {"answer": "I don't have enough information to answer that question.", "sources": []}

    numbered_sources = []
    for i, s in enumerate(sources, 1):
        numbered_sources.append(f"[Source {i} - {s['title']}]: {s['text']}")
    context = "\n\n".join(numbered_sources)

    history_block = ""
    if history:
        history_block = "\n\nPrevious conversation:\n" + "\n".join(
            [f"User: {h['question']}\nAssistant: {h['answer']}" for h in history[-3:]]
        )

    prompt = f"""You are a thorough research analyst like Google NotebookLM. Your job is to give comprehensive, well-structured answers based ONLY on the provided sources.

Rules:
1. Answer in **clear Markdown** using headings, bullet points, and bold for key terms.
2. **Cite sources inline** using the source number, like: `[Source 1]`, `[Source 2]`, etc.
3. If multiple sources cover the same point, cite all of them: `[Source 1][Source 3]`.
4. **Synthesize information across all provided sources** — if the answer requires combining facts from multiple documents, do so.
5. If the context doesn't contain enough information to fully answer, say what you do know and note what's missing.
6. Start with a direct answer, then go deeper with details.
7. Use short, readable paragraphs.{history_block}

The sources below come from {len(sources)} different documents. Use them all.

Context:
{context}

Question: {question}

Comprehensive answer:"""

    answer_text = _call_llm(prompt)
    if not answer_text or len(answer_text.strip()) < 10:
        answer_text = "I'm currently unable to generate an answer — the free AI model quota may be exhausted. Try again later, or set a GEMINI_API_KEY with billing enabled for uninterrupted access."

    return {"answer": answer_text, "sources": sources}


def summarize_document(text: str) -> str:
    prompt = f"""Summarize the following document in 3-5 bullet points. Be concise and factual.

Document:
{text[:8000]}

Summary:
"""
    return _call_llm(prompt) or "Summary unavailable."


def suggest_global_questions(user_id: int) -> list:
    """Generate 5-6 questions across ALL user documents with diversity."""
    from .models import Document
    from .utils import extract_text_from_file

    try:
        docs = Document.objects.filter(user_id=user_id).order_by("-created_at")[:8]
        sample_texts = []
        for doc in docs:
            if doc.file:
                try:
                    text = extract_text_from_file(doc.file.path, doc.file_type)[:1500]
                    sample_texts.append(f"Document: {doc.title}\n{text}")
                except Exception:
                    continue

        if not sample_texts:
            return _fallback_questions(docs)

        samples = "\n\n".join(sample_texts)

        prompt = f"""Based on these {len(docs)} documents, suggest exactly 6 diverse questions. Each question must require information from a DIFFERENT document or combine multiple documents. Ensure variety across documents.

Documents:
{samples}

6 diverse questions (one per line, numbered):"""

        result = _call_llm(prompt)
        if not result:
            return _fallback_questions(docs)

        questions = []
        for line in result.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            cleaned = line.split(". ", 1)[1] if ". " in line and line[0].isdigit() else line
            if cleaned and len(cleaned) > 5 and cleaned not in questions:
                questions.append(cleaned)

        return questions[:6] if questions else _fallback_questions(docs)

    except Exception as e:
        logger.error(f"Global suggest failed: {e}")
        return _fallback_questions(docs[:4])


def _fallback_questions(docs) -> list:
    """Generate basic questions from document titles."""
    questions = []
    for d in docs[:4]:
        questions.append(f"What are the key points in {d.title}?")
    questions.append("What is the overall summary of all my documents?")
    questions.append("What are the main themes across my documents?")
    return questions


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
