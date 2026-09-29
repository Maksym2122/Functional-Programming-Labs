import pytest
from copy import deepcopy
from core import process_orders_pure, make_processor, compose, make_multiplier, Order

@pytest.fixture
def sample_orders() -> list[Order]:
    return [
        {"id": 1, "paid": True, "items": [{"price": 50.0, "qty": 3}]},
        {"id": 2, "paid": True, "items": [{"price": 20.0, "qty": 2}]},
        {"id": 3, "paid": False, "items": [{"price": 200.0, "qty": 1}]}
    ]

def test_referential_transparency(sample_orders):
    args = dict(min_total=100, discount=0.1, tax_rate=0.2)
    r1 = process_orders_pure(sample_orders, **args)
    r2 = process_orders_pure(sample_orders, **args)
    assert r1 == r2

def test_no_mutation(sample_orders):
    original = deepcopy(sample_orders)
    process_orders_pure(sample_orders, min_total=0, discount=0.0, tax_rate=0.0)
    assert sample_orders == original

def test_callable_policies(sample_orders):
    processor = make_processor(
        accept=lambda s: s >= 50,
        apply_discount=lambda s: s * 0.9,
        apply_tax=lambda s: s * 1.2
    )
    result = processor(sample_orders)
    assert result["count"] == 1
    assert result["revenue"] == 150.0 * 0.9 * 1.2

def test_dependency_injection_time(sample_orders):
    mock_now = lambda: 1700000000.0
    processor = make_processor(
        accept=lambda s: s >= 100,
        apply_discount=lambda s: s,
        apply_tax=lambda s: s,
        now=mock_now
    )
    result = processor(sample_orders)
    assert result["orders"][0]["timestamp"] == 1700000000.0