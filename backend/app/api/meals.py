from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.meal import Meal, MealItem
from app.schemas.meal import MealResponse, ManualMealCreateRequest
from app.services.food_logger import FoodLogger

router = APIRouter(prefix="/meals", tags=["Meals"])


@router.get("/today", response_model=List[MealResponse])
def get_today_meals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = datetime.now().strftime("%Y-%m-%d")
    meals = db.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.date == today
    ).order_by(Meal.id.asc()).all()
    return meals


@router.get("", response_model=List[MealResponse])
def get_meals_by_date(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    date_str = date or datetime.now().strftime("%Y-%m-%d")
    meals = db.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.date == date_str
    ).order_by(Meal.id.asc()).all()
    return meals


@router.post("", response_model=MealResponse, status_code=status.HTTP_201_CREATED)
def create_manual_meal(
    meal_in: ManualMealCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    date_str = meal_in.date or datetime.now().strftime("%Y-%m-%d")

    meal = Meal(
        user_id=current_user.id,
        date=date_str,
        meal_type=meal_in.meal_type,
        total_calories=0.0,
        total_protein_g=0.0,
        total_carbs_g=0.0,
        total_fat_g=0.0,
        total_fiber_g=0.0
    )
    db.add(meal)
    db.flush()

    tot_cals = 0.0
    tot_prot = 0.0
    tot_carbs = 0.0
    tot_fat = 0.0
    tot_fiber = 0.0

    for item in meal_in.items:
        m_item = MealItem(
            meal_id=meal.id,
            food_name=item.food_name,
            quantity=item.quantity,
            unit=item.unit or "serving",
            calories=item.calories,
            protein_g=item.protein_g,
            carbs_g=item.carbs_g,
            fat_g=item.fat_g,
            fiber_g=item.fiber_g or 0.0,
            is_estimate=False
        )
        db.add(m_item)
        tot_cals += item.calories
        tot_prot += item.protein_g
        tot_carbs += item.carbs_g
        tot_fat += item.fat_g
        tot_fiber += item.fiber_g or 0.0

    meal.total_calories = round(tot_cals, 1)
    meal.total_protein_g = round(tot_prot, 1)
    meal.total_carbs_g = round(tot_carbs, 1)
    meal.total_fat_g = round(tot_fat, 1)
    meal.total_fiber_g = round(tot_fiber, 1)

    db.commit()
    db.refresh(meal)

    # Sync daily summary
    FoodLogger._sync_daily_nutrition_log(db, current_user.id, date_str)
    return meal


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(
    meal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meal = db.query(Meal).filter(
        Meal.id == meal_id,
        Meal.user_id == current_user.id
    ).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    date_str = meal.date
    db.delete(meal)
    db.commit()

    FoodLogger._sync_daily_nutrition_log(db, current_user.id, date_str)
    return None
