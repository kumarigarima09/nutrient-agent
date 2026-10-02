from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Core demographics
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    sex = Column(String(20), nullable=False)  # male, female, other
    height_cm = Column(Float, nullable=False)
    current_weight_kg = Column(Float, nullable=False)
    target_weight_kg = Column(Float, nullable=False)

    # Lifestyle & Goals
    activity_level = Column(String(50), nullable=False)  # sedentary, light, moderate, very_active, athlete
    goal = Column(String(50), nullable=False)  # weight_loss, weight_maintenance, weight_gain, muscle_gain, general_health
    diet_type = Column(String(50), nullable=False)  # vegetarian, non_vegetarian, vegan, eggetarian, custom

    # Preferences & Constraints (comma-separated or JSON string)
    food_preferences = Column(Text, nullable=True, default="")
    foods_disliked = Column(Text, nullable=True, default="")
    allergies = Column(Text, nullable=True, default="")
    budget = Column(String(50), nullable=True, default="moderate")  # low, moderate, high
    meal_count = Column(Integer, nullable=True, default=4)
    meal_times = Column(Text, nullable=True, default="")  # e.g., "08:30,13:00,17:00,20:30"
    cooking_time = Column(String(50), nullable=True, default="30_mins")  # quick, 30_mins, elaborate
    exercise_frequency = Column(String(50), nullable=True, default="3_4_days")

    # Deterministic Target Metrics (calculated by nutrition_calculator)
    bmr = Column(Float, nullable=True)
    tdee = Column(Float, nullable=True)
    target_calories = Column(Float, nullable=True)
    target_protein_g = Column(Float, nullable=True)
    target_carbs_g = Column(Float, nullable=True)
    target_fat_g = Column(Float, nullable=True)
    target_fiber_g = Column(Float, nullable=True)
    target_water_ml = Column(Float, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="profile")
