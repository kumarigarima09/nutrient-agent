from typing import Optional
from pydantic import BaseModel, Field


class WeightLogCreate(BaseModel):
    weight_kg: float = Field(..., ge=30.0, le=300.0, example=72.5)
    date: Optional[str] = None
    note: Optional[str] = None


class WeightLogResponse(BaseModel):
    id: Optional[int] = None
    date: str
    weight_kg: float
    rolling_avg_7d: Optional[float] = None
    note: Optional[str] = None

    class Config:
        from_attributes = True


class WaterLogCreate(BaseModel):
    amount_ml: float = Field(..., ge=50.0, le=3000.0, example=250.0)
    date: Optional[str] = None


class WaterLogResponse(BaseModel):
    id: int
    date: str
    amount_ml: float

    class Config:
        from_attributes = True


class ExerciseLogCreate(BaseModel):
    date: Optional[str] = None
    exercise_type: str = Field(..., example="Brisk Walking")
    duration_minutes: int = Field(..., ge=1, le=600, example=45)
    calories_burned: Optional[float] = 200.0
    notes: Optional[str] = None


class ExerciseLogResponse(BaseModel):
    id: int
    date: str
    exercise_type: str
    duration_minutes: int
    calories_burned: float
    notes: Optional[str] = None

    class Config:
        from_attributes = True
