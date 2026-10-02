from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.rag import RAGDocument
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from app.services.rag_service import RAGRetriever

router = APIRouter(prefix="/rag", tags=["Nutrition Evidence RAG"])


@router.post("/query", response_model=RAGQueryResponse)
def query_nutrition_evidence(
    request: RAGQueryRequest,
    db: Session = Depends(get_db)
):
    result = RAGRetriever.retrieve_evidence(
        db=db,
        query=request.query,
        top_k=request.top_k or 3
    )
    return result


@router.get("/documents")
def list_evidence_documents(db: Session = Depends(get_db)):
    RAGRetriever.seed_evidence_documents(db)
    docs = db.query(RAGDocument).all()
    return [
        {
            "id": d.id,
            "title": d.title,
            "source_name": d.source_name,
            "author": d.author,
            "category": d.category,
            "published_year": d.published_year,
            "url": d.url
        }
        for d in docs
    ]
