from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class NutritionCalculateRequest(BaseModel):
    weight_kg: float = Field(..., ge=30, le=300)
    height_cm: float = Field(..., ge=100, le=250)
    age: int = Field(..., ge=10, le=120)
    sex: str = Field(..., example="male")
    activity_level: str = Field(..., example="moderate")
    goal: str = Field(..., example="weight_loss")
    custom_deficit: Optional[float] = None
    custom_surplus: Optional[float] = None
    custom_protein_per_kg: Optional[float] = None


class MacroDistribution(BaseModel):
    protein_kcal: float
    carbs_kcal: float
    fat_kcal: float
    protein_pct: float
    carbs_pct: float
    fat_pct: float


class ProteinRange(BaseModel):
    min_g: float
    max_g: float
    grams_per_kg: float


class NutritionCalculateResponse(BaseModel):
    bmr: float
    tdee: float
    target_calories: float
    target_protein_g: float
    protein_range: ProteinRange
    target_carbs_g: float
    target_fat_g: float
    target_fiber_g: float
    target_water_ml: float
    macro_distribution: MacroDistribution
    formula_info: Dict[str, Any]


class GoalFeasibilityRequest(BaseModel):
    current_weight_kg: float
    target_weight_kg: float
    goal: str
    tdee: float


class GoalFeasibilityResponse(BaseModel):
    is_valid: bool
    goal_type: Optional[str] = None
    weight_to_change_kg: Optional[float] = None
    recommended_weekly_rate_kg: Optional[float] = None
    estimated_weeks: Optional[float] = None
    suggested_daily_deficit_kcal: Optional[float] = None
    suggested_daily_surplus_kcal: Optional[float] = None
    projected_daily_target_kcal: Optional[float] = None
    guidance: str
