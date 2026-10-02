from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True, nullable=False)
    category = Column(String(50), index=True, nullable=True)  # grains, dairy, poultry, legumes, fruits, nuts, etc.
    serving_size = Column(String(100), nullable=False)  # e.g., "1 large egg", "1 medium roti (35g)", "1 bowl (150g)"
    serving_unit = Column(String(50), nullable=True, default="serving")
    serving_weight_g = Column(Float, nullable=True, default=100.0)
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, nullable=False)
    carbs_g = Column(Float, nullable=False)
    fat_g = Column(Float, nullable=False)
    fiber_g = Column(Float, nullable=False, default=0.0)
    micronutrients = Column(Text, nullable=True, default="{}")  # JSON string: {"iron_mg": 2.1, "calcium_mg": 120}
    diet_tags = Column(String(200), nullable=True, default="")  # vegetarian, vegan, eggetarian, gluten_free
    is_custom = Column(Boolean, default=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    servings = relationship("FoodServing", back_populates="food", cascade="all, delete-orphan")
    meal_items = relationship("MealItem", back_populates="food")


class FoodServing(Base):
    __tablename__ = "food_servings"

    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("foods.id", ondelete="CASCADE"), nullable=False)
    serving_name = Column(String(100), nullable=False)  # "cup", "katori", "piece", "tablespoon", "100g"
    serving_multiplier = Column(Float, nullable=False, default=1.0)
    gram_weight = Column(Float, nullable=True)

    # Relationships
    food = relationship("Food", back_populates="servings")
