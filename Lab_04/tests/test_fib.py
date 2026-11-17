import pytest

from algorithms import fib, fib_iter


def test_fib_small() -> None:
    fib.cache_clear()
    expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    assert [fib(i) for i in range(10)] == expected
    assert fib.cache_info().hits > 0


def test_fib_iter_parity() -> None:
    for n in range(40):
        assert fib(n) == fib_iter(n)


def test_fib_negative_raises() -> None:
    with pytest.raises(ValueError):
        fib(-1)
    with pytest.raises(ValueError):
        fib_iter(-5)