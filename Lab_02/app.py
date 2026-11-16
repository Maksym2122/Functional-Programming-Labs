from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

from core import SubscriberRecord, build_pipeline, juxt, reduce_stats


def load_records(file_path: Path) -> list[SubscriberRecord]:
    raw = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise TypeError("JSON файл повинен містити список записів.")
    return cast(list[SubscriberRecord], raw)


def parse_args() -> argparse.Namespace:
    default_data = Path(__file__).resolve().parent / "sample_data.json"
    parser = argparse.ArgumentParser(
        description="Варіант 12: Конвеєр обробки мобільних абонентів"
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=default_data,
        help="Шлях до JSON-файлу з вхідними даними",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="Кількість топ-абонентів у рейтингу",
    )
    parser.add_argument(
        "--tariff",
        type=str,
        default="SuperNet Pro",
        help="Назва тарифу для нарахування бонусу",
    )
    parser.add_argument(
        "--factor",
        type=float,
        default=1.15,
        help="Бонусний множник для обраного тарифу",
    )
    parser.add_argument(
        "--min-total",
        type=float,
        default=150.0,
        help="Мінімальна сума платежів для фільтрації активних абонентів",
    )
    return parser.parse_args()


def run() -> None:
    """Головна функція запуску CLI-застосунку."""
    args = parse_args()
    records = load_records(args.data)

    pipeline = build_pipeline(
        top_n=args.top,
        tariff=args.tariff,
        factor=args.factor,
        min_total=args.min_total,
    )

    top_subscribers = pipeline(records)
    analyze = juxt(len, reduce_stats)
    count, stats = analyze(top_subscribers)

    print(
        f"=== Топ-{count} активних абонентів (бонус для '{args.tariff}' x{args.factor}) ==="
    )
    for idx, sub in enumerate(top_subscribers, start=1):
        print(
            f"{idx}. [ID: {sub['id']}] {sub['name']} | "
            f"Тариф: {sub['tariff']} | Сума з бонусом: {sub['total_payment']:.2f} грн"
        )

    print("\n=== Статистика (reduce_stats) ===")
    print(f"Кількість: {int(stats['count'])}")
    print(f"Загальна сума платежів: {stats['payments_sum']:.2f} грн")
    print(f"Середній платіж: {stats['avg_payment']:.2f} грн")


if __name__ == "__main__":
    run()
