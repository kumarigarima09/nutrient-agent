from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.meal import Meal, MealItem
from app.services.vision_service import VisionService
from app.services.food_logger import FoodLogger
from pydantic import BaseModel

router = APIRouter(prefix="/food-image", tags=["Food Vision Analysis"])


class ConfirmLoggedItemsRequest(BaseModel):
    meal_type: str = "lunch"
    date: Optional[str] = None
    items: List[Dict[str, Any]]


@router.post("/analyze")
async def analyze_food_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        content = await file.read()
        analysis = await VisionService.analyze_food_image(
            db=db,
            image_bytes=content,
            filename=file.filename or "food.jpg"
        )
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze food image: {str(e)}"
        )


@router.post("/confirm-log", status_code=status.HTTP_201_CREATED)
def confirm_and_log_image_meal(
    payload: ConfirmLoggedItemsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    date_str = payload.date or datetime.now().strftime("%Y-%m-%d")

    meal = Meal(
        user_id=current_user.id,
        date=date_str,
        meal_type=payload.meal_type,
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

    for it in payload.items:
        qty = float(it.get("estimated_quantity") or it.get("quantity") or 1.0)
        cals = float(it.get("calories", 0.0))
        prot = float(it.get("protein_g", 0.0))
        carbs = float(it.get("carbs_g", 0.0))
        fat = float(it.get("fat_g", 0.0))
        fiber = float(it.get("fiber_g", 0.0))

        item_row = MealItem(
            meal_id=meal.id,
            food_id=it.get("food_id"),
            food_name=it.get("food_name", "Food Item"),
            quantity=qty,
            unit=it.get("estimated_unit") or it.get("unit") or "serving",
            calories=cals,
            protein_g=prot,
            carbs_g=carbs,
            fat_g=fat,
            fiber_g=fiber,
            is_estimate=True,
            notes="Logged from food image analysis"
        )
        db.add(item_row)
        tot_cals += cals
        tot_prot += prot
        tot_carbs += carbs
        tot_fat += fat
        tot_fiber += fiber

    meal.total_calories = round(tot_cals, 1)
    meal.total_protein_g = round(tot_prot, 1)
    meal.total_carbs_g = round(tot_carbs, 1)
    meal.total_fat_g = round(tot_fat, 1)
    meal.total_fiber_g = round(tot_fiber, 1)

    db.commit()
    db.refresh(meal)

    FoodLogger._sync_daily_nutrition_log(db, current_user.id, date_str)

    return {
        "success": True,
        "message": "Meal logged successfully from image analysis!",
        "meal_id": meal.id,
        "total_calories": meal.total_calories,
        "total_protein_g": meal.total_protein_g
    }
