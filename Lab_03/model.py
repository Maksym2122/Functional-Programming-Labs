from collections.abc import Mapping
from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Any, NamedTuple


def make_meta(data: Mapping[str, str] | None = None, **kwargs: str) -> MappingProxyType[str, str]:
    base: dict[str, str] = dict(data) if data else {}
    base.update(kwargs)
    return MappingProxyType(base)


def freeze(obj: Any) -> Any:
    if isinstance(obj, Mapping):
        return MappingProxyType({k: freeze(v) for k, v in obj.items()})
    if isinstance(obj, (set, frozenset)):
        return frozenset(freeze(x) for x in obj)
    if isinstance(obj, (list, tuple)):
        return tuple(freeze(x) for x in obj)
    return obj


class Ingredient(NamedTuple):
    name: str
    grams: float
    calories_per_100g: float


@dataclass(frozen=True, slots=True)
class Dish:
    id: int
    name: str
    price: float
    ingredients: tuple[Ingredient, ...]
    allergens: frozenset[str]
    meta: Mapping[str, str]

    def total_weight(self) -> float:
        return sum(item.grams for item in self.ingredients)

    def total_calories(self) -> float:
        return sum((item.grams / 100.0) * item.calories_per_100g for item in self.ingredients)

    def with_ingredient(self, ingredient: Ingredient) -> "Dish":
        return replace(self, ingredients=self.ingredients + (ingredient,))

    def with_allergen(self, allergen: str) -> "Dish":
        return replace(self, allergens=self.allergens | frozenset({allergen}))

    def with_price(self, new_price: float) -> "Dish":
        if new_price < 0:
            raise ValueError("Price cannot be negative")
        return replace(self, price=new_price)
