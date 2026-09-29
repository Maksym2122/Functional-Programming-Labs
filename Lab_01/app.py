import time
from core import process_inventory_pure, make_inventory_processor, Product, ItemDict

def render_report(result: dict) -> None:
    """Ізольована I/O-функція для виводу звіту."""
    print(f"\nКількість позицій для дозамовлення: {result['count']}")
    print(f"Загальна вартість поповнення: ${result['total_reorder_cost']:.2f}\n")
    print("Товари до замовлення:")
    
    for p in result["products"]:
        name = p["name"] if isinstance(p, dict) else p.name
        cat = p["category"] if isinstance(p, dict) else p.category
        cost = p["reorder_cost"] if isinstance(p, dict) else p.reorder_cost
        qty = p["reorder_qty"] if isinstance(p, dict) else p.reorder_qty
        print(f"- {name} ({cat}): треба {qty} шт., вартість = ${cost:.2f}")

def main() -> None:
    # Вхідні дані без мутацій
    inventory: list[ItemDict] = [
        {"id": 1, "name": "Клавіатура", "category": "Периферія", "stock": 5, "min_stock": 20, "price": 40.0},
        {"id": 2, "name": "Мишка", "category": "Периферія", "stock": 50, "min_stock": 30, "price": 15.0},
        {"id": 3, "name": "Монітор", "category": "Дисплеї", "stock": 2, "min_stock": 10, "price": 200.0},
        {"id": 4, "name": "Кабель HDMI", "category": "Аксесуари", "stock": 10, "min_stock": 100, "price": 5.0},
    ]

    print("=== СКЛАДСЬКИЙ ОБЛІК (Варіант 12) ===")

    # Ін'єкція залежності часу (time.time)
    processor = make_inventory_processor(
        needs_reorder=lambda p: p["stock"] < p["min_stock"],
        discount_policy=lambda cost, qty: cost * 0.85 if qty >= 60 else cost,
        now=time.time
    )

    result = processor(inventory)
    render_report(result)

if __name__ == "__main__":
    main()