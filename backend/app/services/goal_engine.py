"""
Goal Engine
Evaluates weight goals, validates safe caloric deficit/surplus boundaries,
computes realistic weight-loss/gain trajectories, and prevents dangerous extremes.
"""

from typing import Dict, Any


class GoalEngine:
    CALORIES_PER_KG_FAT = 7700.0  # Approx 7700 kcal energy equivalent per 1 kg adipose tissue
    MAX_SAFE_WEEKLY_LOSS_KG = 1.0  # Max ~1kg (2.2 lbs) per week for non-obese individuals
    RECOMMENDED_WEEKLY_LOSS_KG = 0.5  # Sweet spot for sustainable fat loss
    RECOMMENDED_WEEKLY_GAIN_KG = 0.3  # Lean bulk rate to minimize fat gain

    @classmethod
    def analyze_goal_feasibility(
        cls,
        current_weight_kg: float,
        target_weight_kg: float,
        goal: str,
        tdee: float,
    ) -> Dict[str, Any]:
        """
        Calculates projected timeline, safe weekly rate, and caloric balance recommendations.
        """
        weight_diff = target_weight_kg - current_weight_kg
        goal_norm = goal.lower().strip().replace(" ", "_")

        if goal_norm in ["weight_loss", "fat_loss"]:
            if weight_diff >= 0:
                return {
                    "is_valid": False,
                    "message": "For weight loss, target weight should be less than current weight.",
                    "estimated_weeks": 0,
                    "suggested_deficit_kcal": 400,
                }
            abs_loss_kg = abs(weight_diff)
            # Recommend 0.5 kg/week
            weekly_rate_kg = min(cls.RECOMMENDED_WEEKLY_LOSS_KG, max(0.25, abs_loss_kg / 12))
            daily_deficit = (weekly_rate_kg * cls.CALORIES_PER_KG_FAT) / 7.0
            estimated_weeks = round(abs_loss_kg / weekly_rate_kg, 1)

            return {
                "is_valid": True,
                "goal_type": "weight_loss",
                "weight_to_change_kg": round(abs_loss_kg, 1),
                "recommended_weekly_rate_kg": round(weekly_rate_kg, 2),
                "estimated_weeks": estimated_weeks,
                "suggested_daily_deficit_kcal": round(daily_deficit, 0),
                "projected_daily_target_kcal": round(max(1200.0, tdee - daily_deficit), 0),
                "guidance": f"At a safe, sustainable pace of ~{round(weekly_rate_kg, 2)} kg/week, you can reach {target_weight_kg} kg in approximately {int(estimated_weeks)} weeks without muscle breakdown or metabolic slowdown."
            }

        elif goal_norm in ["weight_gain", "muscle_gain"]:
            if weight_diff <= 0:
                return {
                    "is_valid": False,
                    "message": "For weight or muscle gain, target weight should be greater than current weight.",
                    "estimated_weeks": 0,
                    "suggested_surplus_kcal": 300,
                }
            gain_kg = weight_diff
            weekly_rate_kg = cls.RECOMMENDED_WEEKLY_GAIN_KG
            daily_surplus = (weekly_rate_kg * cls.CALORIES_PER_KG_FAT * 0.7) / 7.0  # ~300-350 kcal
            estimated_weeks = round(gain_kg / weekly_rate_kg, 1)

            return {
                "is_valid": True,
                "goal_type": "weight_gain",
                "weight_to_change_kg": round(gain_kg, 1),
                "recommended_weekly_rate_kg": round(weekly_rate_kg, 2),
                "estimated_weeks": estimated_weeks,
                "suggested_daily_surplus_kcal": round(daily_surplus, 0),
                "projected_daily_target_kcal": round(tdee + daily_surplus, 0),
                "guidance": f"Aiming for ~{round(weekly_rate_kg, 2)} kg/week allows quality lean mass gains while keeping unwanted fat gain minimal. Estimated timeline: {int(estimated_weeks)} weeks."
            }

        else:
            return {
                "is_valid": True,
                "goal_type": "maintenance",
                "weight_to_change_kg": 0.0,
                "recommended_weekly_rate_kg": 0.0,
                "estimated_weeks": 0,
                "suggested_daily_deficit_kcal": 0,
                "projected_daily_target_kcal": round(tdee, 0),
                "guidance": "Focus on nutrient density, adequate protein, hydration, and maintaining your current active lifestyle."
            }
