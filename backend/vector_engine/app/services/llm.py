import time
import logging
from google import genai
from app.config import settings

logger = logging.getLogger(__name__)
client = genai.Client(api_key=settings.gemini_api_key)

GEMINI_MODELS = [
    "gemini-1.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash-8b",
    "gemini-2.0-flash",
]


def _local_fallback(prompt: str) -> str:
    try:
        from transformers import pipeline
        gen = pipeline("text2text-generation", model="google/flan-t5-small")
        result = gen(prompt, max_new_tokens=200, temperature=0.3)
        return result[0]["generated_text"]
    except Exception as e:
        logger.warning(f"Local fallback failed: {e}")
        return None


def answer(question: str, chunks: list) -> str:
    context = "\n\n".join([f"[{c['title']}]: {c['text']}" for c in chunks])
    prompt = f"""You are a helpful and intelligent assistant. Answer the following question using ONLY the provided context. 
If the answer is not contained in the context, say "I don't have enough information to answer that based on the provided documents."

IMPORTANT: Format your response in a neat, clean, and highly readable way using Markdown. 
- Use headings (##) for structure
- Use bullet points or numbered lists for multiple items
- Break text into short, readable paragraphs
- Use bold (**text**) for emphasis on key terms

CONTEXT:
{context}

QUESTION: 
{question}

NEAT AND FORMATTED ANSWER:"""

    for model_name in GEMINI_MODELS:
        for attempt in range(3):
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return resp.text
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    delay = 2 ** attempt
                    logger.warning(f"429 on {model_name}, retry {attempt+1} in {delay}s")
                    time.sleep(delay)
                elif "404" in err_str or "not found" in err_str.lower() or "not supported" in err_str:
                    break
                else:
                    raise

    logger.info("All Gemini models exhausted, trying local fallback")
    local_answer = _local_fallback(prompt)
    if local_answer:
        return local_answer

    return "I'm sorry, all AI models are currently unavailable (free tier quota exceeded)."
