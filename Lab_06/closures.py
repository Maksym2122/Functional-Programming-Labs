"""Базові замикання (closures) зі збереженням стану та інʼєкцією залежностей."""

from collections.abc import Callable


def make_counter(start: int = 0) -> Callable[[], int]:
    """Повертає замикання-лічильник, що збільшує стан через nonlocal."""
    value = start

    def inc() -> int:
        nonlocal value
        value += 1
        return value

    return inc


def make_logger(prefix: str, sink: Callable[[str], None] = print) -> Callable[[str], None]:
    """Повертає функцію логування із захопленим префіксом та функцією виводу."""

    def log(msg: str) -> None:
        sink(f"[{prefix}] {msg}")

    return log


def make_unit_converter(
    scale: float,
    offset: float = 0.0,
    precision: int = 4,
) -> Callable[[float], float]:
    """Повертає чисту функцію лінійної конвертації величин із захопленими параметрами."""

    def convert(value: float) -> float:
        return round(value * scale + offset, precision)

    return convert