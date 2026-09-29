import pytest
from copy import deepcopy
from core import (
    process_inventory_pure,
    make_inventory_processor,
    compose,
    make_multiplier,
    Product
)

@pytest.fixture
def sample_products() -> list[Product]:
    return [
        {"id": 1, "name": "Товар A", "category": "Електроніка", "stock": 5, "min_stock": 20, "price": 10.0},
        {"id": 2, "name": "Товар B", "category": "Електроніка", "stock": 30, "min_stock": 10, "price": 50.0},
        {"id": 3, "name": "Товар C", "category": "Офіс", "stock": 0, "min_stock": 100, "price": 2.0}
    ]

def test_referential_transparency(sample_products):
    r1 = process_inventory_pure(sample_products, bulk_threshold=50, bulk_discount=0.1)
    r2 = process_inventory_pure(sample_products, bulk_threshold=50, bulk_discount=0.1)
    assert r1 == r2

def test_no_mutation(sample_products):
    original = deepcopy(sample_products)
    process_inventory_pure(sample_products)
    assert sample_products == original

def test_callable_policies(sample_products):
    processor = make_inventory_processor(
        needs_reorder=lambda p: p["stock"] < p["min_stock"],
        discount_policy=lambda cost, qty: cost * 0.5
    )
    result = processor(sample_products)
    assert result["count"] == 2
    assert result["total_reorder_cost"] == 175.0

def test_dependency_injection_time(sample_products):
    mock_now = lambda: 1700000000.0
    processor = make_inventory_processor(
        needs_reorder=lambda p: p["stock"] < p["min_stock"],
        discount_policy=lambda cost, qty: cost,
        now=mock_now
    )
    result = processor(sample_products)
    assert result["products"][0]["timestamp"] == 1700000000.0