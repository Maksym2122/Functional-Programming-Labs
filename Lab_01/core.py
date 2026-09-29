from typing import Iterable, Callable, TypedDict, Dict, TypeVar, Optional

class Product(TypedDict, total=False):
    id: int
    name: str
    category: str
    stock: int
    min_stock: int
    price: float
    reorder_qty: int
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
    stock = product.get("stock", 0)
    min_stock = product.get("min_stock", 0)
    return max(min_stock - stock, 0)

def calculate_item_cost(product: Product, discount_policy: DiscountPolicyFn) -> float:
    qty = calculate_restock_qty(product)
    price = product.get("price", 0.0)
    base_cost = qty * price
    return discount_policy(base_cost, qty)

def with_reorder_info(product: Product, cost: float, timestamp: Optional[float] = None) -> Product:
    qty = calculate_restock_qty(product)
    new_product = {
        **product,
        "reorder_qty": qty,
        "reorder_cost": cost
    }
    if timestamp is not None:
        new_product["timestamp"] = timestamp
    return new_product

def make_inventory_processor(
    *,
    needs_reorder: ReorderPolicyFn,
    discount_policy: DiscountPolicyFn,
    now: Optional[NowFn] = None
) -> Callable[[Iterable[Product]], Dict[str, object]]:
    def process(products: Iterable[Product]) -> Dict[str, object]:
        to_reorder = []
        total_cost = 0.0

        for p in products:
            if not needs_reorder(p):
                continue
            
            cost = calculate_item_cost(p, discount_policy)
            ts = now() if now is not None else None
            
            updated = with_reorder_info(p, cost, ts)
            to_reorder.append(updated)
            total_cost += cost

        return {
            "count": len(to_reorder),
            "total_cost": total_cost,
            "total_reorder_cost": total_cost,
            "items": to_reorder,
            "products": to_reorder
        }

    return process

def process_inventory_pure(
    products: Iterable[Product],
    *,
    bulk_threshold: int = 50,
    bulk_discount: float = 0.1
) -> Dict[str, object]:
    needs_reorder = lambda p: p.get("stock", 0) < p.get("min_stock", 0)
    discount_policy = lambda cost, qty: cost * (1.0 - bulk_discount) if qty >= bulk_threshold else cost

    processor = make_inventory_processor(
        needs_reorder=needs_reorder,
        discount_policy=discount_policy
    )
    return processor(products)