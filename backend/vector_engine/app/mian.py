# app/main.py
from fastapi import FastAPI
from app.routes import embed, ask

app = FastAPI(title="RAG Engine", version="1.0")

app.include_router(embed.router, prefix="/api")
app.include_router(ask.router, prefix="/api")

@app.get("/")
def root():
    return {"status": "RAG Engine Ready"}