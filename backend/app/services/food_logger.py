"""
Natural Language Food Logger
Extracts food items, numerical quantities, and serving units from free-form text.
Cross-references database, aggregates nutritional totals, handles ambiguity,
and updates daily meal records.
"""

import re
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.meal import Meal, MealItem
from app.models.tracking import NutritionLog
from app.services.food_service import FoodService


# Number word mapping
NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "a": 1, "an": 1, "half": 0.5,
    "one and a half": 1.5, "quarter": 0.25, "couple": 2, "few": 3,
}

UNITS_LIST = [
    "glass", "glasses", "cup", "cups", "bowl", "bowls", "katori", "katoris",
    "piece", "pieces", "slice", "slices", "plate", "plates", "handful", "handfuls",
    "tablespoon", "tablespoons", "tbsp", "teaspoon", "teaspoons", "tsp",
    "gram", "grams", "g", "kg", "kilogram", "ml", "liter", "liters", "oz"
]

MEAL_TYPE_KEYWORDS = {
    "breakfast": ["breakfast", "morning", "brunch"],
    "lunch": ["lunch", "afternoon", "noon"],
    "dinner": ["dinner", "supper", "night"],
    "evening_snack": ["evening", "tea time", "chai"],
    "snack": ["snack", "snacking", "munch"],
}


