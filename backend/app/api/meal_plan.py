import json
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.profile import Profile
from app.models.meal_plan import MealPlan
from app.schemas.meal_plan import (
    MealPlanGenerateRequest,
    MealPlanResponse,
    SubstitutionRequest,
    SubstitutionResponse
)
from app.services.meal_planner import MealPlanner
from app.services.substitution_engine import SubstitutionEngine
from app.services.food_logger import FoodLogger
from app.models.meal import Meal, MealItem

router = APIRouter(prefix="/meal-plan", tags=["Meal Planner"])


@router.post("/generate", status_code=status.HTTP_201_CREATED)
def generate_meal_plan(
    request: MealPlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not configured yet. Complete onboarding first."
        )

    plan_date = request.plan_date or datetime.now().strftime("%Y-%m-%d")
    plan_dict = MealPlanner.generate_daily_plan(db, profile, plan_date)
    return plan_dict


@router.post("/weekly/generate", status_code=status.HTTP_201_CREATED)
def generate_weekly_meal_plan(
    request: MealPlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not configured yet. Complete onboarding first."
        )
    return MealPlanner.generate_weekly_plan(db, profile, request.plan_date)


@router.get("/weekly")
def get_weekly_meal_plan(
    start_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not configured yet. Complete onboarding first."
        )
    return MealPlanner.get_weekly_plan(db, current_user.id, start_date)


@router.get("/grocery-list")
def get_grocery_list(
    start_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not configured yet. Complete onboarding first."
        )
    return MealPlanner.generate_grocery_list(db, current_user.id, start_date)


@router.get("/current")
def get_current_meal_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plan = db.query(MealPlan).filter(
        MealPlan.user_id == current_user.id,
        MealPlan.status == "active"
    ).order_by(desc(MealPlan.id)).first()

    if not plan:
        # Generate one on the fly if profile exists
        profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
        if profile:
            return MealPlanner.generate_daily_plan(db, profile)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active meal plan found. Generate one first."
        )

    return {
        "id": plan.id,
        "title": plan.title,
        "plan_date": plan.plan_date,
        "target_calories": plan.target_calories,
        "target_protein": plan.target_protein,
        "target_carbs": plan.target_carbs,
        "target_fat": plan.target_fat,
        "meals": json.loads(plan.plan_data),
        "status": plan.status
    }


@router.put("/{plan_id}")
def update_meal_plan(
    plan_id: int,
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plan = db.query(MealPlan).filter(
        MealPlan.id == plan_id,
        MealPlan.user_id == current_user.id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    if "title" in update_data:
        plan.title = update_data["title"]
    if "status" in update_data:
        plan.status = update_data["status"]
    if "meals" in update_data:
        plan.plan_data = json.dumps(update_data["meals"])

    db.commit()
    db.refresh(plan)
    return {
        "id": plan.id,
        "title": plan.title,
        "plan_date": plan.plan_date,
        "status": plan.status,
        "meals": json.loads(plan.plan_data)
    }


@router.post("/substitute", response_model=SubstitutionResponse)
def get_food_substitutes(
    sub_in: SubstitutionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    diet_type = profile.diet_type if profile else "vegetarian"
    allergies = profile.allergies if profile else ""
    user_prefs = profile.food_preferences if profile else ""

    result = SubstitutionEngine.suggest_substitution(
        db=db,
        food_name=sub_in.food_name,
        target_calories=sub_in.target_calories,
        target_protein=sub_in.target_protein,
        diet_type=diet_type,
        allergies=allergies,
        user_preferences=user_prefs
    )
    return result


@router.post("/log-slot-to-today/{plan_id}/{slot_name}")
def log_plan_slot_to_today(
    plan_id: int,
    slot_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logs an entire planned meal slot (e.g. breakfast or lunch) directly into today's active meal log.
    """
    plan = db.query(MealPlan).filter(
        MealPlan.id == plan_id,
        MealPlan.user_id == current_user.id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    meals_data = json.loads(plan.plan_data)
    slot_data = meals_data.get(slot_name)
    if not slot_data:
        raise HTTPException(status_code=400, detail=f"Slot '{slot_name}' not found in plan")

    today_str = datetime.now().strftime("%Y-%m-%d")
    meal = Meal(
        user_id=current_user.id,
        date=today_str,
        meal_type=slot_name,
        total_calories=slot_data["total_calories"],
        total_protein_g=slot_data["total_protein_g"],
        total_carbs_g=slot_data["total_carbs_g"],
        total_fat_g=slot_data["total_fat_g"],
        total_fiber_g=slot_data.get("total_fiber_g", 0.0),
    )
    db.add(meal)
    db.flush()

    for item in slot_data["items"]:
        m_item = MealItem(
            meal_id=meal.id,
            food_id=item.get("food_id"),
            food_name=item["food_name"],
            quantity=item["quantity"],
            unit=item["unit"],
            calories=item["calories"],
            protein_g=item["protein_g"],
            carbs_g=item["carbs_g"],
            fat_g=item["fat_g"],
            fiber_g=item.get("fiber_g", 0.0),
            is_estimate=False,
            notes="Logged from active meal plan"
        )
        db.add(m_item)

    db.commit()
    db.refresh(meal)

    # Sync daily log
    FoodLogger._sync_daily_nutrition_log(db, current_user.id, today_str)

    return {
        "success": True,
        "message": f"Successfully logged {slot_data['meal_name']} to today's meals!",
        "meal_id": meal.id
    }
