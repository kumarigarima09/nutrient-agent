from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.profile import Profile
from app.schemas.nutrition import (
    NutritionCalculateRequest,
    NutritionCalculateResponse,
    GoalFeasibilityRequest,
    GoalFeasibilityResponse
)
from app.services.nutrition_calculator import NutritionCalculator
from app.services.goal_engine import GoalEngine

router = APIRouter(prefix="/nutrition", tags=["Nutrition Engine"])


@router.get("/targets")
def get_user_nutrition_targets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not configured yet."
        )

    return NutritionCalculator.calculate_all(
        weight_kg=profile.current_weight_kg,
        height_cm=profile.height_cm,
        age=profile.age,
        sex=profile.sex,
        activity_level=profile.activity_level,
        goal=profile.goal
    )


@router.post("/calculate", response_model=NutritionCalculateResponse)
def calculate_arbitrary_nutrition(request: NutritionCalculateRequest):
    result = NutritionCalculator.calculate_all(
        weight_kg=request.weight_kg,
        height_cm=request.height_cm,
        age=request.age,
        sex=request.sex,
        activity_level=request.activity_level,
        goal=request.goal,
        custom_deficit=request.custom_deficit,
        custom_surplus=request.custom_surplus,
        custom_protein_per_kg=request.custom_protein_per_kg
    )
    return result


@router.post("/goal-feasibility", response_model=GoalFeasibilityResponse)
def analyze_goal_feasibility(request: GoalFeasibilityRequest):
    return GoalEngine.analyze_goal_feasibility(
        current_weight_kg=request.current_weight_kg,
        target_weight_kg=request.target_weight_kg,
        goal=request.goal,
        tdee=request.tdee
    )
