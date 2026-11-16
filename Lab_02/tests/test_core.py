from __future__ import annotations

import copy

import pytest

from core import (
    SubscriberRecord,
    apply_tariff_bonus,
    build_pipeline,
    compose,
    filter_active,
    juxt,
    normalize_names,
    pipe,
    reduce_stats,
    sort_rating,
    take,
    with_total_payment,
)


@pytest.fixture
def sample_subscribers() -> list[SubscriberRecord]:
    return [
        {
            "id": 1,
            "name": "  іван петренко ",
            "tariff": "SuperNet Pro",
            "payments": [100.0, 100.0],
        },
        {
            "id": 2,
            "name": "ольга сидоренко",
            "tariff": "Joice Start",
            "payments": [150.0, 150.0],
        },
        {
            "id": 3,
            "name": "петро іванов",
            "tariff": "SuperNet Pro",
            "payments": [200.0, 100.0],
        },
        {
            "id": 4,
            "name": "новий абонент",
            "tariff": "SuperNet Pro",
            "payments": [500.0],
        },
        {
            "id": 5,
            "name": "малий платіж",
            "tariff": "Joice Start",
            "payments": [30.0, 40.0],
        },
    ]


def test_immutability(sample_subscribers: list[SubscriberRecord]) -> None:
    """Перевіряє відсутність мутацій вхідних записів."""
    original_snapshot = copy.deepcopy(sample_subscribers)
    pipeline = build_pipeline(
        top_n=3, tariff="SuperNet Pro", factor=1.2, min_total=100.0
    )

    result = pipeline(sample_subscribers)

    assert sample_subscribers == original_snapshot
    assert all("total_payment" not in rec for rec in sample_subscribers)
    assert len(result) == 3


def test_pipeline_top_n_and_sorting(sample_subscribers: list[SubscriberRecord]) -> None:
    """Перевіряє коректність обчислень, фільтрації активних та формування Top-N."""
    pipeline = build_pipeline(
        top_n=2, tariff="SuperNet Pro", factor=1.2, min_total=100.0
    )
    top2 = pipeline(sample_subscribers)

    assert [r["id"] for r in top2] == [3, 2]
    assert top2[0]["total_payment"] == 360.0
    assert top2[0]["name"] == "Петро Іванов"
    assert top2[1]["total_payment"] == 300.0


def test_tie_breaker_by_id_ascending() -> None:
    """При однакових сумах перемагає абонент із меншим id."""
    records: list[SubscriberRecord] = [
        {"id": 20, "name": "B", "tariff": "Base", "payments": [100.0, 100.0]},
        {"id": 10, "name": "A", "tariff": "Base", "payments": [100.0, 100.0]},
    ]
    pipeline = build_pipeline(top_n=2, tariff="Other", factor=1.5, min_total=100.0)
    res = pipeline(records)

    assert [r["id"] for r in res] == [10, 20]


def test_reduce_stats() -> None:
    """Перевіряє reduce-агрегацію: count, payments_sum, avg_payment."""
    processed: list[SubscriberRecord] = [
        {"id": 1, "total_payment": 200.0},
        {"id": 2, "total_payment": 300.0},
        {"id": 3, "total_payment": 400.0},
    ]
    assert reduce_stats(processed) == {
        "count": 3.0,
        "payments_sum": 900.0,
        "avg_payment": 300.0,
    }


def test_reduce_stats_empty() -> None:
    """Перевіряє reduce_stats на порожньому списку."""
    assert reduce_stats([]) == {
        "count": 0.0,
        "payments_sum": 0.0,
        "avg_payment": 0.0,
    }


def test_compose_and_pipe_equivalence(
    sample_subscribers: list[SubscriberRecord],
) -> None:
    """Перевіряє еквівалентність compose та pipe."""
    composed = compose(
        take(2),
        sort_rating(),
        filter_active(min_total=100.0, min_payments_count=2),
        apply_tariff_bonus("SuperNet Pro", 1.1),
        with_total_payment(),
        normalize_names(),
    )
    piped = pipe(
        normalize_names(),
        with_total_payment(),
        apply_tariff_bonus("SuperNet Pro", 1.1),
        filter_active(min_total=100.0, min_payments_count=2),
        sort_rating(),
        take(2),
    )

    assert composed(sample_subscribers) == piped(sample_subscribers)


def test_juxt_and_negative_take() -> None:
    """Перевіряє роботу juxt та валідацію від'ємного top_n."""
    fn = juxt(lambda x: x + 1, lambda x: x * 2)
    assert fn(5) == (6, 10)

    with pytest.raises(ValueError):
        take(-1)
