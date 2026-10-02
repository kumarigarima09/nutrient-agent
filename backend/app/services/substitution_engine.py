"""
Food Substitution Engine
Finds macro-compatible and culturally appropriate substitutions.
Scales portion sizes to match original caloric and protein density.
Strictly respects dietary restrictions (veg, vegan, allergies).
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.food import Food
from app.services.food_service import FoodService


class SubstitutionEngine:

    # Direct functional category substitutes
    CATEGORY_ALTERNATIVES = {
        "paneer": ["Tofu (Firm)", "Soy Chunks (Nutrela / Textured Soya)", "Chicken Breast (Cooked / Grilled)", "Egg (Whole Boiled)"],
        "chicken": ["Paneer", "Tofu (Firm)", "Soy Chunks (Nutrela / Textured Soya)", "Fish (Rohu / Katla / Tilapia Curry)", "Egg (Whole Boiled)"],
        "egg": ["Paneer", "Tofu (Firm)", "Soy Chunks (Nutrela / Textured Soya)", "Curd (Plain Dahi / Yogurt)"],
        "milk": ["Soy Chunks (Nutrela / Textured Soya)", "Curd (Plain Dahi / Yogurt)", "Tofu (Firm)"],
        "banana": ["Apple", "Orange", "Mango", "Sweet Potato (Boiled / Baked)"],
        "rice": ["Roti", "Brown Rice (Cooked)", "Oats (Cooked with Water)", "Sweet Potato (Boiled / Baked)"],
        "roti": ["White Rice (Cooked)", "Brown Rice (Cooked)", "Whole Wheat Bread", "Oats (Cooked with Water)"],
        "dal": ["Rajma (Kidney Beans Curry)", "Chole (Chickpeas Curry)", "Soy Chunks (Nutrela / Textured Soya)"],
        "rajma": ["Chole (Chickpeas Curry)", "Dal (Yellow Toor/Moong Cooked)", "Soy Chunks (Nutrela / Textured Soya)"],
        "almonds": ["Walnuts", "Peanuts (Roasted)", "Cashews"],
        "peanuts": ["Almonds", "Walnuts", "Cashews"],
    }

    @classmethod
    def suggest_substitution(
        cls,
        db: Session,
        food_name: str,
        target_calories: Optional[float] = None,
        target_protein: Optional[float] = None,
        diet_type: str = "vegetarian",
        allergies: Optional[str] = "",
        user_preferences: Optional[str] = ""
    ) -> Dict[str, Any]:
        """
        Suggests nutritionally balanced food substitutes.
        """
        food_name_clean = food_name.lower().strip()
        allergy_tokens = [a.strip().lower() for a in (allergies or "").split(",") if a.strip()]

        # 1. Look up original food if in DB
        original_food = FoodService.find_best_match(db, food_name_clean)
        if original_food and target_calories is None:
            target_calories = original_food.calories
            target_protein = original_food.protein_g

        target_cals = target_calories or 200.0
        target_prot = target_protein or 10.0

        # 2. Check candidate suggestions
        candidates_to_try = []
        for key, alts in cls.CATEGORY_ALTERNATIVES.items():
            if key in food_name_clean:
                candidates_to_try.extend(alts)

        # Also pull foods from similar category
        if original_food and original_food.category:
            cat_foods = db.query(Food).filter(
                Food.category == original_food.category,
                Food.id != original_food.id
            ).limit(6).all()
            for cf in cat_foods:
                if cf.name not in candidates_to_try:
                    candidates_to_try.append(cf.name)

        if not candidates_to_try:
            # Fallback popular foods
            candidates_to_try = ["Tofu (Firm)", "Paneer", "Dal (Yellow Toor/Moong Cooked)", "Egg (Whole Boiled)", "Apple"]

        options = []
        diet_norm = diet_type.lower().strip()

        for cand_name in candidates_to_try:
            cand_food = FoodService.find_best_match(db, cand_name)
            if not cand_food:
                continue

            # Check diet restriction
            tags = (cand_food.diet_tags or "").lower()
            if diet_norm == "vegan" and "vegan" not in tags:
                continue
            if diet_norm == "vegetarian" and "vegetarian" not in tags:
                continue
            if diet_norm == "eggetarian" and not ("vegetarian" in tags or "eggetarian" in tags):
                continue

            # Check allergy restriction
            is_allergic = False
            for alg in allergy_tokens:
                if alg in cand_food.name.lower():
                    is_allergic = True
                    break
            if is_allergic:
                continue

            # Calculate scaled portion to match calories or protein
            # Priority: match calories while staying reasonably close on protein
            if cand_food.calories > 0:
                scale_ratio = target_cals / cand_food.calories
            else:
                scale_ratio = 1.0

            scaled_qty = round(scale_ratio, 2)
            cal_diff = round((cand_food.calories * scale_ratio) - target_cals, 1)
            prot_diff = round((cand_food.protein_g * scale_ratio) - target_prot, 1)

            options.append({
                "substitute_food": cand_food.name,
                "suggested_quantity": scaled_qty,
                "serving_unit": cand_food.serving_unit,
                "serving_description": f"{scaled_qty} x {cand_food.serving_size}",
                "nutrition": {
                    "calories": round(cand_food.calories * scale_ratio, 1),
                    "protein_g": round(cand_food.protein_g * scale_ratio, 1),
                    "carbs_g": round(cand_food.carbs_g * scale_ratio, 1),
                    "fat_g": round(cand_food.fat_g * scale_ratio, 1),
                    "fiber_g": round(cand_food.fiber_g * scale_ratio, 1),
                },
                "calorie_difference": cal_diff,
                "protein_difference": prot_diff,
                "fit_note": f"Matches {round(cand_food.calories * scale_ratio)} kcal with {round(cand_food.protein_g * scale_ratio)}g protein."
            })

            if len(options) >= 3:
                break

        return {
            "original_food": food_name,
            "target_calories": target_cals,
            "target_protein_g": target_prot,
            "diet_type": diet_type,
            "substitutes": options,
            "guidance": f"Found {len(options)} suitable substitutes aligned with your {diet_type} diet."
        }
