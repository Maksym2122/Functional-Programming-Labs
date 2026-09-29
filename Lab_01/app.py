import time
from core import (
    Order,
    process_orders_pure,
    make_processor,
    stamp_total,
    compose,
    make_multiplier,
)

def render_report(result: dict) -> None:
    print("=== REPORT ===")
    print(f"Count:   {result['count']}")
    print(f"Revenue: {result['revenue']:.2f}")
    for o in result["orders"]:
        print(f"Order ID: {o['id']} | Total: {o['total']:.2f}")
    print("==============\n")

def run() -> None:
    orders: list[Order] = [
        {"id": 1, "items": [{"price": 50.0, "qty": 2}], "paid": True},
        {"id": 2, "items": [{"price": 30.0, "qty": 1}], "paid": True},
        {"id": 3, "items": [{"price": 200.0, "qty": 1}], "paid": False},
        {"id": 4, "items": [{"price": 120.0, "qty": 1}], "paid": True},
    ]

    pure_result = process_orders_pure(
        orders,
        min_total=100.0,
        discount=0.1,
        tax_rate=0.2,
    )
    render_report(pure_result)

    accept_fn = lambda s: s >= 100.0
    promo_discount = lambda s: s * 0.95
    base_discount = lambda s: s * 0.9
    combined_discount = compose(promo_discount, base_discount)
    tax_fn = make_multiplier(1.2)

    processor = make_processor(
        accept=accept_fn,
        apply_discount=combined_discount,
        apply_tax=tax_fn,
    )
    
    callable_result = processor(orders)
    render_report(callable_result)

    stamped = stamp_total(150.0, now=time.time)
    print(f"Stamped: {stamped}\n")

if __name__ == "__main__":
    run()