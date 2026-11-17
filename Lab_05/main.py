from __future__ import annotations

import operator
from itertools import accumulate

from streams import (
    drop,
    fib_stream,
    moving_average,
    naturals,
    sliding_window,
    take,
    triangular_adjacent_diffs,
    triangular_numbers,
    triangular_up_to,
)


def main() -> None:
    # 1. Нескінченний стрім Фібоначчі + take/drop
    first_10_fib = take(10, fib_stream())
    next_8_after_5 = take(8, drop(5, fib_stream()))
    print(f"Перші 10 чисел Фібоначчі:       {first_10_fib}")
    print(f"8 чисел Фібоначчі після 5-го:   {next_8_after_5}\n")

    # 2. Ковзні вікна та рухоме середнє
    windows = list(sliding_window([10, 20, 30, 40, 50], 3))
    avg_stream = list(
        moving_average(naturals(1), 3)[:5] if False else take(5, moving_average(naturals(1), 3))
    )
    print(f"Ковзні вікна (k=3):             {windows}")
    print(f"Перші 5 рухомих середніх (1..): {avg_stream}\n")

    # 3. Accumulate (префіксні суми та добутки)
    nums = [1, 2, 3, 4, 5]
    print(f"Префіксні суми {nums}:    {list(accumulate(nums))}")
    print(f"Префіксні добутки {nums}: {list(accumulate(nums, operator.mul))}\n")

    # 4. Варіант 12: Потік трикутних чисел
    limit = 45
    first_8_tri = take(8, triangular_numbers())
    tri_limited = list(triangular_up_to(limit))
    tri_diffs = list(triangular_adjacent_diffs(limit))

    print("--- Варіант 12: Трикутні числа ---")
    print(f"Перші 8 трикутних чисел:        {first_8_tri}")
    print(f"Трикутні числа <= {limit}:          {tri_limited}")
    print(f"Різниці сусідніх (<= {limit}):      {tri_diffs}")


if __name__ == "__main__":
    main()
