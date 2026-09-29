from typing import Iterable, Callable, TypedDict, List, Dict, TypeVar

class Product(TypedDict):
    id: int
    name: str
    category: str
    stock: int
    min_stock: int
    price: float
    reorder_cost: float
    timestamp: float

ReorderPolicyFn = Callable[[Product], bool]
DiscountPolicyFn = Callable[[float, int], float]
NowFn = Callable[[], float]

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    return lambda x: f(g(x))

def make_multiplier(k: float) -> Callable[[float], float]:
    return lambda x: x * k

def calculate_restock_qty(product: Product) -> int:
    needed = product["min_stock"] - product["stock"]
    return max(needed, 0)

def calculate_item_cost(product: Product, discount_policy: DiscountPolicyFn) -> float:
    qty = calculate_restock_qty(product)
    base_cost = qty * product["price"]
    return discount_policy(base_cost, qty)

def with_reorder_info(product: Product, cost: float, timestamp: float | None = None) -> Product:
    new_product = {**product, "reorder_cost": cost}
    if timestamp is not None:
        new_product["timestamp"] = timestamp
    return new_product

def make_inventory_processor(
    *,
    needs_reorder: ReorderPolicyFn,
    discount_policy: DiscountPolicyFn,
    now: NowFn | None = None
) -> Callable[[Iterable[Product]], Dict[str, object]]:
    def process(products: Iterable[Product]) -> Dict[str, object]:
        to_reorder = []
        total_cost = 0.0

        for p in products:
            if not needs_reorder(p):
                continue
            
            cost = calculate_item_cost(p, discount_policy)
            timestamp = now() if now else None
            
            updated = with_reorder_info(p, cost, timestamp)
            to_reorder.append(updated)
            total_cost += cost

        return {
            "count": len(to_reorder),
            "total_reorder_cost": total_cost,
            "products": to_reorder
        }

    return process

def process_inventory_pure(
    products: Iterable[Product],
    *,
    bulk_threshold: int = 50,
    bulk_discount: float = 0.1
) -> Dict[str, object]:
    needs_reorder = lambda p: p["stock"] < p["min_stock"]
    discount_policy = lambda cost, qty: cost * (1 - bulk_discount) if qty >= bulk_threshold else cost

    processor = make_inventory_processor(
        needs_reorder=needs_reorder,
        discount_policy=discount_policy
    )
    return processor(products)