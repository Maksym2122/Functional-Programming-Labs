from typing import Callable, TypedDict


class Product(TypedDict, total=False):
    id: int
    name: str
    stock: int
    price: float
    min_stock: int
    category: str
    order_qty: int
    replenishment_cost: float


def replenishment_quantity(product: Product) -> int:
    return max(product["min_stock"] - product["stock"], 0)


def replenishment_cost(product: Product, quantity: int) -> float:
    return product["price"] * quantity


def with_replenishment(
    product: Product,
    quantity: int,
    cost: float
) -> Product:
    return {
        **product,
        "order_qty": quantity,
        "replenishment_cost": cost
    }


def process_products_pure(
    products: list[Product],
    *,
    discount: float
) -> dict[str, object]:
    selected = []
    total_cost = 0.0

    for product in products:
        quantity = replenishment_quantity(product)

        if quantity == 0:
            continue

        cost = replenishment_cost(product, quantity)
        cost = cost * (1 - discount)

        new_product = with_replenishment(product, quantity, cost)
        selected.append(new_product)

        total_cost += cost

    return {
        "count": len(selected),
        "total_cost": total_cost,
        "products": selected
    }


ReorderFn = Callable[[Product], int]
DiscountFn = Callable[[float], float]


def make_processor(
    *,
    reorder: ReorderFn,
    apply_discount: DiscountFn
) -> Callable[[list[Product]], dict[str, object]]:

    def process(products: list[Product]) -> dict[str, object]:
        selected = []
        total_cost = 0.0

        for product in products:
            quantity = reorder(product)

            if quantity <= 0:
                continue

            cost = product["price"] * quantity
            cost = apply_discount(cost)

            new_product = with_replenishment(
                product,
                quantity,
                cost
            )

            selected.append(new_product)
            total_cost += cost

        return {
            "count": len(selected),
            "total_cost": total_cost,
            "products": selected
        }

    return process