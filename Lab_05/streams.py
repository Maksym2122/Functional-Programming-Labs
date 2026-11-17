from __future__ import annotations

from collections import deque
from collections.abc import Iterable, Iterator
from itertools import accumulate, count, islice, starmap, takewhile
from typing import TypeVar

T = TypeVar("T")


# ==========================================
# 1. БАЗОВІ НЕСКІНЧЕННІ ПОТОКИ
# ==========================================
def naturals(start: int = 1) -> Iterator[int]:
    """Нескінченний потік цілих чисел, починаючи зі start (делегування до count)."""
    yield from count(start)


def fib_stream() -> Iterator[int]:
    """Нескінченний лінивий генератор чисел Фібоначчі: 0, 1, 1, 2, 3, 5..."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


# ==========================================
# 2. УНІВЕРСАЛЬНІ КОМБІНАТОРИ TAKE / DROP / ВІКНА
# ==========================================
def take[T](n: int, it: Iterable[T]) -> list[T]:
    """Взяти перші n елементів з ітерованого об'єкта у вигляді списку."""
    if n < 0:
        raise ValueError("Кількість елементів n має бути невід'ємною")
    return list(islice(it, n))


def drop[T](n: int, it: Iterable[T]) -> Iterator[T]:
    """Ліниво пропустити перші n елементів і повернути решту ітератора."""
    if n < 0:
        raise ValueError("Кількість елементів n має бути невід'ємною")
    iterator = iter(it)
    next(islice(iterator, n, n), None)
    return iterator


def sliding_window[T](it: Iterable[T], k: int) -> Iterator[tuple[T, ...]]:
    """
    Лінивий генератор ковзних вікон розміру k на базі deque(maxlen=k).
    Якщо елементів у потоці менше за k, не повертає жодного вікна.
    """
    if k <= 0:
        raise ValueError("Розмір вікна k має бути додатним цілим числом")

    iterator = iter(it)
    window: deque[T] = deque(maxlen=k)

    for _ in range(k):
        try:
            window.append(next(iterator))
        except StopIteration:
            return

    yield tuple(window)

    for item in iterator:
        window.append(item)
        yield tuple(window)


def moving_average(it: Iterable[float], k: int) -> Iterator[float]:
    """Ліниве обчислення рухомого середнього для вікон шириною k."""
    return (sum(win) / k for win in sliding_window(it, k))


# ==========================================
# 3. ВАРІАНТ 12: ПОТІК ТРИКУТНИХ ЧИСЕЛ
# ==========================================
def triangular_numbers() -> Iterator[int]:
    """
    Нескінченний лінивий потік трикутних чисел: 1, 3, 6, 10, 15, ...
    Формується як префіксні суми натуральних чисел 1, 2, 3, ...
    """
    return accumulate(count(1))


def triangular_up_to(limit: int) -> Iterator[int]:
    """Ліниво відбирає трикутні числа, що не перевищують задану межу limit."""
    return takewhile(lambda x: x <= limit, triangular_numbers())


def triangular_adjacent_diffs(limit: int) -> Iterator[int]:
    """
    Будує потік різниць сусідніх трикутних чисел (t_{n} - t_{n-1})
    для значень, що не перевищують limit.
    """
    pairs = sliding_window(triangular_up_to(limit), 2)
    return starmap(lambda prev, curr: curr - prev, pairs)
