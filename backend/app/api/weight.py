from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.tracking import WeightLogCreate, WeightLogResponse
from app.services.progress_analyzer import ProgressAnalyzer

router = APIRouter(prefix="/weight", tags=["Weight Tracking"])


@router.post("", response_model=WeightLogResponse, status_code=status.HTTP_201_CREATED)
def log_weight_entry(
    weight_in: WeightLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = ProgressAnalyzer.log_weight(
        db=db,
        user_id=current_user.id,
        weight_kg=weight_in.weight_kg,
        date_str=weight_in.date,
        note=weight_in.note
    )
    return entry


@router.get("/history", response_model=List[WeightLogResponse])
def get_weight_trend_history(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = ProgressAnalyzer.get_weight_history(
        db=db,
        user_id=current_user.id,
        days=days
    )
    return history
