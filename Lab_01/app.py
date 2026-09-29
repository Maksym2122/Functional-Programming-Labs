import time
from core import make_processor, compose, make_multiplier, Order

def render_report(result: dict[str, object]) -> None:
    for o in result["orders"]:
        ts_str = f" at {o['timestamp']}" if "timestamp" in o else ""
        print(f"Processed order #{o['id']}: total = {o['total']:.2f}{ts_str}")
        
    print(f"Total Revenue: {result['revenue']:.2f}")

discount_10_percent = lambda s: s * 0.9
coupon_flat_5 = lambda s: max(0.0, s - 5.0)
combined_discount = compose(coupon_flat_5, discount_10_percent)

processor = make_processor(
    accept=lambda s: s >= 100.0,
    apply_discount=combined_discount,
    apply_tax=make_multiplier(1.2),
    now=time.time
)

def run(orders: list[Order]) -> None:
    result = processor(orders)
    render_report(result)

if __name__ == "__main__":
    sample_orders: list[Order] = [
        {"id": 1, "paid": True, "items": [{"price": 50.0, "qty": 3}]},
        {"id": 2, "paid": True, "items": [{"price": 20.0, "qty": 2}]},
        {"id": 3, "paid": False, "items": [{"price": 200.0, "qty": 1}]}
    ]
    run(sample_orders)