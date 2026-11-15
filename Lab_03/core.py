from collections.abc import Mapping, Sequence
from dataclasses import replace
from functools import lru_cache

from model import Dish, Ingredient, make_meta


def add_ingredient(dish: Dish, name: str, grams: float, calories_per_100g: float) -> Dish:
    return dish.with_ingredient(Ingredient(name, grams, calories_per_100g))


def add_allergen(dish: Dish, allergen: str) -> Dish:
    return dish.with_allergen(allergen.strip().lower())


def update_price(dish: Dish, new_price: float) -> Dish:
    return dish.with_price(round(new_price, 2))


def apply_discount(dish: Dish, percent: float) -> Dish:
    if not (0.0 <= percent <= 100.0):
        raise ValueError("Discount percent must be between 0 and 100")
    discounted = round(dish.price * (1.0 - percent / 100.0), 2)
    updated_meta = make_meta(dish.meta, discount_applied=f"{percent}%")
    return replace(dish, price=discounted, meta=updated_meta)


def filter_safe_dishes(
    menu: Sequence[Dish], restricted_allergens: frozenset[str]
) -> tuple[Dish, ...]:
    return tuple(dish for dish in menu if dish.allergens.isdisjoint(restricted_allergens))


def get_category(meta: Mapping[str, str]) -> str:
    return meta.get("category", "uncategorized")


@lru_cache(maxsize=256)
def calculate_batch_calories(ingredients: tuple[Ingredient, ...]) -> float:
    return sum((item.grams / 100.0) * item.calories_per_100g for item in ingredients)
