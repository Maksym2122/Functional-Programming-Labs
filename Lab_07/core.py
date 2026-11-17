from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from functools import partial, reduce
from operator import add, attrgetter, itemgetter, methodcaller
from typing import Any, TypeVar

from loaders import load_courses
from models import CourseRank

T = TypeVar("T")
U = TypeVar("U")

_get_title = itemgetter("title")
_get_category = itemgetter("category")
_get_students = itemgetter("students")
_get_rating = itemgetter("rating")
_get_price = itemgetter("price")

_strip = methodcaller("strip")
_title_case = methodcaller("title")


def pipeline(value: Any, *funcs: Callable[[Any], Any]) -> Any:
    """Послідовно пропускає значення крізь ланцюжок функцій."""
    return reduce(lambda acc, fn: fn(acc), funcs, value)


def mapf(fn: Callable[[T], U]) -> Callable[[Iterable[T]], Iterator[U]]:
    """Частково застосований map для використання у конвеєрі."""
    return partial(map, fn)


def filt(pred: Callable[[T], bool]) -> Callable[[Iterable[T]], Iterator[T]]:
    """Частково застосований filter для використання у конвеєрі."""
    return partial(filter, pred)


def take_top(n: int, items: Iterable[T]) -> list[T]:
    """Повертає перші n елементів послідовності."""
    return list(items)[:n]


def normalize_course(raw: dict[str, Any]) -> dict[str, Any]:
    """Очищує рядкові поля та приводить числові характеристики курсу до потрібних типів."""
    clean_title = _strip(str(_get_title(raw)))
    clean_category = _title_case(_strip(str(_get_category(raw))))
    return {
        "title": clean_title,
        "category": clean_category,
        "students": int(_get_students(raw)),
        "rating": float(_get_rating(raw)),
        "price": float(_get_price(raw)),
    }


def has_min_rating(min_rating: float, course: dict[str, Any]) -> bool:
    """Предикат перевірки мінімального рейтингу курсу."""
    return float(_get_rating(course)) >= min_rating


def has_category(category: str, course: dict[str, Any]) -> bool:
    """Предикат перевірки категорії курсу."""
    return str(_get_category(course)).lower() == category.strip().lower()


def to_course_rank(course: dict[str, Any]) -> CourseRank:
    """Перетворює нормалізований словник у модель CourseRank."""
    return CourseRank(
        title=str(_get_title(course)),
        category=str(_get_category(course)),
        students=int(_get_students(course)),
        rating=float(_get_rating(course)),
        price=float(_get_price(course)),
    )


def sort_courses_desc(courses: Iterable[CourseRank]) -> list[CourseRank]:
    """Сортує курси за спаданням рейтингу та студентів, і за зростанням назви."""
    by_title_asc = sorted(courses, key=attrgetter("title"))
    return sorted(
        by_title_asc,
        key=attrgetter("rating", "students"),
        reverse=True,
    )


def build_course_ranking(
    source: Any,
    min_rating: float = 4.5,
    top_n: int = 3,
    category: str | None = None,
) -> list[CourseRank]:
    """Повний конвеєр: завантаження -> очищення -> фільтрація -> модель -> сортування -> Top-N."""
    steps: list[Callable[[Any], Any]] = [
        load_courses,
        mapf(normalize_course),
        filt(partial(has_min_rating, min_rating)),
    ]
    if category is not None:
        steps.append(filt(partial(has_category, category)))

    steps.extend(
        [
            mapf(to_course_rank),
            sort_courses_desc,
            partial(take_top, top_n),
        ]
    )
    return list(pipeline(source, *steps))


def total_enrolled_students(courses: Iterable[CourseRank]) -> int:
    """Обчислює сумарну кількість студентів через reduce та operator.add."""
    student_counts = map(attrgetter("students"), courses)
    return reduce(add, student_counts, 0)