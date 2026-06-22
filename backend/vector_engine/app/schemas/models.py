# app/schemas/models.py
from pydantic import BaseModel
from typing import List

class Chunk(BaseModel):
    text: str
    title: str
    document_id: int

class EmbedRequest(BaseModel):
    user_id: int
    document_id: int
    title: str
    chunks: List[Chunk]

class AskRequest(BaseModel):
    user_id: int
    question: str
    n_results: int = 5

class AskResponse(BaseModel):
    answer: str
    sources: List[dict]