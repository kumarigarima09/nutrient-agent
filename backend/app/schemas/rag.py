from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    query: str = Field(..., example="What foods contain iron?")
    top_k: Optional[int] = 3


class RAGChunkDetail(BaseModel):
    chunk_id: int
    document_title: str
    source: str
    relevance_score: float
    text: str


class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    source: str
    document: str
    confidence: float
    retrieved_chunks: List[str]
    chunk_details: List[RAGChunkDetail]
    disclaimer: str
