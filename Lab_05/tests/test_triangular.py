from streams import (
    take,
    triangular_adjacent_diffs,
    triangular_numbers,
    triangular_up_to,
)


def test_triangular_first_n() -> None:
    assert take(7, triangular_numbers()) == [1, 3, 6, 10, 15, 21, 28]


def test_triangular_up_to_limit() -> None:
    assert list(triangular_up_to(21)) == [1, 3, 6, 10, 15, 21]
    assert list(triangular_up_to(20)) == [1, 3, 6, 10, 15]
    assert list(triangular_up_to(0)) == []


def test_triangular_adjacent_diffs() -> None:
    # Трикутні <= 28: [1, 3, 6, 10, 15, 21, 28]
    # Різниці сусідів: [2, 3, 4, 5, 6, 7]
    assert list(triangular_adjacent_diffs(28)) == [2, 3, 4, 5, 6, 7]
    # Якщо елемент лише один (limit=1), пар для різниці немає
    assert list(triangular_adjacent_diffs(1)) == []
