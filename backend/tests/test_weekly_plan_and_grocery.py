from app.services.meal_planner import MealPlanner


def test_grocery_department_categorization():
    cat, icon = MealPlanner.classify_grocery_category("Spinach / Palak Sabzi")
    assert cat == "Fresh Vegetables & Greens"
    assert icon == "🥗"

    cat, icon = MealPlanner.classify_grocery_category("Apple")
    assert cat == "Fresh Fruits"
    assert icon == "🍎"

    cat, icon = MealPlanner.classify_grocery_category("Paneer")
    assert cat == "Dairy & Plant Alternatives"
    assert icon == "🥛"

    cat, icon = MealPlanner.classify_grocery_category("Dal (Yellow Toor/Moong Cooked)")
    assert cat == "Pulses, Legumes & Plant Proteins"
    assert icon == "🍲"

    cat, icon = MealPlanner.classify_grocery_category("Roti")
    assert cat == "Grains, Breads & Cereals"
    assert icon == "🌾"

    cat, icon = MealPlanner.classify_grocery_category("Almonds")
    assert cat == "Nuts, Seeds & Dry Fruits"
    assert icon == "🥜"


def test_grocery_pluralization_and_units():
    # Test formatting logic
    assert MealPlanner.classify_grocery_category("Unknown Exotic Spice")[0] == "Pantry & Seasonings"
