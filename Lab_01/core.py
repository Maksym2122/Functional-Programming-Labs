from typing import Iterable, Callable, TypedDict, List, Dict, TypeVar, Optional

class Item(TypedDict):
    price: float
    qty: int

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
    stock = product.get("stock", 0)
    min_stock = product.get("min_stock", 0)
    needed = min_stock - stock
    return max(needed, 0)

def order_subtotal(product: Product) -> float:
    qty = calculate_restock_qty(product)
    price = product.get("price", 0.0)
    return qty * price

def calculate_item_cost(product: Product, discount_policy: DiscountPolicyFn) -> float:
    subtotal = order_subtotal(product)
    qty = calculate_restock_qty(product)
    return discount_policy(subtotal, qty)

def with_total(product: Product, total: float, timestamp: Optional[float] = None) -> Product:
    qty = calculate_restock_qty(product)
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
) -> Callable[[Iterable[Product]], Dict[str, object]]:
    def process(products: Iterable[Product]) -> Dict[str, object]:
        qualified: List[Product] = []
        revenue = 0.0

        for p in products:
            if not accept(p):
                continue

            subtotal = order_subtotal(p)
            discounted = apply_discount(subtotal)
            total = apply_tax(discounted) if apply_tax else discounted

            ts = now() if now is not None else None
            new_p = with_total(p, total, ts)

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
) -> Callable[[Iterable[Product]], Dict[str, object]]:
    accept: FilterFn = needs_reorder
    apply_discount: DiscountFn = lambda subtotal: discount_policy(subtotal, 1)

    return make_processor(
        accept=accept,
        apply_discount=apply_discount,
        now=now,
    )

def process_inventory_pure(
    products: Iterable[Product],
    *,
    bulk_threshold: int = 50,
    bulk_discount: float = 0.1,
) -> Dict[str, object]:
    needs_reorder: ReorderPolicyFn = lambda p: p.get("stock", 0) < p.get("min_stock", 0)
    discount_policy: DiscountPolicyFn = (
        lambda cost, qty: cost * (1.0 - bulk_discount) if qty >= bulk_threshold else cost
    )

    processor = make_inventory_processor(
        needs_reorder=needs_reorder,
        discount_policy=discount_policy,
    )
    return processor(products)