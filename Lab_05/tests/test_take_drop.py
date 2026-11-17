from itertools import count

import pytest

from streams import drop, take


def test_take_drop_infinite_stream() -> None:
    stream = count(1)
    assert take(4, stream) == [1, 2, 3, 4]
    # Ітератор просунувся на 4 кроки вперед
    assert take(3, stream) == [5, 6, 7]


def test_take_drop_edge_cases() -> None:
    assert take(0, count(1)) == []
    assert take(5, []) == []
    assert list(drop(0, [1, 2, 3])) == [1, 2, 3]
    assert list(drop(10, [1, 2, 3])) == []


def test_take_drop_negative_raises() -> None:
    with pytest.raises(ValueError):
        take(-1, [1, 2, 3])
    with pytest.raises(ValueError):
        drop(-2, [1, 2, 3])
