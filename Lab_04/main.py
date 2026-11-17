from __future__ import annotations

import sys
import time

from algorithms import (
    Node,
    bfs_level_order,
    dfs_preorder_iter,
    fib,
    fib_iter,
    inorder,
    lcs_iter,
    lcs_memo,
    lcs_naive,
    postorder,
    preorder,
    quicksort,
)


def main() -> None:
    print(f"Поточний ліміт глибини рекурсії CPython: {sys.getrecursionlimit()}\n")

    # 1. Quicksort
    data = [15, 3, 9, 8, 5, 2, 7, 1, 6, 9]
    sorted_data = quicksort(data)
    print(f"Quicksort вхід:  {data}")
    print(f"Quicksort вихід: {sorted_data}\n")

    # 2. Обходи бінарного дерева
    tree = Node(
        4,
        left=Node(2, Node(1), Node(3)),
        right=Node(6, None, Node(7)),
    )
    print(f"Preorder (рек.):  {list(preorder(tree))}")
    print(f"Inorder (рек.):   {list(inorder(tree))}")
    print(f"Postorder (рек.): {list(postorder(tree))}")
    print(f"BFS (ітер.):      {bfs_level_order(tree)}")
    print(f"DFS (ітер.):      {dfs_preorder_iter(tree)}\n")

    # 3. Мемоізація Фібоначчі
    fib.cache_clear()
    n_fib = 35
    val_memo = fib(n_fib)
    print(f"fib({n_fib}) = {val_memo} | {fib.cache_info()}")
    print(f"fib_iter({n_fib}) = {fib_iter(n_fib)}\n")

    # 4. Варіант 12: Порівняння продуктивності LCS
    s1 = "ABCBDABABCBDAB"
    s2 = "BDCABABDCABA"
    print(f"--- Варіант 12: LCS для '{s1}' та '{s2}' ---")

    t0 = time.perf_counter()
    res_naive = lcs_naive(s1, s2)
    t_naive = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    res_memo, cache_stats = lcs_memo(s1, s2)
    t_memo = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    res_iter = lcs_iter(s1, s2)
    t_iter = (time.perf_counter() - t0) * 1000

    print(f"Наївна рекурсія:   довжина = {res_naive}, час = {t_naive:.4f} мс")
    print(f"Мемоізація (LRU):  довжина = {res_memo}, час = {t_memo:.4f} мс | {cache_stats}")
    print(f"Ітеративний DP:    довжина = {res_iter}, час = {t_iter:.4f} мс")


if __name__ == "__main__":
    main()