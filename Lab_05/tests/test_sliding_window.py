from collections.abc import Iterator

import pytest

from streams import moving_average, sliding_window, take


def test_sliding_window_basic_and_edge_cases() -> None:
    assert list(sliding_window([1, 2, 3, 4], 3)) == [(1, 2, 3), (2, 3, 4)]
    assert list(sliding_window([1, 2], 5)) == []  # k > довжини потоку
    assert list(sliding_window([], 2)) == []  # порожнє джерело


def test_sliding_window_invalid_size() -> None:
    with pytest.raises(ValueError):
        list(sliding_window([1, 2, 3], 0))
    with pytest.raises(ValueError):
        list(sliding_window([1, 2, 3], -3))


def test_moving_average() -> None:
    assert list(moving_average([2.0, 4.0, 6.0, 8.0], 2)) == [3.0, 5.0, 7.0]


def test_laziness_evaluation_count() -> None:
    """Перевірка, що потік обчислює рівно стільки елементів, скільки запрошено."""
    evaluated = 0

    def tracked_source() -> Iterator[int]:
        nonlocal evaluated
        n = 1
        while True:
            evaluated += 1
            yield n
            n += 1

    # Для 3 вікон шириною 4 потрібно витягти рівно 4 + (3 - 1) = 6 елементів
    result = take(3, sliding_window(tracked_source(), 4))
    assert result == [(1, 2, 3, 4), (2, 3, 4, 5), (3, 4, 5, 6)]
    assert evaluated == 6
