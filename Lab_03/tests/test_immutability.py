from types import MappingProxyType

import pytest

from core import (
    add_allergen,
    add_ingredient,
    apply_discount,
    calculate_batch_calories,
    filter_safe_dishes,
    update_price,
)
from model import Dish, Ingredient, freeze, make_meta


@pytest.fixture
def sample_dish() -> Dish:
    return Dish(
        id=1,
        name="Carbonara",
        price=240.0,
        ingredients=(
            Ingredient("Spaghetti", 150.0, 350.0),
            Ingredient("Guanciale", 50.0, 650.0),
        ),
        allergens=frozenset({"gluten", "eggs"}),
        meta=make_meta(category="pasta", chef="Marco"),
    )


def test_pure_updates_do_not_mutate_original(sample_dish: Dish) -> None:
    expected = Dish(
        id=1,
        name="Carbonara",
        price=240.0,
        ingredients=(
            Ingredient("Spaghetti", 150.0, 350.0),
            Ingredient("Guanciale", 50.0, 650.0),
        ),
        allergens=frozenset({"gluten", "eggs"}),
        meta=make_meta(category="pasta", chef="Marco"),
    )

    d1 = add_ingredient(sample_dish, "Pecorino", 30.0, 387.0)
    d2 = add_allergen(d1, "Lactose")
    d3 = update_price(d2, 265.0)

    assert sample_dish == expected
    assert len(sample_dish.ingredients) == 2
    assert "lactose" not in sample_dish.allergens
    assert sample_dish.price == 240.0

    assert d3 is not sample_dish
    assert len(d3.ingredients) == 3
    assert d3.allergens == frozenset({"gluten", "eggs", "lactose"})
    assert d3.price == 265.0


def test_dish_fields_are_frozen(sample_dish: Dish) -> None:
    with pytest.raises(AttributeError):
        sample_dish.price = 100.0  # type: ignore[misc]

    with pytest.raises(AttributeError):
        sample_dish.name = "Bolognese"  # type: ignore[misc]


def test_meta_mappingproxy_is_read_only(sample_dish: Dish) -> None:
    raw = {"category": "dessert"}
    meta = make_meta(raw)
    raw["category"] = "hacked"

    assert meta["category"] == "dessert"

    with pytest.raises(TypeError):
        sample_dish.meta["category"] = "soup"  # type: ignore[index]


def test_hashability_rules(sample_dish: Dish) -> None:
    ing1 = Ingredient("Salt", 5.0, 0.0)
    ing2 = Ingredient("Salt", 5.0, 0.0)
    ing3 = Ingredient("Pepper", 2.0, 250.0)

    ingredients_set = {ing1, ing2, ing3}
    assert len(ingredients_set) == 2
    assert hash(ing1) == hash(ing2)

    with pytest.raises(TypeError):
        hash(sample_dish)


def test_discount_and_filtering(sample_dish: Dish) -> None:
    discounted = apply_discount(sample_dish, 10.0)
    assert discounted.price == 216.0
    assert discounted.meta["discount_applied"] == "10.0%"
    assert "discount_applied" not in sample_dish.meta

    safe_menu = filter_safe_dishes((sample_dish, discounted), frozenset({"nuts"}))
    assert len(safe_menu) == 2

    restricted_menu = filter_safe_dishes((sample_dish,), frozenset({"gluten"}))
    assert len(restricted_menu) == 0


def test_deep_freeze_utility() -> None:
    nested = {"kitchen": ["hot", "cold"], "tags": {"vegan", "bio"}}
    frozen = freeze(nested)

    assert isinstance(frozen, MappingProxyType)
    assert isinstance(frozen["kitchen"], tuple)
    assert isinstance(frozen["tags"], frozenset)


def test_lru_cache_on_immutable_tuple(sample_dish: Dish) -> None:
    calculate_batch_calories.cache_clear()
    first = calculate_batch_calories(sample_dish.ingredients)
    second = calculate_batch_calories(sample_dish.ingredients)

    assert first == second == 850.0
    assert calculate_batch_calories.cache_info().hits == 1
