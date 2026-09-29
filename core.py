from typing import Iterable, Callable, TypedDict, List, Dict, TypeVar

class Item(TypedDict):
    price: float
    qty: int

class Order(TypedDict, total=False):
    id: int
    items: List[Item]
    paid: bool
    total: float

SubtotalFn = Callable[[Order], float]
FilterFn = Callable[[float], bool]
DiscountFn = Callable[[float], float]
TaxFn = Callable[[float], float]
NowFn = Callable[[], float]

def order_subtotal(order: Order) -> float:
    return sum(it["price"] * it["qty"] for it in order["items"])

def with_total(order: Order, total: float) -> Order:
    return {**order, "total": total}

def process_orders_pure(
    orders: Iterable[Order],
    min_total: float,
    discount: float,
    tax_rate: float,
) -> Dict[str, object]:
    paid_orders = (o for o in orders if o.get("paid", False))
    qualified: List[Order] = []
    revenue = 0.0

    for o in paid_orders:
        subtotal = order_subtotal(o)
        if subtotal < min_total:
            continue

        discounted = subtotal * (1 - discount)
        total = discounted * (1 + tax_rate)

        new_o = with_total(o, total)
        qualified.append(new_o)
        revenue += total

    return {
        "count": len(qualified),
        "revenue": revenue,
        "orders": qualified,
    }

def make_processor(
    accept: FilterFn,
    apply_discount: DiscountFn,
    apply_tax: TaxFn,
) -> Callable[[List[Order]], Dict[str, object]]:
    def process(orders: List[Order]) -> Dict[str, object]:
        qualified: List[Order] = []
        revenue = 0.0

        for o in orders:
            if not o.get("paid", False):
                continue

            subtotal = order_subtotal(o)
            if not accept(subtotal):
                continue

            total = apply_tax(apply_discount(subtotal))
            qualified.append(with_total(o, total))
            revenue += total

        return {
            "count": len(qualified),
            "revenue": revenue,
            "orders": qualified,
        }

    return process

def stamp_total(total: float, now: NowFn) -> tuple[float, float]:
    return total, now()

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    return lambda x: f(g(x))

def make_multiplier(k: float) -> Callable[[float], float]:
    return lambda x: x * k