import time
from core import Product, make_inventory_processor, Category

def main() -> None:
    inventory: list[Product] = [
        Product(id=1, name="Клавіатура", category=Category.PERIPHERALS.value, stock=5, min_stock=20, price=40.0),
        Product(id=2, name="Мишка", category=Category.PERIPHERALS.value, stock=50, min_stock=30, price=15.0),
        Product(id=3, name="Монітор", category=Category.DISPLAYS.value, stock=2, min_stock=10, price=200.0),
        Product(id=4, name="Кабель HDMI", category=Category.ACCESSORIES.value, stock=10, min_stock=100, price=5.0),
    ]

    print("=== СКЛАДСЬКИЙ ОБЛІК (Варіант 12) ===")

    processor = make_inventory_processor(
        needs_reorder=lambda p: p.stock < p.min_stock,
        discount_policy=lambda cost, qty: cost * 0.85 if qty >= 60 else cost,
        now=time.time
    )

    result = processor(inventory)

    print(f"\nКількість позицій для дозамовлення: {result['count']}")
    print(f"Загальна вартість поповнення: ${result['total_reorder_cost']:.2f}\n")

    print("Товари до замовлення:")
    for p in result["products"]:
        qty = p.min_stock - p.stock
        print(f"- {p.name} ({p.category}): треба {qty} шт., вартість = ${p.reorder_cost:.2f}")

if __name__ == "__main__":
    main()