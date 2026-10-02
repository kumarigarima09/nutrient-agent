from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.progress_analyzer import ProgressAnalyzer

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
def get_dashboard(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    date_str = date or datetime.now().strftime("%Y-%m-%d")
    summary = ProgressAnalyzer.get_dashboard_summary(
        db=db,
        user_id=current_user.id,
        date_str=date_str
    )
    return summary
