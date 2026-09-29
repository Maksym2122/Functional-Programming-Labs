from typing import Iterable, Callable, TypedDict, List, Dict, TypeVar, Optional, Union
from dataclasses import dataclass, replace

class ItemDict(TypedDict, total=False):
    id: int
    name: str
    category: str
    stock: int
    min_stock: int
    price: float
    reorder_qty: int
    reorder_cost: float
    timestamp: float

@dataclass(frozen=True)
class Product:
    id: int
    name: str
    category: str
    stock: int
    min_stock: int
    price: float
    reorder_qty: int = 0
    reorder_cost: float = 0.0
    timestamp: float = 0.0

ProductType = Union[Product, ItemDict, Dict[str, object]]

# Політики Callable
ReorderPolicyFn = Callable[[ProductType], bool]
FilterFn = Callable[[ProductType], bool]
DiscountPolicyFn = Callable[[float, int], float]
DiscountFn = Callable[[float, int], float]
TaxFn = Callable[[float], float]
NowFn = Callable[[], float]

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    """Допоміжна чиста функція композиції двох функцій."""
    return lambda x: f(g(x))

def make_multiplier(k: float) -> Callable[[float], float]:
    """Фабрика для створення множників."""
    return lambda x: x * k

def get_field(item: ProductType, field_name: str, default: object = 0) -> object:
    """Універсальне безпечне читання полів з dataclass або dict без мутацій."""
    if isinstance(item, dict):
        return item.get(field_name, default)
    return getattr(item, field_name, default)

def calculate_restock_qty(product: ProductType) -> int:
    """Чиста функція: обчислення необхідної кількості для дозамовлення."""
    stock = int(get_field(product, "stock", 0))
    min_stock = int(get_field(product, "min_stock", 0))
    needed = min_stock - stock
    return max(needed, 0)

def calculate_item_cost(product: ProductType, discount_policy: DiscountPolicyFn) -> float:
    """Чиста функція: розрахунок вартості поповнення з урахуванням політики знижки."""
    qty = calculate_restock_qty(product)
    price = float(get_field(product, "price", 0.0))
    base_cost = qty * price
    return discount_policy(base_cost, qty)

def with_reorder_info(product: ProductType, cost: float, timestamp: Optional[float] = None) -> ProductType:
    """Чиста функція: повернення НОВОГО об'єкта без мутацій вхідного."""
    qty = calculate_restock_qty(product)
    
    if isinstance(product, dict):
        new_dict = {**product, "reorder_qty": qty, "reorder_cost": cost}
        if timestamp is not None:
            new_dict["timestamp"] = timestamp
        return new_dict
    
    kwargs = {"reorder_qty": qty, "reorder_cost": cost}
    if timestamp is not None:
        kwargs["timestamp"] = timestamp
    return replace(product, **kwargs)

def filter_products(products: Iterable[ProductType], predicate: FilterFn) -> List[ProductType]:
    """Чиста функція відбору елементів за умовою."""
    return [p for p in products if predicate(p)]

def make_inventory_processor(
    *,
    needs_reorder: ReorderPolicyFn,
    discount_policy: DiscountPolicyFn,
    now: Optional[NowFn] = None
) -> Callable[[Iterable[ProductType]], Dict[str, object]]:
    """Фабрика (функція вищого порядку) для обробки товарних запасів."""
    def process(products: Iterable[ProductType]) -> Dict[str, object]:
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
            "revenue": total_cost,
            "total_cost": total_cost,
            "total_reorder_cost": total_cost,
            "items": to_reorder,
            "orders": to_reorder,
            "products": to_reorder
        }

    return process

def process_inventory_pure(
    products: Iterable[ProductType],
    *,
    bulk_threshold: int = 50,
    bulk_discount: float = 0.1
) -> Dict[str, object]:
    """Головна чиста функція обробки складських залишків."""
    needs_reorder = lambda p: int(get_field(p, "stock", 0)) < int(get_field(p, "min_stock", 0))
    discount_policy = lambda cost, qty: cost * (1.0 - bulk_discount) if qty >= bulk_threshold else cost

    processor = make_inventory_processor(
        needs_reorder=needs_reorder,
        discount_policy=discount_policy
    )
    return processor(products)