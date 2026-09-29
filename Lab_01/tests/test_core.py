from copy import deepcopy
import pytest
from core import (
    Order,
    process_orders_pure,
    make_processor,
    compose,
    make_multiplier,
)

@pytest.fixture
def sample_orders() -> list[Order]:
    return [
        {"id": 1, "items": [{"price": 50.0, "qty": 2}], "paid": True},
        {"id": 2, "items": [{"price": 20.0, "qty": 1}], "paid": True},
        {"id": 3, "items": [{"price": 100.0, "qty": 1}], "paid": False},
    ]

def test_referential_transparency(sample_orders: list[Order]) -> None:
    args = dict(min_total=50.0, discount=0.1, tax_rate=0.2)
    r1 = process_orders_pure(sample_orders, **args)
    r2 = process_orders_pure(sample_orders, **args)
    assert r1 == r2

def test_no_mutation(sample_orders: list[Order]) -> None:
    original = deepcopy(sample_orders)
    process_orders_pure(sample_orders, min_total=0.0, discount=0.0, tax_rate=0.0)
    assert sample_orders == original

def test_callable_policies(sample_orders: list[Order]) -> None:
    accept = lambda s: s >= 50.0
    apply_discount = lambda s: s * 0.9
    apply_tax = lambda s: s * 1.2

    processor = make_processor(
        accept=accept,
        apply_discount=apply_discount,
        apply_tax=apply_tax,
    )
    
    result = processor(sample_orders)
    assert result["count"] == 1
    assert pytest.approx(result["revenue"], 0.01) == 108.0

def test_compose_and_multiplier() -> None:
    double = make_multiplier(2)
    triple = make_multiplier(3)
    times_six = compose(double, triple)
    assert times_six(5) == 30