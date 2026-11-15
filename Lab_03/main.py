from core import add_allergen, add_ingredient, apply_discount, filter_safe_dishes, update_price
from model import Dish, Ingredient, make_meta


def main() -> None:
    carbonara = Dish(
        id=1,
        name="Паста Карбонара",
        price=240.0,
        ingredients=(
            Ingredient("Спагеті", 150.0, 350.0),
            Ingredient("Гуанчале", 50.0, 650.0),
        ),
        allergens=frozenset({"глютен", "яйця"}),
        meta=make_meta(category="паста", chef="Марко"),
    )

    updated = add_ingredient(carbonara, "Пекоріно", 30.0, 387.0)
    updated = add_allergen(updated, "лактоза")
    updated = update_price(updated, 265.0)
    discounted = apply_discount(updated, 10.0)

    safe_dishes = filter_safe_dishes((carbonara, discounted), frozenset({"горіхи"}))

    print(f"Початкова страва: {carbonara.name}, ціна: {carbonara.price} грн")
    print(f"Оновлена зі знижкою: {discounted.name}, ціна: {discounted.price} грн")
    print(f"Безпечних страв без горіхів: {len(safe_dishes)}")


if __name__ == "__main__":
    main()
