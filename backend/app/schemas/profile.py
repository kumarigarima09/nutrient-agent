from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProfileBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Rohan Sharma"})
    age: int = Field(..., ge=12, le=110, json_schema_extra={"example": 28})
    sex: str = Field(..., json_schema_extra={"example": "male"})
    height_cm: float = Field(..., ge=100.0, le=250.0, json_schema_extra={"example": 175.0})
    current_weight_kg: float = Field(..., ge=30.0, le=300.0, json_schema_extra={"example": 78.0})
    target_weight_kg: float = Field(..., ge=30.0, le=300.0, json_schema_extra={"example": 72.0})
    activity_level: str = Field(..., json_schema_extra={"example": "moderate"})
    goal: str = Field(..., json_schema_extra={"example": "weight_loss"})
    diet_type: str = Field(..., json_schema_extra={"example": "vegetarian"})

    food_preferences: Optional[str] = ""
    foods_disliked: Optional[str] = ""
    allergies: Optional[str] = ""
    budget: Optional[str] = "moderate"
    meal_count: Optional[int] = 4
    meal_times: Optional[str] = "08:30,13:00,17:00,20:30"
    cooking_time: Optional[str] = "30_mins"
    exercise_frequency: Optional[str] = "3_4_days"


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    height_cm: Optional[float] = None
    current_weight_kg: Optional[float] = None
    target_weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    goal: Optional[str] = None
    diet_type: Optional[str] = None
    food_preferences: Optional[str] = None
    foods_disliked: Optional[str] = None
    allergies: Optional[str] = None
    budget: Optional[str] = None
    meal_count: Optional[int] = None
    meal_times: Optional[str] = None
    cooking_time: Optional[str] = None
    exercise_frequency: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: int
    user_id: int
    bmr: Optional[float] = None
    tdee: Optional[float] = None
    target_calories: Optional[float] = None
    target_protein_g: Optional[float] = None
    target_carbs_g: Optional[float] = None
    target_fat_g: Optional[float] = None
    target_fiber_g: Optional[float] = None
    target_water_ml: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
