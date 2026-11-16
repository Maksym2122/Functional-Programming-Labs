from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from functools import reduce
from itertools import islice
from typing import Any, TypedDict


class SubscriberRecord(TypedDict, total=False):
    id: int
    name: str
    tariff: str
    payments: list[float]
    total_payment: float


# --- Композиція та утиліти вищого порядку ---


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Правостороння композиція функцій: compose(f, g)(x) == f(g(x))."""

    def _composed(data: Any) -> Any:
        return reduce(lambda acc, fn: fn(acc), reversed(funcs), data)

    return _composed


def pipe(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Лівостороння композиція (конвеєр): pipe(f, g)(x) == g(f(x))."""

    def _piped(data: Any) -> Any:
        return reduce(lambda acc, fn: fn(acc), funcs, data)

    return _piped


def juxt(*funcs: Callable[[Any], Any]) -> Callable[[Any], tuple[Any, ...]]:
    """Застосовує кілька функцій до одного аргументу і повертає кортеж результатів."""
    return lambda data: tuple(fn(data) for fn in funcs)


# --- Чисті трансформації (без мутації вхідних даних) ---


def normalize_names() -> (
    Callable[[Iterable[SubscriberRecord]], Iterator[SubscriberRecord]]
):
    """Нормалізує ім'я абонента (strip + Title Case) без мутації."""
    return lambda recs: (
        {**r, "name": str(r.get("name", "")).strip().title()} for r in recs
    )


def with_total_payment() -> (
    Callable[[Iterable[SubscriberRecord]], Iterator[SubscriberRecord]]
):
    """Обчислює суму платежів кожного абонента (total_payment)."""
    return lambda recs: (
        {
            **r,
            "total_payment": round(float(sum(r.get("payments") or [])), 2),
        }
        for r in recs
    )


def apply_tariff_bonus(
    target_tariff: str,
    factor: float,
) -> Callable[[Iterable[SubscriberRecord]], Iterator[SubscriberRecord]]:
    """Застосовує бонусний коефіцієнт до total_payment для обраного тарифу."""
    normalized_target = target_tariff.strip().lower()

    def _apply(r: SubscriberRecord) -> SubscriberRecord:
        base = float(r.get("total_payment", 0.0))
        is_target = str(r.get("tariff", "")).strip().lower() == normalized_target
        boosted = round(base * factor, 2) if is_target else base
        return {**r, "total_payment": boosted}

    return lambda recs: map(_apply, recs)


def filter_active(
    min_total: float = 100.0,
    min_payments_count: int = 2,
) -> Callable[[Iterable[SubscriberRecord]], Iterator[SubscriberRecord]]:
    """Відфільтровує активних абонентів за кількістю платежів та мінімальною сумою."""
    return lambda recs: filter(
        lambda r: len(r.get("payments") or []) >= min_payments_count
        and float(r.get("total_payment", 0.0)) >= min_total,
        recs,
    )


def sort_rating() -> Callable[[Iterable[SubscriberRecord]], list[SubscriberRecord]]:
    """Сортує абонентів за спаданням total_payment (тай-брейкер: id за зростанням)."""
    return lambda recs: sorted(
        recs,
        key=lambda r: (-float(r.get("total_payment", 0.0)), int(r.get("id", 0))),
    )


def take(top_n: int) -> Callable[[Iterable[SubscriberRecord]], list[SubscriberRecord]]:
    """Повертає перші N записів рейтингу без мутації."""
    if top_n < 0:
        raise ValueError("top_n не може бути від'ємним")
    return lambda recs: list(islice(recs, top_n))


# --- reduce-агрегація ---


def reduce_stats(recs: Iterable[SubscriberRecord]) -> dict[str, float]:
    """Обчислює статистику через reduce: count, payments_sum, avg_payment."""
    initial: dict[str, float] = {"count": 0.0, "payments_sum": 0.0}

    acc = reduce(
        lambda state, r: {
            "count": state["count"] + 1.0,
            "payments_sum": state["payments_sum"] + float(r.get("total_payment", 0.0)),
        },
        recs,
        initial,
    )

    count = int(acc["count"])
    payments_sum = round(acc["payments_sum"], 2)
    avg_payment = round(payments_sum / count, 2) if count > 0 else 0.0

    return {
        "count": float(count),
        "payments_sum": payments_sum,
        "avg_payment": avg_payment,
    }


# --- Складання конвеєра ---


def build_pipeline(
    top_n: int = 3,
    tariff: str = "SuperNet Pro",
    factor: float = 1.15,
    min_total: float = 100.0,
    min_payments_count: int = 2,
) -> Callable[[Iterable[SubscriberRecord]], list[SubscriberRecord]]:
    """Збирає повний функціональний конвеєр обробки абонентів через compose."""
    return compose(
        take(top_n),
        sort_rating(),
        filter_active(min_total=min_total, min_payments_count=min_payments_count),
        apply_tariff_bonus(target_tariff=tariff, factor=factor),
        with_total_payment(),
        normalize_names(),
    )
