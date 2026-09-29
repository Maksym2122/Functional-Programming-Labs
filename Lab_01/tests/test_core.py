from copy import deepcopy

from core import (
    Product,
    process_products_pure,
    make_processor
)


def sample_products() -> list[Product]:
    return [
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
        }
    ]


def test_referential_transparency():
    products = sample_products()

    r1 = process_products_pure(
        products,
        discount=0.1
    )

    r2 = process_products_pure(
        products,
        discount=0.1
    )

    assert r1 == r2


def test_no_mutation():
    products = sample_products()
    original = deepcopy(products)

    process_products_pure(
        products,
        discount=0.1
    )

    assert products == original


def test_replenishment():
    products = sample_products()

    result = process_products_pure(
        products,
        discount=0.0
    )

    assert result["count"] == 2
    assert result["products"][0]["order_qty"] == 5
    assert result["products"][1]["order_qty"] == 2
    assert result["total_cost"] == 16000.0


def test_callable_policies():
    products = sample_products()

    reorder = lambda product: max(
        product["min_stock"] - product["stock"],
        0
    )

    apply_discount = lambda cost: cost * 0.9

    processor = make_processor(
        reorder=reorder,
        apply_discount=apply_discount
    )

    result = processor(products)

    assert result["count"] == 2
    assert result["total_cost"] == 14400.0