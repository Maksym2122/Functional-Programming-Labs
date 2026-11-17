"""Параметризовані декоратори як функції вищого порядку (HOF)."""

import functools
import threading
import time
from collections.abc import Callable, Hashable
from typing import Any, Literal, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def make_key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Hashable:
    """Формує хешований ключ кешу з позиційних та іменованих аргументів."""
    return (args, tuple(sorted(kwargs.items())))


def cached(
    *,
    ttl: float | None = None,
    time_fn: Callable[[], float] = time.time,
) -> Callable[[Callable[P, R]], Any]:
    """Потокобезпечний декоратор кешування результатів із TTL, статистикою та інвалідацією."""
    if ttl is not None and ttl <= 0:
        raise ValueError("ttl має бути додатним числом або None")

    def decorator(func: Callable[P, R]) -> Any:
        cache: dict[Hashable, tuple[float | None, R]] = {}
        stats = {"hits": 0, "misses": 0}
        lock = threading.Lock()

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = make_key(args, kwargs)
            now = time_fn()
            with lock:
                if key in cache:
                    exp, val = cache[key]
                    if exp is None or now < exp:
                        stats["hits"] += 1
                        return val
                    del cache[key]
                stats["misses"] += 1

            val = func(*args, **kwargs)
            with lock:
                expiry = None if ttl is None else now + ttl
                cache[key] = (expiry, val)
            return val

        def cache_clear() -> None:
            with lock:
                cache.clear()

        def cache_invalidate(
            predicate: Callable[[tuple[Any, ...], dict[str, Any]], bool],
        ) -> int:
            removed = 0
            with lock:
                for k in list(cache.keys()):
                    args_k, kwargs_k = k[0], dict(k[1])
                    if predicate(args_k, kwargs_k):
                        del cache[k]
                        removed += 1
            return removed

        def cache_stats() -> dict[str, int]:
            with lock:
                return {"hits": stats["hits"], "misses": stats["misses"], "size": len(cache)}

        wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
        wrapper.cache_invalidate = cache_invalidate  # type: ignore[attr-defined]
        wrapper.cache_stats = cache_stats  # type: ignore[attr-defined]
        return wrapper

    return decorator


def count_calls(
    *,
    on_call: Callable[[str, int], None] | None = None,
) -> Callable[[Callable[P, R]], Any]:
    """Параметризований декоратор підрахунку кількості викликів функції через closure."""

    def decorator(func: Callable[P, R]) -> Any:
        calls = 0

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            nonlocal calls
            calls += 1
            if on_call is not None:
                on_call(func.__name__, calls)
            return func(*args, **kwargs)

        def get_calls() -> int:
            return calls

        def reset_calls() -> None:
            nonlocal calls
            calls = 0

        wrapper.get_calls = get_calls  # type: ignore[attr-defined]
        wrapper.reset_calls = reset_calls  # type: ignore[attr-defined]
        return wrapper

    return decorator


def timed(
    label: str | None = None,
    *,
    unit: Literal["s", "ms", "us"] = "ms",
    logger: Callable[[str], None] = print,
    clock: Callable[[], float] = time.perf_counter,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Параметризований декоратор вимірювання часу виконання з інʼєкцією clock та logger."""
    factors = {"s": 1.0, "ms": 1e3, "us": 1e6}
    factor = factors[unit]

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        name = label or func.__name__

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            t0 = clock()
            try:
                return func(*args, **kwargs)
            finally:
                dt = (clock() - t0) * factor
                logger(f"[timed] {name} took {dt:.3f} {unit}")

        return wrapper

    return decorator