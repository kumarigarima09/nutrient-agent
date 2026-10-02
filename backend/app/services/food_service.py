"""
Food Service
Manages food database lookups, seed initialization, nutrition calculations per serving,
and custom food additions.
"""

import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.food import Food, FoodServing
from app.data.initial_foods import INITIAL_FOODS


class FoodService:

    @classmethod
    def seed_initial_foods(cls, db: Session) -> int:
        """
        Seeds initial foods if database table is empty.
        """
        existing_count = db.query(Food).count()
        if existing_count > 0:
            return existing_count

        created_count = 0
        for item in INITIAL_FOODS:
            servings_data = item.pop("servings", [])
            micronutrients_json = json.dumps(item.get("micronutrients", {}))
            
            food = Food(
                name=item["name"],
                category=item.get("category", "General"),
                serving_size=item["serving_size"],
                serving_unit=item.get("serving_unit", "serving"),
                serving_weight_g=item.get("serving_weight_g", 100.0),
                calories=item["calories"],
                protein_g=item["protein_g"],
                carbs_g=item["carbs_g"],
                fat_g=item["fat_g"],
                fiber_g=item.get("fiber_g", 0.0),
                micronutrients=micronutrients_json,
                diet_tags=item.get("diet_tags", ""),
                is_custom=False,
            )
            db.add(food)
            db.flush()

            for s in servings_data:
                serving = FoodServing(
                    food_id=food.id,
                    serving_name=s["serving_name"],
                    serving_multiplier=s["serving_multiplier"],
                    gram_weight=s.get("gram_weight"),
                )
                db.add(serving)

            created_count += 1

        db.commit()
        return created_count

    @classmethod
    def search_foods(
        cls,
        db: Session,
        query: str = "",
        category: Optional[str] = None,
        diet_type: Optional[str] = None,
        limit: int = 50,
        user_id: Optional[int] = None
    ) -> List[Food]:
        """
        Searches foods with optional keyword, category, and diet filters.
        """
        q = db.query(Food)

        if query:
            search_term = f"%{query.strip()}%"
            q = q.filter(
                or_(
                    Food.name.ilike(search_term),
                    Food.category.ilike(search_term)
                )
            )

        if category:
            q = q.filter(Food.category.ilike(f"%{category.strip()}%"))

        if diet_type:
            dt = diet_type.lower().strip()
            if dt == "vegetarian":
                q = q.filter(Food.diet_tags.contains("vegetarian"))
            elif dt == "vegan":
                q = q.filter(Food.diet_tags.contains("vegan"))
            elif dt == "eggetarian":
                q = q.filter(
                    or_(
                        Food.diet_tags.contains("vegetarian"),
                        Food.diet_tags.contains("eggetarian")
                    )
                )

        # Include standard foods or custom foods created by this user
        if user_id:
            q = q.filter(or_(Food.created_by_user_id == None, Food.created_by_user_id == user_id))  # noqa: E711
        else:
            q = q.filter(Food.created_by_user_id == None)  # noqa: E711

        return q.order_by(Food.name.asc()).limit(limit).all()

    @classmethod
    def get_food_by_id(cls, db: Session, food_id: int) -> Optional[Food]:
        return db.query(Food).filter(Food.id == food_id).first()

    @classmethod
    def find_best_match(cls, db: Session, food_name: str) -> Optional[Food]:
        """
        Finds exact or closest matching food in the database.
        """
        name_clean = food_name.lower().strip()

        # 1. Exact match
        exact = db.query(Food).filter(Food.name.ilike(name_clean)).first()
        if exact:
            return exact

        # 2. Prefix / Contains match
        contains = db.query(Food).filter(Food.name.ilike(f"%{name_clean}%")).first()
        if contains:
            return contains

        # 3. Word-by-word token match
        tokens = [t for t in name_clean.split() if len(t) > 2]
        for token in tokens:
            token_match = db.query(Food).filter(Food.name.ilike(f"%{token}%")).first()
            if token_match:
                return token_match

        return None

    @classmethod
    def calculate_serving_nutrition(
        cls,
        food: Food,
        quantity: float,
        unit: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates exact nutrition based on quantity and serving unit.
        """
        multiplier = 1.0

        if unit:
            unit_norm = unit.lower().strip()
            # Check custom servings
            for s in food.servings:
                if s.serving_name.lower() == unit_norm:
                    multiplier = s.serving_multiplier
                    break
            else:
                # Common standard units conversion
                if unit_norm in ["g", "gram", "grams"]:
                    multiplier = 1.0 / (food.serving_weight_g if food.serving_weight_g else 100.0)
                elif unit_norm in ["kg", "kilogram"]:
                    multiplier = 1000.0 / (food.serving_weight_g if food.serving_weight_g else 100.0)

        effective_qty = quantity * multiplier

        return {
            "food_id": food.id,
            "food_name": food.name,
            "quantity": quantity,
            "unit": unit or food.serving_unit,
            "effective_serving_count": round(effective_qty, 2),
            "calories": round(food.calories * effective_qty, 1),
            "protein_g": round(food.protein_g * effective_qty, 1),
            "carbs_g": round(food.carbs_g * effective_qty, 1),
            "fat_g": round(food.fat_g * effective_qty, 1),
            "fiber_g": round(food.fiber_g * effective_qty, 1),
            "is_estimate": False,
        }

    @classmethod
    def create_custom_food(cls, db: Session, user_id: int, data: Dict[str, Any]) -> Food:
        food = Food(
            name=data["name"],
            category=data.get("category", "Custom"),
            serving_size=data["serving_size"],
            serving_unit=data.get("serving_unit", "serving"),
            serving_weight_g=data.get("serving_weight_g", 100.0),
            calories=data["calories"],
            protein_g=data["protein_g"],
            carbs_g=data["carbs_g"],
            fat_g=data["fat_g"],
            fiber_g=data.get("fiber_g", 0.0),
            micronutrients=json.dumps(data.get("micronutrients", {})),
            diet_tags=data.get("diet_tags", ""),
            is_custom=True,
            created_by_user_id=user_id,
        )
        db.add(food)
        db.commit()
        db.refresh(food)
        return food
