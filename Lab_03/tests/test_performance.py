from copy import deepcopy
from typing import Any

from core import add_ingredient, update_price
from model import Dish, Ingredient, make_meta


def _mutable_update(order: dict[str, Any]) -> dict[str, Any]:
    copied = deepcopy(order)
    copied["items"].append({"name": "Basil", "grams": 5.0, "cal": 23.0})
    copied["price"] = 250.0
    return copied


def test_benchmark_mutable_with_deepcopy(benchmark: Any) -> None:
    mutable_dish: dict[str, Any] = {
        "id": 1,
        "name": "Pizza",
        "price": 220.0,
        "items": [{"name": "Dough", "grams": 200.0, "cal": 260.0} for _ in range(50)],
        "allergens": {"gluten"},
        "meta": {"category": "main"},
    }
    benchmark(_mutable_update, mutable_dish)


def test_benchmark_immutable_pure_update(benchmark: Any) -> None:
    immutable_dish = Dish(
        id=1,
        name="Pizza",
        price=220.0,
        ingredients=tuple(Ingredient("Dough", 200.0, 260.0) for _ in range(50)),
        allergens=frozenset({"gluten"}),
        meta=make_meta(category="main"),
    )

    def _run() -> Dish:
        d = add_ingredient(immutable_dish, "Basil", 5.0, 23.0)
        return update_price(d, 250.0)

    benchmark(_run)
