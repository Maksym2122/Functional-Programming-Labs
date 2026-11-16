"""Автоматичні тести для модуля core.py та точки входу."""

from copy import deepcopy
from typing import List

import pytest

from core import (
    Product,
    calculate_restock_qty,
    compose,
    filter_products,
    make_inventory_processor,
    make_multiplier,
    make_processor,
    order_subtotal,
    process_inventory_pure,
    with_total,
)


@pytest.fixture
def sample_products() -> List[Product]:
    return [
        {
            "id": 1,
            "name": "Товар A",
            "category": "Електроніка",
            "stock": 5,
            "min_stock": 20,
            "price": 10.0,
        },
        {
            "id": 2,
            "name": "Товар B",
            "category": "Електроніка",
            "stock": 30,
            "min_stock": 10,
            "price": 50.0,
        },
        {
            "id": 3,
            "name": "Товар C",
            "category": "Офіс",
            "stock": 0,
            "min_stock": 100,
            "price": 2.0,
        },
    ]


def test_referential_transparency(sample_products: List[Product]) -> None:
    r1 = process_inventory_pure(sample_products, bulk_threshold=50, bulk_discount=0.1)
    r2 = process_inventory_pure(sample_products, bulk_threshold=50, bulk_discount=0.1)
    assert r1 == r2


def test_no_mutation(sample_products: List[Product]) -> None:
    original = deepcopy(sample_products)
    process_inventory_pure(sample_products)
    assert sample_products == original


def test_callable_policies(sample_products: List[Product]) -> None:
    processor = make_inventory_processor(
        needs_reorder=lambda p: int(p.get("stock", 0)) < int(p.get("min_stock", 0)),
        discount_policy=lambda cost, qty: cost * 0.5,
    )
    result = processor(sample_products)
    assert result["count"] == 2
    assert result["total_reorder_cost"] == 175.0


def test_dependency_injection_time(sample_products: List[Product]) -> None:
    mock_now = lambda: 1700000000.0
    processor = make_inventory_processor(
        needs_reorder=lambda p: int(p.get("stock", 0)) < int(p.get("min_stock", 0)),
        discount_policy=lambda cost, qty: cost,
        now=mock_now,
    )
    result = processor(sample_products)
    assert result["products"][0]["timestamp"] == 1700000000.0


def test_compose_and_multiplier() -> None:
    double = make_multiplier(2.0)
    add_ten_percent = lambda x: x * 1.1
    combined = compose(add_ten_percent, double)
    assert combined(10.0) == 22.0


def test_helpers(sample_products: List[Product]) -> None:
    p = sample_products[0]
    assert calculate_restock_qty(p) == 15
    assert order_subtotal(p) == 150.0
    updated = with_total(p, 135.0)
    assert updated["total"] == 135.0


def test_filter_and_generic_processor(sample_products: List[Product]) -> None:
    electronics = filter_products(
        sample_products, lambda p: p.get("category") == "Електроніка"
    )
    assert len(electronics) == 2

    processor = make_processor(
        accept=lambda p: calculate_restock_qty(p) > 0,
        apply_discount=lambda s: s * 0.9,
        apply_tax=lambda d: d * 1.2,
    )
    result = processor(sample_products)
    assert result["count"] == 2
    assert result["total_cost"] == pytest.approx(378.0)


def test_empty_inventory() -> None:
    result = process_inventory_pure([])
    assert result["count"] == 0
    assert result["total_reorder_cost"] == 0.0
    assert result["products"] == []