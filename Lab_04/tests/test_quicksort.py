import random

from algorithms import quicksort


def test_quicksort_edge_cases() -> None:
    assert quicksort([]) == []
    assert quicksort([42]) == [42]
    assert quicksort([3, 2, 1]) == [1, 2, 3]
    assert quicksort([2, 2, 1, 3, 2]) == [1, 2, 2, 2, 3]


def test_quicksort_immutability_and_random() -> None:
    xs = [random.randint(-1000, 1000) for _ in range(500)]
    original_copy = xs[:]
    result = quicksort(xs)
    assert result == sorted(xs)
    assert xs == original_copy  # Вхідний список не мутовано