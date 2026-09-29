from typing import Callable, TypedDict


class Product(TypedDict):
    id: int
    name: str
    stock: int
    price: float
    min_stock: int
    category: str


class ProcessedProduct(Product):
    order_qty: int
    replenishment_cost: float


class Result(TypedDict):
    count: int
    total_cost: float
    products: list[ProcessedProduct]


def replenishment_quantity(product: Product) -> int:
    return max(product["min_stock"] - product["stock"], 0)


def replenishment_cost(product: Product, quantity: int) -> float:
    return product["price"] * quantity


def with_replenishment(
    product: Product,
    quantity: int,
    cost: float
) -> ProcessedProduct:
    return {
        **product,
        "order_qty": quantity,
        "replenishment_cost": cost
    }


def process_products_pure(
    products: list[Product],
    *,
    discount: float
) -> Result:
    selected: list[ProcessedProduct] = []
    total_cost = 0.0

    for product in products:
        quantity = replenishment_quantity(product)

        if quantity == 0:
            continue

        cost = replenishment_cost(product, quantity)
        cost = cost * (1 - discount)

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


ReorderFn = Callable[[Product], int]
DiscountFn = Callable[[float], float]


def make_processor(
    *,
    reorder: ReorderFn,
    apply_discount: DiscountFn
) -> Callable[[list[Product]], Result]:

    def process(products: list[Product]) -> Result:
        selected: list[ProcessedProduct] = []
        total_cost = 0.0

        for product in products:
            quantity = reorder(product)

            if quantity <= 0:
                continue

            cost = replenishment_cost(product, quantity)
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