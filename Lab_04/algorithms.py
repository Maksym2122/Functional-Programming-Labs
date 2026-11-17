from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from functools import lru_cache
from random import choice
from typing import Generator, Optional


# ==========================================
# 1. ШВИДКЕ СОРТУВАННЯ (QUICKSORT)
# ==========================================
def quicksort(xs: list[int]) -> list[int]:
    """Чисте рекурсивне швидке сортування без мутації вхідного списку."""
    # База рекурсії: порожній або одноелементний список уже відсортований
    if len(xs) <= 1:
        return xs[:]

    # Випадковий pivot знижує ймовірність деградації до O(n^2)
    pivot = choice(xs)
    left = [x for x in xs if x < pivot]
    mid = [x for x in xs if x == pivot]
    right = [x for x in xs if x > pivot]

    # Рекурсивний крок
    return quicksort(left) + mid + quicksort(right)


# ==========================================
# 2. БІНАРНЕ ДЕРЕВО ТА ОБХОДИ
# ==========================================
@dataclass(slots=True, frozen=True)
class Node:
    """Незмінний вузол бінарного дерева."""

    key: int
    left: Optional[Node] = None
    right: Optional[Node] = None


def preorder(t: Optional[Node]) -> Generator[int, None, None]:
    """Рекурсивний прямий обхід дерева (Root -> Left -> Right)."""
    if t is None:
        return
    yield t.key
    yield from preorder(t.left)
    yield from preorder(t.right)


def inorder(t: Optional[Node]) -> Generator[int, None, None]:
    """Рекурсивний центрований обхід дерева (Left -> Root -> Right)."""
    if t is None:
        return
    yield from inorder(t.left)
    yield t.key
    yield from inorder(t.right)


def postorder(t: Optional[Node]) -> Generator[int, None, None]:
    """Рекурсивний зворотний обхід дерева (Left -> Right -> Root)."""
    if t is None:
        return
    yield from postorder(t.left)
    yield from postorder(t.right)
    yield t.key


def bfs_level_order(t: Optional[Node]) -> list[int]:
    """Ітеративний обхід у ширину (BFS) на базі черги. Безпечний для глибоких дерев."""
    if t is None:
        return []
    queue: deque[Node] = deque([t])
    out: list[int] = []
    while queue:
        node = queue.popleft()
        out.append(node.key)
        if node.left is not None:
            queue.append(node.left)
        if node.right is not None:
            queue.append(node.right)
    return out


def dfs_preorder_iter(t: Optional[Node]) -> list[int]:
    """Ітеративний прямий обхід у глибину (DFS) із власним стеком."""
    if t is None:
        return []
    stack: list[Node] = [t]
    out: list[int] = []
    while stack:
        node = stack.pop()
        out.append(node.key)
        # Спершу кладемо правий підвузол, щоб лівий обробився першим
        if node.right is not None:
            stack.append(node.right)
        if node.left is not None:
            stack.append(node.left)
    return out


# ==========================================
# 3. МЕМОІЗАЦІЯ: ЧИСЛА ФІБОНАЧЧІ
# ==========================================
@lru_cache(maxsize=None)
def fib(n: int) -> int:
    """Мемоізоване рекурсивне обчислення n-го числа Фібоначчі."""
    if n < 0:
        raise ValueError("n має бути невід'ємним цілим числом")
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def fib_iter(n: int) -> int:
    """Ітеративне обчислення n-го числа Фібоначчі за O(n) часу та O(1) пам'яті."""
    if n < 0:
        raise ValueError("n має бути невід'ємним цілим числом")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


# ==========================================
# 4. ВАРІАНТ 12: НАЙДОВША СПІЛЬНА ПІДПОСЛІДОВНІСТЬ (LCS)
# ==========================================
def lcs_naive(s1: str, s2: str) -> int:
    """Наївна рекурсія для обчислення довжини LCS (експоненційна складність)."""

    def _solve(i: int, j: int) -> int:
        # Базовий випадок: дійшли до кінця одного з рядків
        if i == len(s1) or j == len(s2):
            return 0
        # Рекурсивний крок
        if s1[i] == s2[j]:
            return 1 + _solve(i + 1, j + 1)
        return max(_solve(i + 1, j), _solve(i, j + 1))

    return _solve(0, 0)


def lcs_memo(s1: str, s2: str) -> tuple[int, str]:
    """
    Мемоізоване обчислення довжини LCS за станами індексів (i, j).
    Повертає кортеж (довжина LCS, рядок статистики cache_info).
    """

    @lru_cache(maxsize=None)
    def _solve(i: int, j: int) -> int:
        if i == len(s1) or j == len(s2):
            return 0
        if s1[i] == s2[j]:
            return 1 + _solve(i + 1, j + 1)
        return max(_solve(i + 1, j), _solve(i, j + 1))

    result = _solve(0, 0)
    info = str(_solve.cache_info())
    _solve.cache_clear()
    return result, info


def lcs_iter(s1: str, s2: str) -> int:
    """
    Ітеративний табличний алгоритм (Bottom-Up DP) для знаходження довжини LCS.
    Безпечний для довгих рядків, оскільки не використовує стек викликів.
    """
    n, m = len(s1), len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            if s1[i] == s2[j]:
                dp[i][j] = 1 + dp[i + 1][j + 1]
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])

    return dp[0][0]