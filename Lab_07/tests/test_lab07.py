from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from core import (
    build_course_ranking,
    filt,
    mapf,
    normalize_course,
    pipeline,
    total_enrolled_students,
)
from loaders import load_courses
from models import CourseRank


def test_pipeline_and_partial_combinators() -> None:
    numbers = [1, 2, 3, 4, 5]
    result = pipeline(
        numbers,
        filt(lambda x: x % 2 == 1),
        mapf(lambda x: x * 10),
        list,
    )
    assert result == [10, 30, 50]


def test_normalize_course_with_operator() -> None:
    raw = {
        "title": "   Functional Python   ",
        "category": "  pRoGrAmMiNg ",
        "students": "1500",
        "rating": "4.85",
        "price": "39.99",
    }
    normalized = normalize_course(raw)
    assert normalized == {
        "title": "Functional Python",
        "category": "Programming",
        "students": 1500,
        "rating": 4.85,
        "price": 39.99,
    }


def test_singledispatch_all_sources(tmp_path: Path) -> None:
    records = [
        {
            "title": "Course A",
            "category": "Programming",
            "students": 1000,
            "rating": 4.8,
            "price": 20.0,
        },
        {
            "title": "Course B",
            "category": "Design",
            "students": 500,
            "rating": 4.6,
            "price": 15.0,
        },
    ]
    json_str = json.dumps(records)
    json_file = tmp_path / "courses.json"
    json_file.write_text(json_str, encoding="utf-8")

    csv_file = tmp_path / "courses.csv"
    csv_file.write_text(
        "title,category,students,rating,price\n"
        "Course A,Programming,1000,4.8,20.0\n"
        "Course B,Design,500,4.6,15.0\n",
        encoding="utf-8",
    )

    from_str = load_courses(json_str)
    from_path_str = load_courses(str(json_file))
    from_path = load_courses(json_file)
    from_list = load_courses(records)
    from_csv = load_courses(csv_file)

    with json_file.open(encoding="utf-8") as f_json:
        from_json_stream = load_courses(f_json)

    with csv_file.open(encoding="utf-8", newline="") as f_csv:
        from_csv_stream = load_courses(f_csv)

    assert from_str == from_path_str == from_path == from_list == from_json_stream
    assert len(from_csv) == 2
    assert from_csv == from_csv_stream
    assert from_csv[0]["title"] == "Course A"

    stream_no_name = io.StringIO(json_str)
    assert load_courses(stream_no_name) == records


def test_singledispatch_invalid_types() -> None:
    with pytest.raises(TypeError):
        load_courses(12345)

    with pytest.raises(ValueError):
        load_courses([1, 2, 3])


def test_course_rank_total_ordering() -> None:
    c1 = CourseRank("Alpha", "Dev", 1000, 4.7, 30.0)
    c2 = CourseRank("Beta", "Dev", 1500, 4.7, 30.0)
    c3 = CourseRank("Gamma", "Dev", 500, 4.9, 50.0)
    c1_dup = CourseRank("Alpha", "Other", 1000, 4.7, 99.0)

    assert c1 == c1_dup
    assert not (c1 != c1_dup)
    assert c1 < c2 < c3
    assert c1 <= c1_dup <= c2
    assert c3 > c2 > c1
    assert c3 >= c2 >= c1_dup
    assert max([c1, c2, c3]) == c3
    assert sorted([c3, c1, c2]) == [c1, c2, c3]

    assert (c1 == "not a course") is False
    with pytest.raises(TypeError):
        _ = c1 < "not a course"


def test_build_course_ranking_and_reduce_total() -> None:
    raw_courses = [
        {"title": "  Python Pro ", "category": "dev", "students": "3000", "rating": "4.9", "price": "50"},
        {"title": "  Rust Core  ", "category": "dev", "students": "4500", "rating": "4.9", "price": "60"},
        {"title": "  Basic Web  ", "category": "dev", "students": "8000", "rating": "4.1", "price": "10"},
        {"title": "  Go Micro   ", "category": "dev", "students": "2000", "rating": "4.7", "price": "40"},
    ]

    ranked = build_course_ranking(raw_courses, min_rating=4.5, top_n=2)
    assert [c.title for c in ranked] == ["Rust Core", "Python Pro"]
    assert total_enrolled_students(ranked) == 7500