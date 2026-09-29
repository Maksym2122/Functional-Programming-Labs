from typing import Iterable, Callable, TypedDict, List, Dict, TypeVar, Optional, Any

class Product(TypedDict, total=False):
    id: int
    name: str
    category: str
    stock: int
    min_stock: int
    price: float
    reorder_qty: int
    reorder_cost: float
    total: float
    timestamp: float

ReorderPolicyFn = Callable[[Product], bool]
DiscountPolicyFn = Callable[[float, int], float]
DiscountFn = Callable[[float], float]
TaxFn = Callable[[float], float]
FilterFn = Callable[[Product], bool]
NowFn = Callable[[], float]

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    return lambda x: f(g(x))

def make_multiplier(k: float) -> Callable[[float], float]:
    return lambda x: x * k

def calculate_restock_qty(product: Product) -> int:
    stock: int = int(product.get("stock", 0))
    min_stock: int = int(product.get("min_stock", 0))
    needed: int = min_stock - stock
    return max(needed, 0)

def order_subtotal(product: Product) -> float:
    qty: int = calculate_restock_qty(product)
    price: float = float(product.get("price", 0.0))
    return qty * price

def calculate_item_cost(product: Product, discount_policy: DiscountPolicyFn) -> float:
    subtotal: float = order_subtotal(product)
    qty: int = calculate_restock_qty(product)
    return discount_policy(subtotal, qty)

def with_total(product: Product, total: float, timestamp: Optional[float] = None) -> Product:
    qty: int = calculate_restock_qty(product)
    new_product: Product = {
        **product,
        "reorder_qty": qty,
        "reorder_cost": total,
        "total": total,
    }
    if timestamp is not None:
        new_product["timestamp"] = timestamp
    return new_product

def with_reorder_info(product: Product, cost: float, timestamp: Optional[float] = None) -> Product:
    return with_total(product, cost, timestamp)

def filter_products(products: Iterable[Product], predicate: FilterFn) -> List[Product]:
    return [p for p in products if predicate(p)]

def make_processor(
    *,
    accept: FilterFn,
    apply_discount: DiscountFn,
    apply_tax: Optional[TaxFn] = None,
    now: Optional[NowFn] = None,
) -> Callable[[Iterable[Product]], Dict[str, Any]]:
    def process(products: Iterable[Product]) -> Dict[str, Any]:
        qualified: List[Product] = []
        revenue: float = 0.0

        for p in products:
            if not accept(p):
                continue

            subtotal: float = order_subtotal(p)
            discounted: float = apply_discount(subtotal)
            total: float = apply_tax(discounted) if apply_tax is not None else discounted

            ts: Optional[float] = now() if now is not None else None
            new_p: Product = with_total(p, total, ts)

            qualified.append(new_p)
            revenue += total

        return {
            "count": len(qualified),
            "revenue": revenue,
            "total_cost": revenue,
            "total_reorder_cost": revenue,
            "orders": qualified,
            "products": qualified,
            "items": qualified,
        }

    return process

def make_inventory_processor(
    *,
    needs_reorder: ReorderPolicyFn,
    discount_policy: DiscountPolicyFn,
    now: Optional[NowFn] = None,
) -> Callable[[Iterable[Product]], Dict[str, Any]]:
    def process(products: Iterable[Product]) -> Dict[str, Any]:
        to_reorder: List[Product] = []
        total_cost: float = 0.0

        for p in products:
            if not needs_reorder(p):
                continue

            cost: float = calculate_item_cost(p, discount_policy)
            ts: Optional[float] = now() if now is not None else None

            updated: Product = with_reorder_info(p, cost, ts)
            to_reorder.append(updated)
            total_cost += cost

        return {
            "count": len(to_reorder),
            "revenue": total_cost,
            "total_cost": total_cost,
            "total_reorder_cost": total_cost,
            "orders": to_reorder,
            "products": to_reorder,
            "items": to_reorder,
        }

    return process

def process_inventory_pure(
    products: Iterable[Product],
    *,
    bulk_threshold: int = 50,
    bulk_discount: float = 0.1,
) -> Dict[str, Any]:
    needs_reorder: ReorderPolicyFn = lambda p: int(p.get("stock", 0)) < int(p.get("min_stock", 0))
    discount_policy: DiscountPolicyFn = (
        lambda cost, qty: cost * (1.0 - bulk_discount) if qty >= bulk_threshold else cost
    )

    processor = make_inventory_processor(
        needs_reorder=needs_reorder,
        discount_policy=discount_policy,
    )
    return processor(products)