class FoodLogger:

    @classmethod
    def infer_meal_type_from_time(cls) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 11:
            return "breakfast"
        elif 11 <= hour < 16:
            return "lunch"
        elif 16 <= hour < 19:
            return "evening_snack"
        elif 19 <= hour < 23:
            return "dinner"
        else:
            return "bedtime_snack"

    @classmethod
    def parse_natural_language_text(cls, text: str) -> Dict[str, Any]:
        """
        Parses food items, counts, and units deterministically from natural language.
        Supports sentences like: 'I ate two eggs, three rotis and one glass of milk for breakfast'
        """
        lower_text = text.lower().strip()

        # 1. Detect meal type if mentioned
        detected_meal_type = None
        for m_type, triggers in MEAL_TYPE_KEYWORDS.items():
            if any(t in lower_text for t in triggers):
                detected_meal_type = m_type
                break
        if not detected_meal_type:
            detected_meal_type = cls.infer_meal_type_from_time()

        # 2. Clean conversational filler prefixes
        cleaned = re.sub(
            r'^(i had|i ate|for lunch i ate|for breakfast i had|for dinner i ate|logged|log|having|ate|had|eating)\s+',
            '',
            lower_text
        )
        cleaned = re.sub(r'\s+for\s+(breakfast|lunch|dinner|snack|supper)', '', cleaned)

        # 3. Split clauses by commas, "and", "plus", "&"
        segments = re.split(r'[,;]|\band\b|\bwith\b|\bplus\b|&', cleaned)

        extracted_items = []

        for seg in segments:
            seg = seg.strip()
            if not seg:
                continue

            quantity = 1.0
            unit = None
            is_ambiguous = False
            food_phrase = seg

            # Check for words like "some", "a little", "few"
            if re.search(r'\b(some|a bit of|a lot of|portion of)\b', seg):
                is_ambiguous = True
                seg = re.sub(r'\b(some|a bit of|a lot of|portion of)\b', '', seg).strip()

            # Find numbers (digits or spelled out words)
            # Try spelled numbers first
            matched_num = False
            for word, val in NUMBER_WORDS.items():
                pattern = rf'^{word}\b'
                if re.match(pattern, seg):
                    quantity = float(val)
                    seg = re.sub(pattern, '', seg).strip()
                    matched_num = True
                    break

            if not matched_num:
                # Try digit numbers (e.g. 2, 2.5, 1/2)
                digit_match = re.match(r'^(\d+(?:\.\d+)?|\d+/\d+)\s*', seg)
                if digit_match:
                    num_str = digit_match.group(1)
                    if "/" in num_str:
                        num, den = num_str.split("/")
                        quantity = float(num) / float(den)
                    else:
                        quantity = float(num_str)
                    seg = seg[digit_match.end():].strip()

            # Check unit
            for u in UNITS_LIST:
                unit_pattern = rf'^{u}\s+(?:of\s+)?'
                if re.match(unit_pattern, seg):
                    unit = u
                    seg = re.sub(unit_pattern, '', seg).strip()
                    break

            food_name = seg.strip()
            if food_name:
                extracted_items.append({
                    "raw_food_text": food_name,
                    "quantity": quantity,
                    "unit": unit,
                    "is_ambiguous": is_ambiguous
                })

        return {
            "meal_type": detected_meal_type,
            "raw_text": text,
            "items": extracted_items
        }

    @classmethod
    def log_meal_from_text(
        cls,
        db: Session,
        user_id: int,
        text: str,
        date_str: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parses natural language, resolves database foods, computes totals,
        and saves Meal and MealItem records.
        """
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        parsed = cls.parse_natural_language_text(text)
        meal_type = parsed["meal_type"]
        items_data = parsed["items"]

        if not items_data:
            return {
                "success": False,
                "message": "Could not identify any food items. Please specify foods, e.g., '2 rotis and 1 bowl dal'.",
                "meal": None
            }

        meal = Meal(
            user_id=user_id,
            date=date_str,
            meal_type=meal_type,
            total_calories=0.0,
            total_protein_g=0.0,
            total_carbs_g=0.0,
            total_fat_g=0.0,
            total_fiber_g=0.0,
        )
        db.add(meal)
        db.flush()

        resolved_items = []
        ambiguities = []

        total_cals = 0.0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0
        total_fiber = 0.0

        for item in items_data:
            raw_name = item["raw_food_text"]
            qty = item["quantity"]
            unit = item["unit"]
            is_ambig = item["is_ambiguous"]

            db_food = FoodService.find_best_match(db, raw_name)

            if db_food:
                nutr = FoodService.calculate_serving_nutrition(db_food, qty, unit)
                meal_item = MealItem(
                    meal_id=meal.id,
                    food_id=db_food.id,
                    food_name=db_food.name,
                    quantity=qty,
                    unit=unit or db_food.serving_unit,
                    calories=nutr["calories"],
                    protein_g=nutr["protein_g"],
                    carbs_g=nutr["carbs_g"],
                    fat_g=nutr["fat_g"],
                    fiber_g=nutr["fiber_g"],
                    is_estimate=is_ambig,
                    notes=f"Matched from '{raw_name}'"
                )
                db.add(meal_item)

                total_cals += nutr["calories"]
                total_protein += nutr["protein_g"]
                total_carbs += nutr["carbs_g"]
                total_fat += nutr["fat_g"]
                total_fiber += nutr["fiber_g"]

                resolved_items.append({
                    "food_name": db_food.name,
                    "matched": True,
                    "quantity": qty,
                    "unit": unit or db_food.serving_unit,
                    "calories": nutr["calories"],
                    "protein_g": nutr["protein_g"],
                    "carbs_g": nutr["carbs_g"],
                    "fat_g": nutr["fat_g"],
                    "fiber_g": nutr["fiber_g"],
                    "is_estimate": is_ambig
                })
            else:
                # Heuristic estimation for unmatched foods
                est_cals = 150.0 * qty
                est_protein = 5.0 * qty
                est_carbs = 20.0 * qty
                est_fat = 5.0 * qty
                est_fiber = 2.0 * qty

                meal_item = MealItem(
                    meal_id=meal.id,
                    food_id=None,
                    food_name=raw_name.capitalize(),
                    quantity=qty,
                    unit=unit or "serving",
                    calories=est_cals,
                    protein_g=est_protein,
                    carbs_g=est_carbs,
                    fat_g=est_fat,
                    fiber_g=est_fiber,
                    is_estimate=True,
                    notes=f"Estimated generic value for '{raw_name}'"
                )
                db.add(meal_item)

                total_cals += est_cals
                total_protein += est_protein
                total_carbs += est_carbs
                total_fat += est_fat
                total_fiber += est_fiber

                ambiguities.append(f"'{raw_name}' not in standard database; logged with estimated portion.")
                resolved_items.append({
                    "food_name": raw_name.capitalize(),
                    "matched": False,
                    "quantity": qty,
                    "unit": unit or "serving",
                    "calories": est_cals,
                    "protein_g": est_protein,
                    "carbs_g": est_carbs,
                    "fat_g": est_fat,
                    "fiber_g": est_fiber,
                    "is_estimate": True
                })

        meal.total_calories = round(total_cals, 1)
        meal.total_protein_g = round(total_protein, 1)
        meal.total_carbs_g = round(total_carbs, 1)
        meal.total_fat_g = round(total_fat, 1)
        meal.total_fiber_g = round(total_fiber, 1)

        db.commit()
        db.refresh(meal)

        # Update or create daily NutritionLog
        cls._sync_daily_nutrition_log(db, user_id, date_str)

        return {
            "success": True,
            "meal_id": meal.id,
            "meal_type": meal_type,
            "date": date_str,
            "items": resolved_items,
            "total_nutrition": {
                "calories": meal.total_calories,
                "protein_g": meal.total_protein_g,
                "carbs_g": meal.total_carbs_g,
                "fat_g": meal.total_fat_g,
                "fiber_g": meal.total_fiber_g,
            },
            "clarifications_needed": ambiguities if ambiguities else None
        }

    @classmethod
    def _sync_daily_nutrition_log(cls, db: Session, user_id: int, date_str: str) -> None:
        """
        Aggregates all meals logged for the date into NutritionLog.
        """
        meals = db.query(Meal).filter(Meal.user_id == user_id, Meal.date == date_str).all()
        
        day_cals = sum(m.total_calories for m in meals)
        day_protein = sum(m.total_protein_g for m in meals)
        day_carbs = sum(m.total_carbs_g for m in meals)
        day_fat = sum(m.total_fat_g for m in meals)
        day_fiber = sum(m.total_fiber_g for m in meals)

        log = db.query(NutritionLog).filter(
            NutritionLog.user_id == user_id,
            NutritionLog.date == date_str
        ).first()

        if not log:
            log = NutritionLog(
                user_id=user_id,
                date=date_str,
                total_calories=day_cals,
                total_protein_g=day_protein,
                total_carbs_g=day_carbs,
                total_fat_g=day_fat,
                total_fiber_g=day_fiber,
                total_water_ml=0.0
            )
            db.add(log)
        else:
            log.total_calories = round(day_cals, 1)
            log.total_protein_g = round(day_protein, 1)
            log.total_carbs_g = round(day_carbs, 1)
            log.total_fat_g = round(day_fat, 1)
            log.total_fiber_g = round(day_fiber, 1)

        db.commit()
