from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.tracking import WaterLog, ExerciseLog
from app.schemas.meal import NaturalLanguageLogRequest
from app.schemas.tracking import WaterLogCreate, WaterLogResponse, ExerciseLogCreate, ExerciseLogResponse
from app.services.food_logger import FoodLogger
from app.services.progress_analyzer import ProgressAnalyzer

router = APIRouter(prefix="/food-log", tags=["Food Logging"])


@router.post("", status_code=status.HTTP_201_CREATED)
def log_food_natural_language(
    log_request: NaturalLanguageLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = FoodLogger.log_meal_from_text(
        db=db,
        user_id=current_user.id,
        text=log_request.text,
        date_str=log_request.date
    )
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to log food.")
        )
    return result


@router.get("/today")
def get_today_food_log(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = datetime.now().strftime("%Y-%m-%d")
    return ProgressAnalyzer.get_dashboard_summary(db, current_user.id, today)


@router.post("/water", response_model=WaterLogResponse, status_code=status.HTTP_201_CREATED)
def log_water_intake(
    water_in: WaterLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    date_str = water_in.date or datetime.now().strftime("%Y-%m-%d")
    w_log = WaterLog(
        user_id=current_user.id,
        date=date_str,
        amount_ml=water_in.amount_ml
    )
    db.add(w_log)
    db.commit()
    db.refresh(w_log)
    return w_log


@router.post("/exercise", response_model=ExerciseLogResponse, status_code=status.HTTP_201_CREATED)
def log_exercise_activity(
    exercise_in: ExerciseLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    date_str = exercise_in.date or datetime.now().strftime("%Y-%m-%d")
    ex_log = ExerciseLog(
        user_id=current_user.id,
        date=date_str,
        exercise_type=exercise_in.exercise_type,
        duration_minutes=exercise_in.duration_minutes,
        calories_burned=exercise_in.calories_burned or (exercise_in.duration_minutes * 5.0),
        notes=exercise_in.notes
    )
    db.add(ex_log)
    db.commit()
    db.refresh(ex_log)
    return ex_log
