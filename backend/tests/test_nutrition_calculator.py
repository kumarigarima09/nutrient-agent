import pytest
from app.services.nutrition_calculator import NutritionCalculator


def test_calculate_bmr_male():
    # 70kg, 175cm, 25 years, male
    # BMR = 10 * 70 + 6.25 * 175 - 5 * 25 + 5
    # BMR = 700 + 1093.75 - 125 + 5 = 1673.75 -> 1673.8
    bmr = NutritionCalculator.calculate_bmr(weight_kg=70.0, height_cm=175.0, age=25, sex="male")
    assert bmr == pytest.approx(1673.8, abs=0.5)


def test_calculate_bmr_female():
    # 60kg, 165cm, 30 years, female
    # BMR = 10 * 60 + 6.25 * 165 - 5 * 30 - 161
    # BMR = 600 + 1031.25 - 150 - 161 = 1320.25 -> 1320.2
    bmr = NutritionCalculator.calculate_bmr(weight_kg=60.0, height_cm=165.0, age=30, sex="female")
    assert bmr == pytest.approx(1320.2, abs=0.5)


def test_calculate_tdee():
    bmr = 1600.0
    # Sedentary (1.2)
    assert NutritionCalculator.calculate_tdee(bmr, "sedentary") == pytest.approx(1920.0, abs=1.0)
    # Moderate (1.55)
    assert NutritionCalculator.calculate_tdee(bmr, "moderate") == pytest.approx(2480.0, abs=1.0)
    # Athlete (1.9)
    assert NutritionCalculator.calculate_tdee(bmr, "athlete") == pytest.approx(3040.0, abs=1.0)


def test_calculate_calorie_target_safety_floor():
    # Test that extreme deficit is prevented by safety floor
    target_female = NutritionCalculator.calculate_calorie_target(
        tdee=1300.0,
        goal="weight_loss",
        sex="female",
        custom_delta=-500.0
    )
    # Minimum safe floor is 1200 kcal
    assert target_female >= 1200.0


def test_calculate_protein_target():
    # Weight loss: 1.8 g/kg for 75kg
    prot = NutritionCalculator.calculate_protein_target(weight_kg=75.0, goal="weight_loss")
    assert prot["target_g"] == pytest.approx(75.0 * 1.8, abs=1.0)
    assert prot["min_g"] < prot["target_g"] < prot["max_g"]


def test_macro_distribution():
    res = NutritionCalculator.calculate_all(
        weight_kg=70.0,
        height_cm=175.0,
        age=28,
        sex="male",
        activity_level="moderate",
        goal="weight_maintenance"
    )
    assert res["target_calories"] > 0
    assert res["target_protein_g"] > 0
    assert res["target_carbs_g"] > 0
    assert res["target_fat_g"] > 0
    assert res["target_fiber_g"] >= 25.0
    assert res["target_water_ml"] >= 2500.0
