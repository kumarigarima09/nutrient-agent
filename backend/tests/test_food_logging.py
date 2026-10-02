import pytest
from app.services.food_logger import FoodLogger


def test_parse_natural_language_three_items():
    text = "I ate two eggs, three rotis and one glass of milk"
    parsed = FoodLogger.parse_natural_language_text(text)
    items = parsed["items"]
    assert len(items) == 3

    # Check item 1: two eggs
    egg_item = next(it for it in items if "egg" in it["raw_food_text"])
    assert egg_item["quantity"] == 2.0

    # Check item 2: three rotis
    roti_item = next(it for it in items if "roti" in it["raw_food_text"])
    assert roti_item["quantity"] == 3.0

    # Check item 3: one glass of milk
    milk_item = next(it for it in items if "milk" in it["raw_food_text"])
    assert milk_item["quantity"] == 1.0
    assert milk_item["unit"] in ["glass", "glasses"]


def test_parse_ambiguous_portion():
    text = "Had some rice and a bowl of dal"
    parsed = FoodLogger.parse_natural_language_text(text)
    items = parsed["items"]

    rice_item = next(it for it in items if "rice" in it["raw_food_text"])
    assert rice_item["is_ambiguous"] is True

    dal_item = next(it for it in items if "dal" in it["raw_food_text"])
    assert dal_item["unit"] == "bowl"
