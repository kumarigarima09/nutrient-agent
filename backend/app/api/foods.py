from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.food import FoodResponse, FoodCreate, ServingCalculateRequest
from app.services.food_service import FoodService

router = APIRouter(prefix="/foods", tags=["Food Database"])


@router.get("", response_model=List[FoodResponse])
def search_foods(
    query: str = Query("", description="Food name search query"),
    category: Optional[str] = Query(None, description="Category filter"),
    diet_type: Optional[str] = Query(None, description="vegetarian, vegan, eggetarian"),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Ensure seed foods exist
    FoodService.seed_initial_foods(db)
    foods = FoodService.search_foods(
        db=db,
        query=query,
        category=category,
        diet_type=diet_type,
        limit=limit,
        user_id=current_user.id
    )
    return foods


@router.get("/{food_id}", response_model=FoodResponse)
def get_food(food_id: int, db: Session = Depends(get_db)):
    food = FoodService.get_food_by_id(db, food_id)
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found."
        )
    return food


@router.post("", response_model=FoodResponse, status_code=status.HTTP_201_CREATED)
def create_custom_food(
    food_in: FoodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    food = FoodService.create_custom_food(
        db=db,
        user_id=current_user.id,
        data=food_in.model_dump()
    )
    return food


@router.post("/calculate-serving")
def calculate_serving(
    request: ServingCalculateRequest,
    db: Session = Depends(get_db)
):
    food = FoodService.get_food_by_id(db, request.food_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food item not found")

    return FoodService.calculate_serving_nutrition(
        food=food,
        quantity=request.quantity,
        unit=request.unit
    )
