
import pytest

from closures import make_counter, make_logger, make_unit_converter
from decorators import cached, count_calls, timed


def test_closures_state_and_dependencies() -> None:
    """Перевіряє збереження стану через nonlocal та інʼєкцію залежностей у замиканнях."""
    counter = make_counter(5)
    assert counter() == 6
    assert counter() == 7

    messages: list[str] = []
    logger = make_logger("TEST", sink=messages.append)
    logger("ok")
    assert messages == ["[TEST] ok"]

    c_to_f = make_unit_converter(scale=1.8, offset=32.0, precision=2)
    assert c_to_f(0.0) == 32.0
    assert c_to_f(100.0) == 212.0


def test_metadata_preserved() -> None:
    """Перевіряє збереження __name__, __doc__ та __wrapped__ після декорування."""

    def raw_convert(x: float) -> float:
        """Оригінальний докстрінг."""
        return x * 2.0

    decorated = timed()(cached(ttl=10.0)(count_calls()(raw_convert)))

    assert decorated.__name__ == "raw_convert"
    assert decorated.__doc__ == "Оригінальний докстрінг."
    assert hasattr(decorated, "__wrapped__")


def test_cached_ttl_hit_miss_and_invalidation() -> None:
    """Перевіряє кешування, TTL за фейковим часом, статистику hit/miss та інвалідацію."""
    now = 100.0

    def fake_time() -> float:
        return now

    @cached(ttl=5.0, time_fn=fake_time)
    @count_calls()
    def transform(code: str, value: int = 1) -> str:
        return f"{code}:{value * 10}"

    assert transform("A", value=2) == "A:20"
    assert transform.get_calls() == 1
    assert transform.cache_stats() == {"hits": 0, "misses": 1, "size": 1}

    now += 4.9
    assert transform("A", value=2) == "A:20"
    assert transform.get_calls() == 1
    assert transform.cache_stats() == {"hits": 1, "misses": 1, "size": 1}

    now += 0.2
    assert transform("A", value=2) == "A:20"
    assert transform.get_calls() == 2
    assert transform.cache_stats() == {"hits": 1, "misses": 2, "size": 1}

    assert transform("B", value=3) == "B:30"
    removed = transform.cache_invalidate(lambda args, kwargs: args[0] == "A")
    assert removed == 1
    assert transform.cache_stats()["size"] == 1

    transform.cache_clear()
    assert transform.cache_stats()["size"] == 0


def test_cached_invalid_ttl_and_unhashable_args() -> None:
    """Перевіряє граничні умови: некоректний TTL та нехешовані аргументи."""
    with pytest.raises(ValueError):
        cached(ttl=0.0)

    @cached()
    def identity(items: list[int]) -> list[int]:
        return items

    with pytest.raises(TypeError):
        identity([1, 2, 3])


def test_timed_with_injected_clock_and_exception() -> None:
    """Перевіряє декоратор таймінгу без реального часу та при виникненні винятку."""
    ticks = iter([10.0, 10.025, 20.0, 20.005])
    logs: list[str] = []

    @timed("step", unit="ms", logger=logs.append, clock=lambda: next(ticks))
    def compute(flag: bool) -> int:
        if not flag:
            raise RuntimeError("boom")
        return 42

    assert compute(True) == 42
    assert logs[-1] == "[timed] step took 25.000 ms"

    with pytest.raises(RuntimeError, match="boom"):
        compute(False)
    assert logs[-1] == "[timed] step took 5.000 ms"


def test_count_calls_callback_and_reset() -> None:
    """Перевіряє роботу декоратора @count_calls, колбек та скидання лічильника."""
    events: list[tuple[str, int]] = []

    @count_calls(on_call=lambda name, n: events.append((name, n)))
    def step(x: int) -> int:
        return x + 1

    assert step(1) == 2
    assert step(2) == 3
    assert step.get_calls() == 2
    assert events == [("step", 1), ("step", 2)]

    step.reset_calls()
    assert step.get_calls() == 0