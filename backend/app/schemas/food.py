from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class FoodServingResponse(BaseModel):
    id: int
    serving_name: str
    serving_multiplier: float
    gram_weight: Optional[float] = None

    class Config:
        from_attributes = True


class FoodResponse(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    serving_size: str
    serving_unit: Optional[str] = "serving"
    serving_weight_g: Optional[float] = 100.0
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    micronutrients: Optional[str] = "{}"
    diet_tags: Optional[str] = ""
    is_custom: bool = False
    servings: List[FoodServingResponse] = []

    class Config:
        from_attributes = True


class FoodCreate(BaseModel):
    name: str = Field(..., example="Oat Milk")
    category: Optional[str] = "Dairy Alternatives"
    serving_size: str = Field(..., example="1 glass (250ml)")
    serving_unit: Optional[str] = "glass"
    serving_weight_g: Optional[float] = 250.0
    calories: float = Field(..., ge=0)
    protein_g: float = Field(..., ge=0)
    carbs_g: float = Field(..., ge=0)
    fat_g: float = Field(..., ge=0)
    fiber_g: Optional[float] = 0.0
    diet_tags: Optional[str] = "vegan,vegetarian"
    micronutrients: Optional[Dict[str, Any]] = None


class ServingCalculateRequest(BaseModel):
    food_id: int
    quantity: float = 1.0
    unit: Optional[str] = None
