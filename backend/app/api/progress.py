from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.progress_analyzer import ProgressAnalyzer

router = APIRouter(prefix="/progress", tags=["Progress & Analytics"])


@router.get("/weekly")
def get_weekly_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analysis = ProgressAnalyzer.analyze_weekly_progress(
        db=db,
        user_id=current_user.id
    )
    return analysis
