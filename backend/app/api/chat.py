from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatSessionResponse,
    ChatMessageResponse
)
from app.services.nutrition_agent import NutritionAgent

router = APIRouter(prefix="/chat", tags=["AI Nutrition Agent Chat"])


@router.post("", response_model=ChatResponse)
async def chat_with_agent(
    chat_in: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Ensure session exists or create one
    session = None
    if chat_in.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == chat_in.session_id,
            ChatSession.user_id == current_user.id
        ).first()

    if not session:
        session = ChatSession(
            user_id=current_user.id,
            title=f"Nutrition Consultation ({chat_in.message[:25]}...)"
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    response = await NutritionAgent.chat(
        db=db,
        user_id=current_user.id,
        session_id=session.id,
        user_message=chat_in.message
    )

    return ChatResponse(
        session_id=session.id,
        role=response["role"],
        content=response["content"],
        tool_calls_executed=response.get("tool_calls_executed", []),
        safety_disclaimer=response.get("safety_disclaimer")
    )


@router.get("/sessions", response_model=List[ChatSessionResponse])
def get_user_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(desc(ChatSession.updated_at)).all()
    return sessions


@router.get("/history", response_model=List[ChatMessageResponse])
def get_session_history(
    session_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not session_id:
        latest_session = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id
        ).order_by(desc(ChatSession.updated_at)).first()
        if not latest_session:
            return []
        session_id = latest_session.id

    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.id.asc()).all()
    return messages


@router.post("/sessions", response_model=ChatSessionResponse)
def create_new_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = ChatSession(
        user_id=current_user.id,
        title="New Nutrition Consultation"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session
