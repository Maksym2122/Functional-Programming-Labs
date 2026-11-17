from itertools import islice

from streams import drop, fib_stream, take


def test_fib_first_10() -> None:
    assert list(islice(fib_stream(), 10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_fib_drop_and_take() -> None:
    assert take(5, drop(6, fib_stream())) == [8, 13, 21, 34, 55]
