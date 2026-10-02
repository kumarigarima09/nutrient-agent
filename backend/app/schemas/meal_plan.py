from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class MealPlanGenerateRequest(BaseModel):
    plan_date: Optional[str] = None


class MealPlanResponse(BaseModel):
    id: int
    user_id: int
    title: str
    plan_date: str
    target_calories: float
    target_protein: float
    target_carbs: float
    target_fat: float
    plan_data: str  # JSON string
    status: str

    class Config:
        from_attributes = True


class SubstitutionRequest(BaseModel):
    food_name: str = Field(..., example="Paneer")
    target_calories: Optional[float] = None
    target_protein: Optional[float] = None


class SubstituteOption(BaseModel):
    substitute_food: str
    suggested_quantity: float
    serving_unit: str
    serving_description: str
    nutrition: Dict[str, float]
    calorie_difference: float
    protein_difference: float
    fit_note: str


class SubstitutionResponse(BaseModel):
    original_food: str
    target_calories: float
    target_protein_g: float
    diet_type: str
    substitutes: List[SubstituteOption]
    guidance: str
