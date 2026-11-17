from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering


@total_ordering
@dataclass(frozen=True)
class CourseRank:
    """Незмінна модель ранжованого онлайн-курсу з повним впорядкуванням."""

    title: str
    category: str
    students: int
    rating: float
    price: float

    def _sort_key(self) -> tuple[float, int, str]:
        return (self.rating, self.students, self.title)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CourseRank):
            return NotImplemented
        return self._sort_key() == other._sort_key()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, CourseRank):
            return NotImplemented
        return self._sort_key() < other._sort_key()