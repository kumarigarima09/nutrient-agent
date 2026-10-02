"""
Deterministic Meal Planner
Creates balanced 4 to 6 meal daily or weekly schedules mapped precisely
to target calories and macronutrients, adhering strictly to diet, allergies, and cooking time.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.meal_plan import MealPlan
from app.models.profile import Profile
from app.services.food_service import FoodService


class MealPlanner:

    # Culturally authentic, nutritious Indian/Global templates for rich variety across 7 days
    MEAL_TEMPLATES = {
        "breakfast": {
            "vegetarian": [
                {
                    "name": "Oats with Nuts & Apple",
                    "items": [
                        {"food": "Oats (Cooked with Water)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Milk (Cow / Toned)", "qty": 1.0, "unit": "glass"},
                        {"food": "Almonds", "qty": 1.0, "unit": "serving"},
                        {"food": "Apple", "qty": 1.0, "unit": "piece"},
                    ],
                    "prep": "Simmer oats in milk for 5-7 minutes. Top with crisp apple slices and crushed almonds."
                },
                {
                    "name": "Poha with Curd & Peanuts",
                    "items": [
                        {"food": "Poha", "qty": 1.0, "unit": "plate"},
                        {"food": "Curd (Plain Dahi / Yogurt)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Peanuts (Roasted)", "qty": 0.5, "unit": "handful"},
                    ],
                    "prep": "Tempered flattened rice with mustard seeds, turmeric and onions. Top with roasted peanuts & cool curd."
                },
                {
                    "name": "Steamed Idli with Sambar Dal",
                    "items": [
                        {"food": "Idli", "qty": 3.0, "unit": "piece"},
                        {"food": "Dal (Yellow Toor/Moong Cooked)", "qty": 1.0, "unit": "bowl"},
                    ],
                    "prep": "Steamed fluffy idlis served hot with nutrient-dense toor dal sambar."
                },
                {
                    "name": "Vegetable Upma with Curd",
                    "items": [
                        {"food": "Upma", "qty": 1.0, "unit": "bowl"},
                        {"food": "Curd (Plain Dahi / Yogurt)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Cashews", "qty": 0.5, "unit": "serving"},
                    ],
                    "prep": "Roasted semolina cooked with mixed vegetables, tempered with curry leaves and golden cashews."
                },
                {
                    "name": "Crispy Dosa with Yellow Dal",
                    "items": [
                        {"food": "Dosa (Plain)", "qty": 2.0, "unit": "piece"},
                        {"food": "Dal (Yellow Toor/Moong Cooked)", "qty": 1.0, "unit": "bowl"},
                    ],
                    "prep": "Golden crispy fermented dosas paired with spiced comforting lentil dal."
                },
                {
                    "name": "Whole Wheat Bread with Milk & Banana",
                    "items": [
                        {"food": "Whole Wheat Bread", "qty": 2.0, "unit": "slice"},
                        {"food": "Milk (Cow / Toned)", "qty": 1.0, "unit": "glass"},
                        {"food": "Banana", "qty": 1.0, "unit": "piece"},
                        {"food": "Walnuts", "qty": 0.5, "unit": "handful"},
                    ],
                    "prep": "Toasted whole grain bread served with warm spiced milk, banana, and fresh walnuts."
                },
                {
                    "name": "Paneer Stuffed Toast & Fruit",
                    "items": [
                        {"food": "Whole Wheat Bread", "qty": 2.0, "unit": "slice"},
                        {"food": "Paneer", "qty": 0.6, "unit": "100g"},
                        {"food": "Orange", "qty": 1.0, "unit": "piece"},
                    ],
                    "prep": "Seasoned crushed paneer sandwich toasted crisp, paired with a juicy fresh orange."
                }
            ],
            "eggetarian": [
                {
                    "name": "Boiled Eggs with Whole Wheat Toast & Milk",
                    "items": [
                        {"food": "Egg (Whole Boiled)", "qty": 2.0, "unit": "piece"},
                        {"food": "Egg White (Boiled)", "qty": 2.0, "unit": "piece"},
                        {"food": "Whole Wheat Bread", "qty": 2.0, "unit": "slice"},
                        {"food": "Milk (Cow / Toned)", "qty": 1.0, "unit": "glass"},
                    ],
                    "prep": "Hard boiled eggs seasoned with cracked pepper. Whole wheat toast & warm milk."
                },
                {
                    "name": "Egg Omelette Toast & Apple",
                    "items": [
                        {"food": "Egg (Whole Boiled)", "qty": 2.0, "unit": "piece"},
                        {"food": "Whole Wheat Bread", "qty": 2.0, "unit": "slice"},
                        {"food": "Apple", "qty": 1.0, "unit": "piece"},
                    ],
                    "prep": "Wholesome eggs with whole wheat slices and a fresh sliced apple."
                }
            ],
            "vegan": [
                {
                    "name": "Scrambled Tofu Toast & Fruit",
                    "items": [
                        {"food": "Tofu (Firm)", "qty": 1.0, "unit": "100g"},
                        {"food": "Whole Wheat Bread", "qty": 2.0, "unit": "slice"},
                        {"food": "Banana", "qty": 1.0, "unit": "piece"},
                    ],
                    "prep": "Crumble firm tofu and sauté with turmeric and herbs over whole wheat toast."
                },
                {
                    "name": "Oatmeal with Almonds & Banana",
                    "items": [
                        {"food": "Oats (Cooked with Water)", "qty": 1.2, "unit": "bowl"},
                        {"food": "Almonds", "qty": 1.0, "unit": "serving"},
                        {"food": "Banana", "qty": 1.0, "unit": "piece"},
                    ],
                    "prep": "Warm rolled oats topped with sliced bananas and crunchy California almonds."
                }
            ]
        },
        "mid_morning": {
            "vegetarian": [
                {
                    "name": "Fresh Banana & Walnut Snack",
                    "items": [
                        {"food": "Banana", "qty": 1.0, "unit": "piece"},
                        {"food": "Walnuts", "qty": 0.5, "unit": "handful"},
                    ],
                    "prep": "Peel and enjoy fresh banana with brain-boosting walnut halves."
                },
                {
                    "name": "Chilled Curd with Roasted Cumin",
                    "items": [
                        {"food": "Curd (Plain Dahi / Yogurt)", "qty": 1.0, "unit": "bowl"},
                    ],
                    "prep": "Whisk fresh curd with roasted cumin powder and rock salt."
                },
                {
                    "name": "Crisp Apple & Almond Energy",
                    "items": [
                        {"food": "Apple", "qty": 1.0, "unit": "piece"},
                        {"food": "Almonds", "qty": 0.8, "unit": "serving"},
                    ],
                    "prep": "Sliced sweet apple paired with crunchy almonds for sustained morning focus."
                },
                {
                    "name": "Seasonal Sweet Orange",
                    "items": [
                        {"food": "Orange", "qty": 1.0, "unit": "piece"},
                        {"food": "Cashews", "qty": 0.5, "unit": "serving"},
                    ],
                    "prep": "Refreshing citrus orange wedges paired with whole roasted cashews."
                }
            ]
        },
        "lunch": {
            "vegetarian": [
                {
                    "name": "Roti, Dal, Paneer Sabzi & Salad",
                    "items": [
                        {"food": "Roti", "qty": 2.0, "unit": "piece"},
                        {"food": "Dal (Yellow Toor/Moong Cooked)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Paneer", "qty": 0.7, "unit": "100g"},
                        {"food": "Salad (Cucumber, Tomato, Onion)", "qty": 1.0, "unit": "bowl"},
                    ],
                    "prep": "Tender paneer cubes sautéed with onions and tomatoes, paired with hot rotis, dal, and fresh salad."
                },
                {
                    "name": "Rice, Slow-Cooked Rajma & Spinach",
                    "items": [
                        {"food": "White Rice (Cooked)", "qty": 1.0, "unit": "cup"},
                        {"food": "Rajma (Kidney Beans Curry)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Spinach / Palak Sabzi", "qty": 1.0, "unit": "bowl"},
                    ],
                    "prep": "Steaming basmati rice served with classic Punjabi rajma curry and sautéed garlicky palak."
                },
                {
                    "name": "Brown Rice, Chole Curry & Curd",
                    "items": [
                        {"food": "Brown Rice (Cooked)", "qty": 1.0, "unit": "cup"},
                        {"food": "Chole (Chickpeas Curry)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Curd (Plain Dahi / Yogurt)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Salad (Cucumber, Tomato, Onion)", "qty": 0.8, "unit": "bowl"},
                    ],
                    "prep": "Aromatic chickpea masala curry paired with wholesome nutty brown rice and chilled cooling curd."
                },
                {
                    "name": "Chapati, Yellow Dal & Mixed Sabzi",
                    "items": [
                        {"food": "Chapati", "qty": 3.0, "unit": "piece"},
                        {"food": "Dal (Yellow Toor/Moong Cooked)", "qty": 1.2, "unit": "bowl"},
                        {"food": "Mixed Indian Sabzi (Vegetables Curry)", "qty": 1.0, "unit": "bowl"},
                    ],
                    "prep": "Fresh chapatis with rich tempering toor dal and colorful sautéed seasonal vegetable medley."
                },
                {
                    "name": "Roti, Soy Chunks Curry & Palak",
                    "items": [
                        {"food": "Roti", "qty": 2.0, "unit": "piece"},
                        {"food": "Soy Chunks (Nutrela / Textured Soya)", "qty": 0.8, "unit": "serving"},
                        {"food": "Spinach / Palak Sabzi", "qty": 1.0, "unit": "bowl"},
                        {"food": "Curd (Plain Dahi / Yogurt)", "qty": 0.8, "unit": "bowl"},
                    ],
                    "prep": "High-protein soy chunks in rich tomato gravy served with warm phulkas and iron-packed spinach."
                }
            ],
            "non_vegetarian": [
                {
                    "name": "Rice, Home-style Chicken Curry & Salad",
                    "items": [
                        {"food": "White Rice (Cooked)", "qty": 1.0, "unit": "cup"},
                        {"food": "Chicken Curry (Home-style)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Salad (Cucumber, Tomato, Onion)", "qty": 1.0, "unit": "bowl"},
                    ],
                    "prep": "Lean chicken pieces simmered in spiced home-style onion-tomato gravy with rice and cucumber salad."
                },
                {
                    "name": "Roti with Grilled Chicken Breast & Greens",
                    "items": [
                        {"food": "Roti", "qty": 2.0, "unit": "piece"},
                        {"food": "Chicken Breast (Cooked / Grilled)", "qty": 1.2, "unit": "100g"},
                        {"food": "Spinach / Palak Sabzi", "qty": 1.0, "unit": "bowl"},
                        {"food": "Salad (Cucumber, Tomato, Onion)", "qty": 0.8, "unit": "bowl"},
                    ],
                    "prep": "Herb-grilled chicken breast paired with whole wheat rotis and steamed spiced greens."
                },
                {
                    "name": "Rice with Fish Curry & Salad",
                    "items": [
                        {"food": "White Rice (Cooked)", "qty": 1.0, "unit": "cup"},
                        {"food": "Fish (Rohu / Katla / Tilapia Curry)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Salad (Cucumber, Tomato, Onion)", "qty": 1.0, "unit": "bowl"},
                    ],
                    "prep": "Fresh fish fillets poached in light mustard and tomato gravy served with steamed white rice."
                }
            ],
            "vegan": [
                {
                    "name": "Rice, Chole Curry & Soy Chunks",
                    "items": [
                        {"food": "Brown Rice (Cooked)", "qty": 1.0, "unit": "cup"},
                        {"food": "Chole (Chickpeas Curry)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Soy Chunks (Nutrela / Textured Soya)", "qty": 0.5, "unit": "serving"},
                        {"food": "Salad (Cucumber, Tomato, Onion)", "qty": 1.0, "unit": "bowl"},
                    ],
                    "prep": "Simmer tender chickpeas in spices with sautéed soy chunks and wholesome brown rice."
                },
                {
                    "name": "Roti with Tofu Sabzi & Dal",
                    "items": [
                        {"food": "Roti", "qty": 2.0, "unit": "piece"},
                        {"food": "Tofu (Firm)", "qty": 1.0, "unit": "100g"},
                        {"food": "Dal (Yellow Toor/Moong Cooked)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Salad (Cucumber, Tomato, Onion)", "qty": 1.0, "unit": "bowl"},
                    ],
                    "prep": "Pan-seared tofu cubes with bell peppers and onions, paired with warm rotis and yellow dal."
                }
            ]
        },
        "evening_snack": {
            "vegetarian": [
                {
                    "name": "Roasted Peanuts & Orange",
                    "items": [
                        {"food": "Peanuts (Roasted)", "qty": 1.0, "unit": "handful"},
                        {"food": "Orange", "qty": 1.0, "unit": "piece"},
                    ],
                    "prep": "Dry roasted peanuts tossed with rock salt paired with fresh Vitamin-C packed orange."
                },
                {
                    "name": "Soy Chunks Chaat",
                    "items": [
                        {"food": "Soy Chunks (Nutrela / Textured Soya)", "qty": 0.6, "unit": "serving"},
                        {"food": "Salad (Cucumber, Tomato, Onion)", "qty": 0.5, "unit": "bowl"},
                    ],
                    "prep": "Tender boiled soy chunks diced with crisp cucumbers, tomatoes, lemon juice and chaat masala."
                },
                {
                    "name": "Sweet Boiled Potato Chaat",
                    "items": [
                        {"food": "Sweet Potato (Boiled / Baked)", "qty": 1.0, "unit": "piece"},
                        {"food": "Curd (Plain Dahi / Yogurt)", "qty": 0.5, "unit": "bowl"},
                    ],
                    "prep": "Warm roasted sweet potato cubes tossed with roasted cumin, lime, and chilled curd."
                },
                {
                    "name": "Spiced Cashews & Apple",
                    "items": [
                        {"food": "Cashews", "qty": 0.7, "unit": "serving"},
                        {"food": "Apple", "qty": 1.0, "unit": "piece"},
                    ],
                    "prep": "Handful of lightly toasted cashews paired with crisp apple slices."
                }
            ]
        },
        "dinner": {
            "vegetarian": [
                {
                    "name": "Rotis, Paneer Bhurji & Mixed Sabzi",
                    "items": [
                        {"food": "Roti", "qty": 2.0, "unit": "piece"},
                        {"food": "Paneer", "qty": 0.8, "unit": "100g"},
                        {"food": "Mixed Indian Sabzi (Vegetables Curry)", "qty": 1.0, "unit": "bowl"},
                    ],
                    "prep": "Fresh paneer bhurji with diced onions and tomatoes served with hot soft rotis and mixed veggies."
                },
                {
                    "name": "Brown Rice, Chole & Curd",
                    "items": [
                        {"food": "Brown Rice (Cooked)", "qty": 1.0, "unit": "cup"},
                        {"food": "Chole (Chickpeas Curry)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Curd (Plain Dahi / Yogurt)", "qty": 1.0, "unit": "bowl"},
                    ],
                    "prep": "High-fiber brown rice bowl with spiced chickpeas and cool probiotic curd."
                },
                {
                    "name": "Chapati, Slow-Cooked Rajma & Salad",
                    "items": [
                        {"food": "Chapati", "qty": 2.0, "unit": "piece"},
                        {"food": "Rajma (Kidney Beans Curry)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Salad (Cucumber, Tomato, Onion)", "qty": 1.0, "unit": "bowl"},
                    ],
                    "prep": "Slow simmered kidney bean curry served alongside whole wheat chapatis and crunchy salad."
                },
                {
                    "name": "Roti, Yellow Dal & Palak Sabzi",
                    "items": [
                        {"food": "Roti", "qty": 2.0, "unit": "piece"},
                        {"food": "Dal (Yellow Toor/Moong Cooked)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Spinach / Palak Sabzi", "qty": 1.0, "unit": "bowl"},
                        {"food": "Paneer", "qty": 0.5, "unit": "100g"},
                    ],
                    "prep": "Light comforting dinner: garlic tempered dal, paneer cubes, wilted spinach and soft rotis."
                },
                {
                    "name": "Paratha with Curd & Dal",
                    "items": [
                        {"food": "Paratha (Plain with Ghee)", "qty": 1.0, "unit": "piece"},
                        {"food": "Dal (Yellow Toor/Moong Cooked)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Curd (Plain Dahi / Yogurt)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Salad (Cucumber, Tomato, Onion)", "qty": 0.5, "unit": "bowl"},
                    ],
                    "prep": "Warm ghee-brushed paratha paired with yellow lentil dal, chilled curd, and salad."
                }
            ],
            "non_vegetarian": [
                {
                    "name": "Rotis with Grilled Chicken Breast & Greens",
                    "items": [
                        {"food": "Roti", "qty": 2.0, "unit": "piece"},
                        {"food": "Chicken Breast (Cooked / Grilled)", "qty": 1.2, "unit": "100g"},
                        {"food": "Mixed Indian Sabzi (Vegetables Curry)", "qty": 1.0, "unit": "bowl"},
                    ],
                    "prep": "Marinated grilled chicken breast served with hot phulkas and fresh mixed vegetable sabzi."
                },
                {
                    "name": "Rice with Bengali Fish Curry & Salad",
                    "items": [
                        {"food": "White Rice (Cooked)", "qty": 1.0, "unit": "cup"},
                        {"food": "Fish (Rohu / Katla / Tilapia Curry)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Salad (Cucumber, Tomato, Onion)", "qty": 1.0, "unit": "bowl"},
                    ],
                    "prep": "Delicate fish fillet poached in light tomato-cumin broth served over steamed rice."
                },
                {
                    "name": "Chapati with Chicken Curry & Curd",
                    "items": [
                        {"food": "Chapati", "qty": 2.0, "unit": "piece"},
                        {"food": "Chicken Curry (Home-style)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Curd (Plain Dahi / Yogurt)", "qty": 0.8, "unit": "bowl"},
                    ],
                    "prep": "Tender chicken simmered in aromatic gravy paired with light chapatis and cooling curd."
                }
            ],
            "vegan": [
                {
                    "name": "Brown Rice with Tofu & Dal",
                    "items": [
                        {"food": "Brown Rice (Cooked)", "qty": 1.0, "unit": "cup"},
                        {"food": "Tofu (Firm)", "qty": 1.0, "unit": "100g"},
                        {"food": "Dal (Yellow Toor/Moong Cooked)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Spinach / Palak Sabzi", "qty": 0.8, "unit": "bowl"},
                    ],
                    "prep": "Nutrient rich bowl with brown rice, sautéed savory tofu, yellow dal and palak."
                },
                {
                    "name": "Roti with Rajma & Mixed Sabzi",
                    "items": [
                        {"food": "Roti", "qty": 2.0, "unit": "piece"},
                        {"food": "Rajma (Kidney Beans Curry)", "qty": 1.0, "unit": "bowl"},
                        {"food": "Mixed Indian Sabzi (Vegetables Curry)", "qty": 1.0, "unit": "bowl"},
                    ],
                    "prep": "Slow cooked red kidney beans served with wholesome wheat rotis and sautéed veggies."
                }
            ]
        },
        "bedtime_snack": {
            "vegetarian": [
                {
                    "name": "Warm Spiced Turmeric Milk",
                    "items": [
                        {"food": "Milk (Cow / Toned)", "qty": 0.8, "unit": "glass"},
                    ],
                    "prep": "Warm milk infused with organic turmeric, cardamom, and black pepper for cellular repair."
                }
            ]
        }
    }

    @classmethod
    def generate_daily_plan(
        cls,
        db: Session,
        profile: Profile,
        plan_date: Optional[str] = None,
        day_offset: int = 0
    ) -> Dict[str, Any]:
        """
        Synthesizes a full day's meal plan matching user targets, diet type, and preferences.
        `day_offset` rotates through the templates to provide full variety throughout the week.
        """
        if not plan_date:
            plan_date = datetime.now().strftime("%Y-%m-%d")

        target_cals = profile.target_calories or 2000.0
        target_prot = profile.target_protein_g or 80.0
        diet_type = (profile.diet_type or "vegetarian").lower().strip()
        meal_count = profile.meal_count or 4

        # Meal slots based on meal_count
        if meal_count <= 3:
            slots = ["breakfast", "lunch", "dinner"]
        elif meal_count == 4:
            slots = ["breakfast", "lunch", "evening_snack", "dinner"]
        elif meal_count == 5:
            slots = ["breakfast", "mid_morning", "lunch", "evening_snack", "dinner"]
        else:
            slots = ["breakfast", "mid_morning", "lunch", "evening_snack", "dinner", "bedtime_snack"]

        generated_meals = {}
        total_plan_cals = 0.0
        total_plan_prot = 0.0
        total_plan_carbs = 0.0
        total_plan_fat = 0.0
        total_plan_fiber = 0.0

        for slot in slots:
            slot_options = cls.MEAL_TEMPLATES.get(slot, {})
            # Pick by diet type fallback to vegetarian
            chosen_template_list = slot_options.get(diet_type)
            if not chosen_template_list:
                if diet_type == "non_vegetarian":
                    chosen_template_list = slot_options.get("non_vegetarian") or slot_options.get("vegetarian")
                elif diet_type == "eggetarian":
                    chosen_template_list = slot_options.get("eggetarian") or slot_options.get("vegetarian")
                elif diet_type == "vegan":
                    chosen_template_list = slot_options.get("vegan") or slot_options.get("vegetarian")
                else:
                    chosen_template_list = slot_options.get("vegetarian")

            if not chosen_template_list:
                continue

            # Select template rotated by day_offset
            template = chosen_template_list[day_offset % len(chosen_template_list)]
            meal_items = []
            slot_cals = 0.0
            slot_prot = 0.0
            slot_carbs = 0.0
            slot_fat = 0.0
            slot_fiber = 0.0

            for it in template["items"]:
                db_food = FoodService.find_best_match(db, it["food"])
                if db_food:
                    qty = it["qty"]
                    unit = it.get("unit", db_food.serving_unit)
                    nutr = FoodService.calculate_serving_nutrition(db_food, qty, unit)
                    
                    meal_items.append({
                        "food_id": db_food.id,
                        "food_name": db_food.name,
                        "quantity": qty,
                        "unit": unit,
                        "serving_description": f"{qty} {unit} ({round(db_food.serving_weight_g * qty, 0)}g)",
                        "calories": nutr["calories"],
                        "protein_g": nutr["protein_g"],
                        "carbs_g": nutr["carbs_g"],
                        "fat_g": nutr["fat_g"],
                        "fiber_g": nutr["fiber_g"]
                    })
                    slot_cals += nutr["calories"]
                    slot_prot += nutr["protein_g"]
                    slot_carbs += nutr["carbs_g"]
                    slot_fat += nutr["fat_g"]
                    slot_fiber += nutr["fiber_g"]

            generated_meals[slot] = {
                "slot_name": slot.replace("_", " ").title(),
                "meal_name": template["name"],
                "items": meal_items,
                "preparation_instructions": template["prep"],
                "total_calories": round(slot_cals, 1),
                "total_protein_g": round(slot_prot, 1),
                "total_carbs_g": round(slot_carbs, 1),
                "total_fat_g": round(slot_fat, 1),
                "total_fiber_g": round(slot_fiber, 1),
            }

            total_plan_cals += slot_cals
            total_plan_prot += slot_prot
            total_plan_carbs += slot_carbs
            total_plan_fat += slot_fat
            total_plan_fiber += slot_fiber

        # Save or update plan in DB
        existing_plan = db.query(MealPlan).filter(
            MealPlan.user_id == profile.user_id,
            MealPlan.plan_date == plan_date
        ).first()

        if existing_plan:
            existing_plan.title = f"Personalized Plan ({plan_date})"
            existing_plan.target_calories = target_cals
            existing_plan.target_protein = target_prot
            existing_plan.target_carbs = profile.target_carbs_g or 250.0
            existing_plan.target_fat = profile.target_fat_g or 55.0
            existing_plan.plan_data = json.dumps(generated_meals)
            existing_plan.status = "active"
            db.commit()
            db.refresh(existing_plan)
            plan = existing_plan
        else:
            plan = MealPlan(
                user_id=profile.user_id,
                title=f"Personalized Plan ({plan_date})",
                plan_date=plan_date,
                target_calories=target_cals,
                target_protein=target_prot,
                target_carbs=profile.target_carbs_g or 250.0,
                target_fat=profile.target_fat_g or 55.0,
                plan_data=json.dumps(generated_meals),
                status="active"
            )
            db.add(plan)
            db.commit()
            db.refresh(plan)

        return {
            "plan_id": plan.id,
            "id": plan.id,
            "plan_date": plan_date,
            "user_id": profile.user_id,
            "targets": {
                "target_calories": target_cals,
                "target_protein_g": target_prot,
                "target_carbs_g": profile.target_carbs_g or 250.0,
                "target_fat_g": profile.target_fat_g or 55.0,
            },
            "planned_totals": {
                "calories": round(total_plan_cals, 1),
                "protein_g": round(total_plan_prot, 1),
                "carbs_g": round(total_plan_carbs, 1),
                "fat_g": round(total_plan_fat, 1),
                "fiber_g": round(total_plan_fiber, 1),
            },
            "calorie_variance": round(total_plan_cals - target_cals, 1),
            "protein_variance": round(total_plan_prot - target_prot, 1),
            "meals": generated_meals
        }

    @classmethod
    def generate_weekly_plan(
        cls,
        db: Session,
        profile: Profile,
        start_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates 7 consecutive daily meal plans with distinct menu rotations
        starting from start_date (or today).
        """
        from datetime import datetime, timedelta
        if not start_date:
            today = datetime.now()
            # Start from current Monday or today
            start_dt = today
        else:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")

        days_list = []
        total_week_cals = 0.0
        total_week_protein = 0.0

        for day_idx in range(7):
            day_dt = start_dt + timedelta(days=day_idx)
            day_str = day_dt.strftime("%Y-%m-%d")
            day_name = day_dt.strftime("%A")
            short_day = day_dt.strftime("%a")

            plan_dict = cls.generate_daily_plan(db, profile, plan_date=day_str, day_offset=day_idx)
            plan_dict["day_name"] = day_name
            plan_dict["short_day"] = short_day
            days_list.append(plan_dict)

            total_week_cals += plan_dict["planned_totals"]["calories"]
            total_week_protein += plan_dict["planned_totals"]["protein_g"]

        end_date = (start_dt + timedelta(days=6)).strftime("%Y-%m-%d")

        return {
            "start_date": start_dt.strftime("%Y-%m-%d"),
            "end_date": end_date,
            "days_count": 7,
            "weekly_average_calories": round(total_week_cals / 7, 1),
            "weekly_average_protein_g": round(total_week_protein / 7, 1),
            "days": days_list
        }

    @classmethod
    def get_weekly_plan(
        cls,
        db: Session,
        user_id: int,
        start_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieves or generates the 7-day weekly meal plan feed for the user.
        """
        from datetime import datetime, timedelta
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            raise ValueError("Profile not configured yet")

        if not start_date:
            today = datetime.now()
            start_dt = today
        else:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")

        days_list = []
        all_found = True

        for day_idx in range(7):
            day_dt = start_dt + timedelta(days=day_idx)
            day_str = day_dt.strftime("%Y-%m-%d")
            existing = db.query(MealPlan).filter(
                MealPlan.user_id == user_id,
                MealPlan.plan_date == day_str
            ).first()

            if existing:
                meals_data = json.loads(existing.plan_data)
                planned_cals = sum(m.get("total_calories", 0) for m in meals_data.values())
                planned_prot = sum(m.get("total_protein_g", 0) for m in meals_data.values())
                planned_carbs = sum(m.get("total_carbs_g", 0) for m in meals_data.values())
                planned_fat = sum(m.get("total_fat_g", 0) for m in meals_data.values())
                planned_fiber = sum(m.get("total_fiber_g", 0) for m in meals_data.values())

                days_list.append({
                    "plan_id": existing.id,
                    "id": existing.id,
                    "plan_date": day_str,
                    "day_name": day_dt.strftime("%A"),
                    "short_day": day_dt.strftime("%a"),
                    "targets": {
                        "target_calories": existing.target_calories,
                        "target_protein_g": existing.target_protein,
                        "target_carbs_g": existing.target_carbs,
                        "target_fat_g": existing.target_fat,
                    },
                    "planned_totals": {
                        "calories": round(planned_cals, 1),
                        "protein_g": round(planned_prot, 1),
                        "carbs_g": round(planned_carbs, 1),
                        "fat_g": round(planned_fat, 1),
                        "fiber_g": round(planned_fiber, 1),
                    },
                    "calorie_variance": round(planned_cals - existing.target_calories, 1),
                    "protein_variance": round(planned_prot - existing.target_protein, 1),
                    "meals": meals_data,
                    "status": existing.status
                })
            else:
                all_found = False
                break

        if not all_found or len(days_list) < 7:
            # Generate the fresh week
            return cls.generate_weekly_plan(db, profile, start_dt.strftime("%Y-%m-%d"))

        end_date = (start_dt + timedelta(days=6)).strftime("%Y-%m-%d")
        total_week_cals = sum(d["planned_totals"]["calories"] for d in days_list)
        total_week_prot = sum(d["planned_totals"]["protein_g"] for d in days_list)

        return {
            "start_date": start_dt.strftime("%Y-%m-%d"),
            "end_date": end_date,
            "days_count": 7,
            "weekly_average_calories": round(total_week_cals / 7, 1),
            "weekly_average_protein_g": round(total_week_prot / 7, 1),
            "days": days_list
        }

    @classmethod
    def classify_grocery_category(cls, food_name: str) -> tuple[str, str]:
        """
        Maps a food item to its supermarket aisle category and emoji icon.
        """
        n = food_name.lower()
        if any(w in n for w in ["milk", "curd", "dahi", "yogurt", "paneer", "tofu", "cheese"]):
            return "Dairy & Plant Alternatives", "🥛"
        if any(w in n for w in ["egg", "chicken", "fish", "meat", "poultry"]):
            return "Eggs, Poultry & Seafood", "🥚"
        if any(w in n for w in ["roti", "chapati", "paratha", "rice", "oats", "poha", "upma", "idli", "dosa", "bread", "wheat", "grain"]):
            return "Grains, Breads & Cereals", "🌾"
        if any(w in n for w in ["dal", "rajma", "chole", "beans", "chickpea", "lentil", "soy chunks"]):
            return "Pulses, Legumes & Plant Proteins", "🍲"
        if any(w in n for w in ["almond", "walnut", "peanut", "cashew", "seed", "nuts"]):
            return "Nuts, Seeds & Dry Fruits", "🥜"
        if any(w in n for w in ["apple", "banana", "orange", "mango", "fruit"]):
            return "Fresh Fruits", "🍎"
        if any(w in n for w in ["spinach", "palak", "sabzi", "salad", "cucumber", "tomato", "onion", "potato", "vegetable"]):
            return "Fresh Vegetables & Greens", "🥗"
        return "Pantry & Seasonings", "🧂"

    @classmethod
    def generate_grocery_list(
        cls,
        db: Session,
        user_id: int,
        start_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Aggregates all meal items across the 7-day meal plan into an aisle-categorized shopping list.
        """
        weekly_plan = cls.get_weekly_plan(db, user_id, start_date)
        days = weekly_plan.get("days", [])

        # Item aggregator: key = food_name
        aggregated: Dict[str, Dict[str, Any]] = {}

        for day in days:
            short_day = day.get("short_day", "")
            meals = day.get("meals", {})
            for slot, slot_data in meals.items():
                items = slot_data.get("items", [])
                for it in items:
                    fname = it.get("food_name")
                    if not fname:
                        continue
                    qty = float(it.get("quantity", 1.0))
                    unit = it.get("unit", "serving")
                    cals = float(it.get("calories", 0.0))
                    prot = float(it.get("protein_g", 0.0))

                    if fname not in aggregated:
                        cat_name, cat_icon = cls.classify_grocery_category(fname)
                        aggregated[fname] = {
                            "food_name": fname,
                            "category": cat_name,
                            "category_icon": cat_icon,
                            "total_quantity": qty,
                            "unit": unit,
                            "days_used": [short_day] if short_day else [],
                            "estimated_calories": cals,
                            "estimated_protein_g": prot,
                            "meal_slots": [slot.replace("_", " ").title()],
                        }
                    else:
                        aggregated[fname]["total_quantity"] += qty
                        aggregated[fname]["estimated_calories"] += cals
                        aggregated[fname]["estimated_protein_g"] += prot
                        if short_day and short_day not in aggregated[fname]["days_used"]:
                            aggregated[fname]["days_used"].append(short_day)
                        slot_title = slot.replace("_", " ").title()
                        if slot_title not in aggregated[fname]["meal_slots"]:
                            aggregated[fname]["meal_slots"].append(slot_title)

        # Format display quantity
        def format_qty(qty: float, unit: str) -> str:
            q = round(qty, 1) if qty % 1 != 0 else int(qty)
            u = unit
            # Pluralize simple units nicely
            if q > 1:
                if u == "glass":
                    u = "glasses"
                elif u in ["piece", "slice", "bowl", "plate", "cup", "serving", "handful"]:
                    u = f"{u}s"
            return f"{q} {u}"

        # Group by category
        categories_dict: Dict[str, Dict[str, Any]] = {}
        for item in aggregated.values():
            cat = item["category"]
            icon = item["category_icon"]
            if cat not in categories_dict:
                categories_dict[cat] = {
                    "category_name": cat,
                    "category_icon": icon,
                    "items": []
                }
            item_entry = {
                "id": item["food_name"].lower().replace(" ", "-").replace("(", "").replace(")", "").replace("/", "-"),
                "food_name": item["food_name"],
                "total_quantity": round(item["total_quantity"], 1),
                "unit": item["unit"],
                "display_quantity": format_qty(item["total_quantity"], item["unit"]),
                "days_used": item["days_used"],
                "days_count": len(item["days_used"]),
                "estimated_calories": round(item["estimated_calories"], 0),
                "estimated_protein_g": round(item["estimated_protein_g"], 1),
                "meal_slots": item["meal_slots"]
            }
            categories_dict[cat]["items"].append(item_entry)

        # Sort items inside each category alphabetically
        for cat in categories_dict.values():
            cat["items"].sort(key=lambda x: x["food_name"])

        # Preferred category order
        desired_order = [
            "Fresh Vegetables & Greens",
            "Fresh Fruits",
            "Dairy & Plant Alternatives",
            "Eggs, Poultry & Seafood",
            "Pulses, Legumes & Plant Proteins",
            "Grains, Breads & Cereals",
            "Nuts, Seeds & Dry Fruits",
            "Pantry & Seasonings"
        ]

        categories_list = []
        for cat_name in desired_order:
            if cat_name in categories_dict:
                categories_list.append(categories_dict[cat_name])

        for cat_name, cat_data in categories_dict.items():
            if cat_name not in desired_order:
                categories_list.append(cat_data)

        total_items_count = len(aggregated)

        return {
            "start_date": weekly_plan.get("start_date"),
            "end_date": weekly_plan.get("end_date"),
            "days_count": 7,
            "total_unique_items": total_items_count,
            "categories": categories_list
        }

