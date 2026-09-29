from core import Product, process_products_pure, make_processor


products: list[Product] = [
    {
        "id": 1,
        "name": "Keyboard",
        "stock": 5,
        "price": 800.0,
        "min_stock": 10,
        "category": "Accessories"
    },
    {
        "id": 2,
        "name": "Mouse",
        "stock": 15,
        "price": 500.0,
        "min_stock": 10,
        "category": "Accessories"
    },
    {
        "id": 3,
        "name": "Monitor",
        "stock": 3,
        "price": 6000.0,
        "min_stock": 5,
        "category": "Displays"
    },
    {
        "id": 4,
        "name": "USB Cable",
        "stock": 4,
        "price": 200.0,
        "min_stock": 8,
        "category": "Cables"
    }
]


def render_report(result: dict) -> None:
    print("Products for replenishment:")

    for product in result["products"]:
        print(
            product["name"],
            "| Category:", product["category"],
            "| Quantity:", product["order_qty"],
            "| Cost:", product["replenishment_cost"]
        )

    print("Count:", result["count"])
    print("Total cost:", result["total_cost"])


def main() -> None:
    result = process_products_pure(
        products,
        discount=0.1
    )

    render_report(result)

    reorder = lambda product: max(
        product["min_stock"] - product["stock"],
        0
    )

    apply_discount = lambda cost: cost * 0.9

    processor = make_processor(
        reorder=reorder,
        apply_discount=apply_discount
    )

    result2 = processor(products)

    print("\nUsing Callable:")
    render_report(result2)


if __name__ == "__main__":
    main()