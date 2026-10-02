"""
Progress Analyzer & Trend Engine
Computes 7-day and 30-day rolling averages, adherence metrics,
and generates clinically grounded, non-reactive weekly target adjustments.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.profile import Profile
from app.models.tracking import WeightLog, NutritionLog, WaterLog, ExerciseLog, Recommendation
from app.models.meal import Meal


class ProgressAnalyzer:

    @classmethod
    def log_weight(
        cls,
        db: Session,
        user_id: int,
        weight_kg: float,
        date_str: Optional[str] = None,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Logs a weight entry and computes 7-day rolling average.
        """
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        existing = db.query(WeightLog).filter(
            WeightLog.user_id == user_id,
            WeightLog.date == date_str
        ).first()

        if existing:
            existing.weight_kg = weight_kg
            existing.note = note
            entry = existing
        else:
            entry = WeightLog(
                user_id=user_id,
                date=date_str,
                weight_kg=weight_kg,
                note=note
            )
            db.add(entry)

        db.flush()

        # Compute 7-day rolling average
        # Get past 7 records up to this date
        past_logs = db.query(WeightLog).filter(
            WeightLog.user_id == user_id,
            WeightLog.date <= date_str
        ).order_by(desc(WeightLog.date)).limit(7).all()

        if past_logs:
            avg_7d = sum(w.weight_kg for w in past_logs) / len(past_logs)
            entry.rolling_avg_7d = round(avg_7d, 2)

        # Also update current_weight_kg in Profile
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if profile:
            profile.current_weight_kg = weight_kg

        db.commit()
        db.refresh(entry)

        return {
            "id": entry.id,
            "date": entry.date,
            "weight_kg": entry.weight_kg,
            "rolling_avg_7d": entry.rolling_avg_7d,
            "note": entry.note
        }

    @classmethod
    def get_weight_history(
        cls,
        db: Session,
        user_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Fetches chronological weight log with 7-day rolling averages.
        """
        logs = db.query(WeightLog).filter(
            WeightLog.user_id == user_id
        ).order_by(WeightLog.date.asc()).all()

        # If more than days requested, slice the most recent
        recent = logs[-days:] if len(logs) > days else logs

        result = []
        for l in recent:
            result.append({
                "date": l.date,
                "weight_kg": l.weight_kg,
                "rolling_avg_7d": l.rolling_avg_7d or l.weight_kg,
                "note": l.note
            })
        return result

    @classmethod
    def analyze_weekly_progress(
        cls,
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Deep clinical & behavioral analysis of the past 7-14 days.
        Determines adherence, trends, and suggests safe target calibration.
        """
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            return {"error": "Profile not found."}

        target_cals = profile.target_calories or 2000.0
        target_prot = profile.target_protein_g or 80.0
        target_water = profile.target_water_ml or 2500.0
        goal = (profile.goal or "general_health").lower()

        # Fetch last 14 days of nutrition logs
        nutr_logs = db.query(NutritionLog).filter(
            NutritionLog.user_id == user_id
        ).order_by(desc(NutritionLog.date)).limit(14).all()

        # Fetch weight logs
        weight_logs = db.query(WeightLog).filter(
            WeightLog.user_id == user_id
        ).order_by(desc(WeightLog.date)).limit(14).all()

        days_logged = len(nutr_logs)
        avg_calories = (
            sum(nl.total_calories for nl in nutr_logs) / days_logged
            if days_logged > 0 else 0.0
        )
        avg_protein = (
            sum(nl.total_protein_g for nl in nutr_logs) / days_logged
            if days_logged > 0 else 0.0
        )

        # Adherence calculation: % of days where calories were within 15% of target
        adherent_days = sum(
            1 for nl in nutr_logs
            if abs(nl.total_calories - target_cals) <= (0.15 * target_cals)
        )
        calorie_adherence_pct = round((adherent_days / days_logged * 100), 1) if days_logged > 0 else 0.0
        protein_adherence_pct = round((avg_protein / target_prot * 100), 1) if target_prot > 0 else 0.0

        # Weight change analysis
        weight_trend = "insufficient_data"
        weight_delta_kg = 0.0
        rate_of_change_weekly = 0.0

        if len(weight_logs) >= 2:
            latest_wt = weight_logs[0].rolling_avg_7d or weight_logs[0].weight_kg
            oldest_wt = weight_logs[-1].rolling_avg_7d or weight_logs[-1].weight_kg
            weight_delta_kg = round(latest_wt - oldest_wt, 2)
            days_span = max(1, len(weight_logs))
            rate_of_change_weekly = round((weight_delta_kg / days_span) * 7.0, 2)

            if weight_delta_kg < -0.3:
                weight_trend = "losing"
            elif weight_delta_kg > 0.3:
                weight_trend = "gaining"
            else:
                weight_trend = "stable"

        # Adaptive Recommendation Logic (Deterministic rules, never reactive to 1 day)
        calorie_delta = 0.0
        protein_delta = 0.0
        recommendation_type = "maintain"
        ai_recommendation_text = ""

        if days_logged < 4:
            recommendation_type = "gather_more_data"
            ai_recommendation_text = (
                "You have fewer than 4 logged days this week. Maintain current targets and focus on consistently logging your meals before adjusting targets."
            )
        elif calorie_adherence_pct < 60.0:
            recommendation_type = "improve_consistency"
            ai_recommendation_text = (
                f"Your calorie consistency is currently at {calorie_adherence_pct}%. Do not cut calories further right now. Instead, focus on meal prep simplicity, batch cooking, and closing the gap to your baseline target of {int(target_cals)} kcal."
            )
        else:
            # High adherence (>=60%), evaluate physiological response
            if goal in ["weight_loss", "fat_loss"]:
                if weight_trend == "stable" and days_logged >= 7:
                    # True metabolic adaptation / plateau
                    calorie_delta = -100.0
                    recommendation_type = "slight_deficit_increase"
                    ai_recommendation_text = (
                        f"Great consistency ({calorie_adherence_pct}% adherence)! Weight has stabilized over the last period. We suggest a gentle calibration of -100 kcal (new target: {int(target_cals - 100)} kcal) to resume steady, sustainable fat loss."
                    )
                elif weight_trend == "losing":
                    if rate_of_change_weekly < -1.0:
                        calorie_delta = +150.0
                        recommendation_type = "slow_down_rate"
                        ai_recommendation_text = (
                            f"Weight is dropping rapidly (~{abs(rate_of_change_weekly)} kg/week). To protect lean muscle tissue and energy levels, we suggest increasing daily calories by +150 kcal (new target: {int(target_cals + 150)} kcal)."
                        )
                    else:
                        recommendation_type = "maintain"
                        ai_recommendation_text = (
                            f"Outstanding progress! Weight is trending down at an optimal pace (~{abs(rate_of_change_weekly)} kg/week). Keep following your current {int(target_cals)} kcal target."
                        )
                else:
                    recommendation_type = "monitor"
                    ai_recommendation_text = "Adherence is solid. Continue this week with current targets to verify scale trends against water weight fluctuations."

            elif goal in ["muscle_gain", "weight_gain"]:
                if weight_trend == "stable" and days_logged >= 7:
                    calorie_delta = +150.0
                    recommendation_type = "slight_surplus_increase"
                    ai_recommendation_text = (
                        f"Consistent adherence observed with stable weight. To promote steady lean tissue accretion, we suggest nudging daily calories by +150 kcal (new target: {int(target_cals + 150)} kcal)."
                    )
                else:
                    recommendation_type = "maintain"
                    ai_recommendation_text = f"You are on track for steady, quality lean gains. Maintain your target of {int(target_cals)} kcal."

            else:
                recommendation_type = "maintain"
                ai_recommendation_text = f"Nutrient intake and weight are nicely balanced. Maintain your daily target of {int(target_cals)} kcal."

        # Record recommendation
        rec = Recommendation(
            user_id=user_id,
            week_start_date=datetime.now().strftime("%Y-%m-%d"),
            recommendation_text=ai_recommendation_text,
            calorie_delta=calorie_delta,
            protein_delta=protein_delta,
            status="active"
        )
        db.add(rec)
        db.commit()

        return {
            "user_id": user_id,
            "period": "Past 14 Days",
            "days_logged": days_logged,
            "averages": {
                "daily_calories": round(avg_calories, 1),
                "target_calories": round(target_cals, 1),
                "daily_protein_g": round(avg_protein, 1),
                "target_protein_g": round(target_prot, 1),
            },
            "adherence": {
                "calorie_adherence_pct": calorie_adherence_pct,
                "protein_adherence_pct": min(100.0, protein_adherence_pct),
                "consistency_rating": "High" if calorie_adherence_pct >= 75 else ("Moderate" if calorie_adherence_pct >= 50 else "Needs Focus")
            },
            "weight_analysis": {
                "trend": weight_trend,
                "net_change_kg": weight_delta_kg,
                "weekly_rate_kg": rate_of_change_weekly,
                "current_weight_kg": profile.current_weight_kg,
                "target_weight_kg": profile.target_weight_kg,
            },
            "recommendation": {
                "action": recommendation_type,
                "suggested_calorie_delta": calorie_delta,
                "new_calorie_target": round(target_cals + calorie_delta, 1),
                "text": ai_recommendation_text
            }
        }

    @classmethod
    def get_dashboard_summary(cls, db: Session, user_id: int, date_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Gathers complete real-time dashboard data for today.
        """
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            return {"error": "Profile not found."}

        # Daily meals
        meals = db.query(Meal).filter(
            Meal.user_id == user_id,
            Meal.date == date_str
        ).all()

        logged_cals = round(sum(m.total_calories for m in meals), 1)
        logged_prot = round(sum(m.total_protein_g for m in meals), 1)
        logged_carbs = round(sum(m.total_carbs_g for m in meals), 1)
        logged_fat = round(sum(m.total_fat_g for m in meals), 1)
        logged_fiber = round(sum(m.total_fiber_g for m in meals), 1)

        # Water logs for today
        water_records = db.query(WaterLog).filter(
            WaterLog.user_id == user_id,
            WaterLog.date == date_str
        ).all()
        logged_water_ml = round(sum(w.amount_ml for w in water_records), 0)

        # Targets
        target_cals = profile.target_calories or 2000.0
        target_prot = profile.target_protein_g or 80.0
        target_carbs = profile.target_carbs_g or 250.0
        target_fat = profile.target_fat_g or 55.0
        target_fiber = profile.target_fiber_g or 28.0
        target_water = profile.target_water_ml or 2500.0

        # Remaining
        rem_cals = round(max(0.0, target_cals - logged_cals), 1)
        rem_prot = round(max(0.0, target_prot - logged_prot), 1)

        # Latest weight
        latest_weight = db.query(WeightLog).filter(
            WeightLog.user_id == user_id
        ).order_by(desc(WeightLog.date)).first()
        current_wt = latest_weight.weight_kg if latest_weight else profile.current_weight_kg

        # Recent 7-day weight trend for sparkline
        weight_history = cls.get_weight_history(db, user_id, days=7)

        # Latest active recommendation
        latest_rec = db.query(Recommendation).filter(
            Recommendation.user_id == user_id
        ).order_by(desc(Recommendation.created_at)).first()

        meals_summary = []
        for m in meals:
            items_list = []
            for it in m.items:
                items_list.append({
                    "food_name": it.food_name,
                    "quantity": it.quantity,
                    "unit": it.unit,
                    "calories": it.calories,
                    "protein_g": it.protein_g,
                    "is_estimate": it.is_estimate
                })
            meals_summary.append({
                "id": m.id,
                "meal_type": m.meal_type,
                "total_calories": m.total_calories,
                "total_protein_g": m.total_protein_g,
                "total_carbs_g": m.total_carbs_g,
                "total_fat_g": m.total_fat_g,
                "items": items_list
            })

        return {
            "date": date_str,
            "user_name": profile.name,
            "goal": profile.goal,
            "metrics": {
                "calories": {
                    "current": logged_cals,
                    "target": target_cals,
                    "remaining": rem_cals,
                    "percentage": min(100.0, round((logged_cals / target_cals) * 100, 1)) if target_cals > 0 else 0
                },
                "protein": {
                    "current": logged_prot,
                    "target": target_prot,
                    "remaining": rem_prot,
                    "percentage": min(100.0, round((logged_prot / target_prot) * 100, 1)) if target_prot > 0 else 0
                },
                "carbs": {
                    "current": logged_carbs,
                    "target": target_carbs,
                    "remaining": max(0.0, round(target_carbs - logged_carbs, 1)),
                    "percentage": min(100.0, round((logged_carbs / target_carbs) * 100, 1)) if target_carbs > 0 else 0
                },
                "fat": {
                    "current": logged_fat,
                    "target": target_fat,
                    "remaining": max(0.0, round(target_fat - logged_fat, 1)),
                    "percentage": min(100.0, round((logged_fat / target_fat) * 100, 1)) if target_fat > 0 else 0
                },
                "fiber": {
                    "current": logged_fiber,
                    "target": target_fiber,
                    "remaining": max(0.0, round(target_fiber - logged_fiber, 1)),
                    "percentage": min(100.0, round((logged_fiber / target_fiber) * 100, 1)) if target_fiber > 0 else 0
                },
                "water": {
                    "current_ml": logged_water_ml,
                    "target_ml": target_water,
                    "remaining_ml": max(0.0, round(target_water - logged_water_ml, 0)),
                    "percentage": min(100.0, round((logged_water_ml / target_water) * 100, 1)) if target_water > 0 else 0
                }
            },
            "weight": {
                "current_kg": current_wt,
                "target_kg": profile.target_weight_kg,
                "trend_sparkline": weight_history
            },
            "today_meals": meals_summary,
            "active_recommendation": {
                "text": latest_rec.recommendation_text if latest_rec else "Keep tracking your meals to receive your weekly AI nutrition coaching recommendations!",
                "calorie_delta": latest_rec.calorie_delta if latest_rec else 0.0
            }
        }
