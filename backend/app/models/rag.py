from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class RAGDocument(Base):
    __tablename__ = "rag_documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    source_name = Column(String(100), nullable=False)  # WHO, ICMR-NIN, USDA, ISSN, Harvard Health
    author = Column(String(200), nullable=True)
    category = Column(String(100), nullable=True)  # protein, micronutrients, hydration, energy_balance
    published_year = Column(Integer, nullable=True)
    url = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    chunks = relationship("RAGChunk", back_populates="document", cascade="all, delete-orphan")


class RAGChunk(Base):
    __tablename__ = "rag_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("rag_documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding_json = Column(Text, nullable=True)  # stored vector representation
    metadata_json = Column(Text, nullable=True)

    document = relationship("RAGDocument", back_populates="chunks")
