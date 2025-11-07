# app/services/llm.py
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)

def answer(question: str, chunks: list) -> str:
    context = "\n\n".join([f"[{c['title']}]: {c['text']}" for c in chunks])
    prompt = f"""Answer using only this context:

{context}

Question: {question}
Answer:"""

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )
    return resp.choices[0].message.content