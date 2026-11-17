from __future__ import annotations

import csv
from functools import singledispatch
import io
import json
from pathlib import Path
from typing import Any


def _parse_csv_stream(stream: io.TextIOBase) -> list[dict[str, Any]]:
    reader = csv.DictReader(stream)
    return [dict(row) for row in reader]


def _parse_json_data(raw_data: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_data, list) or any(
        not isinstance(item, dict) for item in raw_data
    ):
        raise ValueError("JSON джерело повинно містити список словників")
    return raw_data


@singledispatch
def load_courses(src: Any) -> list[dict[str, Any]]:
    """Поліморфний завантажувач записів курсів із різних джерел."""
    raise TypeError(f"Непідтримуваний тип джерела: {type(src)!r}")


@load_courses.register
def _(src: str) -> list[dict[str, Any]]:
    stripped = src.strip()
    if stripped.startswith("["):
        return _parse_json_data(json.loads(stripped))
    return load_courses(Path(src))


@load_courses.register
def _(src: Path) -> list[dict[str, Any]]:
    suffix = src.suffix.lower()
    if suffix == ".csv":
        with src.open(mode="r", encoding="utf-8", newline="") as file_obj:
            return _parse_csv_stream(file_obj)
    if suffix == ".json":
        content = src.read_text(encoding="utf-8")
        return _parse_json_data(json.loads(content))
    raise ValueError(f"Непідтримуване розширення файлу: {src.suffix!r}")


@load_courses.register
def _(src: io.TextIOBase) -> list[dict[str, Any]]:
    file_name = getattr(src, "name", "")
    if isinstance(file_name, str) and file_name.lower().endswith(".csv"):
        return _parse_csv_stream(src)

    content = src.read()
    stripped = content.strip()
    if not stripped:
        return []
    if stripped.startswith("["):
        return _parse_json_data(json.loads(stripped))
    return _parse_csv_stream(io.StringIO(content))


@load_courses.register
def _(src: list) -> list[dict[str, Any]]:
    if any(not isinstance(item, dict) for item in src):
        raise ValueError("Очікувався список словників (list[dict])")
    return [dict(item) for item in src]