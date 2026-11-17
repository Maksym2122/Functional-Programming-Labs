from __future__ import annotations

from pathlib import Path

from core import build_course_ranking, total_enrolled_students
from loaders import load_courses


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    json_path = base_dir / "sample_data.json"
    csv_path = base_dir / "sample_data.csv"

    print("=== 1. Top-3 курси з JSON-файлу (рейтинг >= 4.6) ===")
    top_json = build_course_ranking(json_path, min_rating=4.6, top_n=3)
    for idx, course in enumerate(top_json, start=1):
        print(
            f"{idx}. {course.title} [{course.category}] — "
            f"rating={course.rating}, students={course.students}, price=${course.price}"
        )
    print(f"Загалом студентів у вибірці: {total_enrolled_students(top_json)}\n")

    print("=== 2. Top-2 курси з CSV-файлу у категорії Programming ===")
    top_csv = build_course_ranking(
        str(csv_path),
        min_rating=4.5,
        top_n=2,
        category="programming",
    )
    for idx, course in enumerate(top_csv, start=1):
        print(
            f"{idx}. {course.title} [{course.category}] — "
            f"rating={course.rating}, students={course.students}"
        )

    if len(top_json) >= 2:
        best, second = top_json[0], top_json[1]
        print(f"\nПеревірка @total_ordering: {best.title!r} > {second.title!r} -> {best > second}")

    with csv_path.open(encoding="utf-8", newline="") as stream:
        raw_from_stream = load_courses(stream)
    print(f"Завантажено записів через TextIOBase: {len(raw_from_stream)}")


if __name__ == "__main__":
    main()