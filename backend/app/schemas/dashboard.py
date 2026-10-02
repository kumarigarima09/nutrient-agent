from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class MetricItem(BaseModel):
    current: float
    target: float
    remaining: float
    percentage: float


class WaterMetricItem(BaseModel):
    current_ml: float
    target_ml: float
    remaining_ml: float
    percentage: float


class DashboardMetrics(BaseModel):
    calories: MetricItem
    protein: MetricItem
    carbs: MetricItem
    fat: MetricItem
    fiber: MetricItem
    water: WaterMetricItem


class DashboardWeight(BaseModel):
    current_kg: float
    target_kg: float
    trend_sparkline: List[Dict[str, Any]] = []


class ActiveRecommendation(BaseModel):
    text: str
    calorie_delta: float


class DashboardResponse(BaseModel):
    date: str
    user_name: str
    goal: str
    metrics: DashboardMetrics
    weight: DashboardWeight
    today_meals: List[Dict[str, Any]] = []
    active_recommendation: ActiveRecommendation
