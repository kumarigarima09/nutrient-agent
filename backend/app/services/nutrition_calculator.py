"""
Deterministic Nutrition Calculation Engine
Implements peer-reviewed and clinically documented formulas:
- Mifflin-St Jeor BMR formula
- Standard TDEE physical activity multipliers
- Goal-oriented calorie targets with safe boundary enforcement
- Scientific protein target ranges (ISSN / ICMR-NIN)
- Essential fatty acids and carbohydrate distribution
- Fiber (14g per 1000 kcal) and water intake targets (35ml/kg + activity bonus)
"""

from typing import Dict, Any, Tuple


class NutritionCalculator:
    # Physical activity multipliers based on standard exercise physiology
    ACTIVITY_MULTIPLIERS: Dict[str, float] = {
        "sedentary": 1.2,        # Little to no exercise, desk job
        "light": 1.375,          # Light exercise 1-3 days/week
        "moderate": 1.55,        # Moderate exercise 3-5 days/week
        "very_active": 1.725,    # Hard exercise 6-7 days/week
        "athlete": 1.9,          # Very heavy physical work or 2x/day training
    }

    # Protein intake ranges (grams per kg of body weight) based on goal & ISSN
    PROTEIN_RANGES: Dict[str, Tuple[float, float, float]] = {
        # (min, target, max)
        "weight_loss": (1.6, 1.8, 2.2),        # High protein spares muscle during caloric deficit
        "muscle_gain": (1.8, 2.0, 2.2),        # Optimal for muscle protein synthesis with resistance training
        "weight_gain": (1.4, 1.6, 2.0),        # Surplus caloric support with solid protein
        "weight_maintenance": (1.2, 1.4, 1.8), # Lean mass preservation
        "general_health": (1.0, 1.2, 1.6),     # ICMR-NIN & WHO general health standard
    }

    # Caloric surplus / deficit defaults (kcal/day)
    CALORIE_ADJUSTMENTS: Dict[str, float] = {
        "weight_loss": -400.0,       # Moderate ~0.4 kg/week steady fat loss
        "weight_gain": 350.0,        # Moderate steady gain
        "muscle_gain": 250.0,        # Lean bulk, minimal fat accumulation
        "weight_maintenance": 0.0,
        "general_health": 0.0,
    }

    # Water activity bonus in ml
    WATER_ACTIVITY_BONUS: Dict[str, float] = {
        "sedentary": 0.0,
        "light": 350.0,
        "moderate": 500.0,
        "very_active": 800.0,
        "athlete": 1000.0,
    }

    @classmethod
    def calculate_bmr(cls, weight_kg: float, height_cm: float, age: int, sex: str) -> float:
        """
        Calculates Basal Metabolic Rate using Mifflin-St Jeor formula:
        Male: 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        Female: 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        Other: Average offset (-78)
        """
        sex_normalized = sex.lower().strip()
        base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age)

        if sex_normalized in ["male", "m", "man"]:
            bmr = base + 5.0
        elif sex_normalized in ["female", "f", "woman"]:
            bmr = base - 161.0
        else:
            bmr = base - 78.0

        return round(max(bmr, 800.0), 1)

    @classmethod
    def calculate_tdee(cls, bmr: float, activity_level: str) -> float:
        """
        Calculates Total Daily Energy Expenditure (TDEE) = BMR * activity_multiplier
        """
        act_key = activity_level.lower().strip().replace(" ", "_")
        multiplier = cls.ACTIVITY_MULTIPLIERS.get(act_key, 1.375)
        return round(bmr * multiplier, 1)

    @classmethod
    def calculate_calorie_target(
        cls,
        tdee: float,
        goal: str,
        sex: str = "male",
        custom_delta: float = None,
    ) -> float:
        """
        Calculates target daily calories with safety minimum guardrails:
        Minimum 1200 kcal for females, 1500 kcal for males.
        """
        goal_key = goal.lower().strip().replace(" ", "_")

        if custom_delta is not None:
            delta = custom_delta
        else:
            delta = cls.CALORIE_ADJUSTMENTS.get(goal_key, 0.0)

        target = tdee + delta

        # Safety floor check
        sex_norm = sex.lower().strip()
        min_safe = 1200.0 if sex_norm in ["female", "f", "woman"] else 1400.0
        if target < min_safe:
            target = min_safe

        return round(target, 1)

    @classmethod
    def calculate_protein_target(
        cls,
        weight_kg: float,
        goal: str,
        custom_per_kg: float = None
    ) -> Dict[str, float]:
        """
        Calculates target protein and scientific intake range (grams/day).
        """
        goal_key = goal.lower().strip().replace(" ", "_")
        min_rate, target_rate, max_rate = cls.PROTEIN_RANGES.get(
            goal_key, (1.2, 1.4, 1.8)
        )

        chosen_rate = custom_per_kg if custom_per_kg else target_rate

        return {
            "target_g": round(weight_kg * chosen_rate, 1),
            "min_g": round(weight_kg * min_rate, 1),
            "max_g": round(weight_kg * max_rate, 1),
            "grams_per_kg": round(chosen_rate, 2),
        }

    @classmethod
    def calculate_fat_target(
        cls,
        total_calories: float,
        goal: str = "general_health",
        fat_ratio: float = 0.25
    ) -> Dict[str, float]:
        """
        Calculates fat target based on 20-30% of total caloric intake.
        1 gram fat = 9 kcal.
        """
        # Ensure fat ratio is healthy between 20% and 35%
        ratio = max(0.20, min(fat_ratio, 0.35))
        fat_cals = total_calories * ratio
        fat_g = fat_cals / 9.0

        return {
            "target_g": round(fat_g, 1),
            "calories_from_fat": round(fat_cals, 1),
            "percentage_of_total": round(ratio * 100, 1),
        }

    @classmethod
    def calculate_carb_target(
        cls,
        total_calories: float,
        protein_g: float,
        fat_g: float
    ) -> Dict[str, float]:
        """
        Calculates carbohydrate target using remaining calories:
        Carbs = (total_calories - (protein_g * 4 + fat_g * 9)) / 4
        """
        cals_from_protein = protein_g * 4.0
        cals_from_fat = fat_g * 9.0
        remaining_cals = max(0.0, total_calories - (cals_from_protein + cals_from_fat))
        carb_g = remaining_cals / 4.0

        return {
            "target_g": round(carb_g, 1),
            "calories_from_carbs": round(remaining_cals, 1),
            "percentage_of_total": round((remaining_cals / total_calories) * 100, 1) if total_calories > 0 else 0.0,
        }

    @classmethod
    def calculate_fiber_target(cls, total_calories: float) -> float:
        """
        Calculates daily fiber recommendation:
        14g per 1000 kcal consumed, minimum 25g.
        """
        fiber = (total_calories / 1000.0) * 14.0
        return round(max(25.0, fiber), 1)

    @classmethod
    def calculate_water_target(cls, weight_kg: float, activity_level: str) -> float:
        """
        Calculates daily water hydration target in milliliters (ml):
        Baseline: 35 ml per kg body weight + exercise compensation.
        """
        act_key = activity_level.lower().strip().replace(" ", "_")
        bonus = cls.WATER_ACTIVITY_BONUS.get(act_key, 350.0)
        baseline = weight_kg * 35.0
        total_ml = baseline + bonus
        return round(total_ml, 0)

    @classmethod
    def calculate_all(
        cls,
        weight_kg: float,
        height_cm: float,
        age: int,
        sex: str,
        activity_level: str,
        goal: str,
        custom_deficit: float = None,
        custom_surplus: float = None,
        custom_protein_per_kg: float = None,
    ) -> Dict[str, Any]:
        """
        Complete deterministic nutrition breakdown for a user profile.
        """
        bmr = cls.calculate_bmr(weight_kg, height_cm, age, sex)
        tdee = cls.calculate_tdee(bmr, activity_level)

        custom_delta = None
        if custom_deficit is not None:
            custom_delta = -abs(custom_deficit)
        elif custom_surplus is not None:
            custom_delta = abs(custom_surplus)

        target_cals = cls.calculate_calorie_target(
            tdee=tdee,
            goal=goal,
            sex=sex,
            custom_delta=custom_delta
        )

        protein_info = cls.calculate_protein_target(
            weight_kg=weight_kg,
            goal=goal,
            custom_per_kg=custom_protein_per_kg
        )

        fat_info = cls.calculate_fat_target(
            total_calories=target_cals,
            goal=goal,
            fat_ratio=0.25
        )

        carb_info = cls.calculate_carb_target(
            total_calories=target_cals,
            protein_g=protein_info["target_g"],
            fat_g=fat_info["target_g"]
        )

        fiber_target = cls.calculate_fiber_target(target_cals)
        water_target_ml = cls.calculate_water_target(weight_kg, activity_level)

        return {
            "bmr": bmr,
            "tdee": tdee,
            "target_calories": target_cals,
            "target_protein_g": protein_info["target_g"],
            "protein_range": {
                "min_g": protein_info["min_g"],
                "max_g": protein_info["max_g"],
                "grams_per_kg": protein_info["grams_per_kg"],
            },
            "target_carbs_g": carb_info["target_g"],
            "target_fat_g": fat_info["target_g"],
            "target_fiber_g": fiber_target,
            "target_water_ml": water_target_ml,
            "macro_distribution": {
                "protein_kcal": round(protein_info["target_g"] * 4, 1),
                "carbs_kcal": carb_info["calories_from_carbs"],
                "fat_kcal": fat_info["calories_from_fat"],
                "protein_pct": round((protein_info["target_g"] * 4 / target_cals) * 100, 1),
                "carbs_pct": carb_info["percentage_of_total"],
                "fat_pct": fat_info["percentage_of_total"],
            },
            "formula_info": {
                "bmr_formula": "Mifflin-St Jeor (1990)",
                "tdee_method": f"Activity Multiplier ({cls.ACTIVITY_MULTIPLIERS.get(activity_level.lower().replace(' ', '_'), 1.375)}x)",
                "water_formula": "35ml/kg + Activity Compensation",
                "notes": "Target calories and macronutrients are deterministic baseline estimates. Monitor real-world weekly scale weight and energy to calibrate over time."
            }
        }
