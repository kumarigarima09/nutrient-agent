from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MealItemResponse(BaseModel):
    id: int
    food_id: Optional[int] = None
    food_name: str
    quantity: float
    unit: Optional[str] = "serving"
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    is_estimate: bool
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class MealResponse(BaseModel):
    id: int
    user_id: int
    date: str
    meal_type: str
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_fiber_g: float
    created_at: datetime
    items: List[MealItemResponse] = []

    class Config:
        from_attributes = True


class NaturalLanguageLogRequest(BaseModel):
    text: str = Field(..., example="I ate two eggs, three rotis and one glass of milk")
    date: Optional[str] = None


class ManualItemInput(BaseModel):
    food_name: str
    quantity: float = 1.0
    unit: Optional[str] = "serving"
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: Optional[float] = 0.0


class ManualMealCreateRequest(BaseModel):
    meal_type: str = Field(..., example="lunch")
    date: Optional[str] = None
    items: List[ManualItemInput]
