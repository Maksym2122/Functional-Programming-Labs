"""Демонстрація лабораторної роботи №6 (Варіант 12: Кешування конвертації даних)."""

from closures import make_counter, make_logger, make_unit_converter
from decorators import cached, count_calls, timed

log = make_logger("LAB06")
step_counter = make_counter(0)
celsius_to_fahrenheit = make_unit_converter(scale=1.8, offset=32.0, precision=2)


@timed("convert-batch", unit="ms", logger=log)
@cached(ttl=60.0)
@count_calls()
def convert_sensor_record(sensor_id: str, celsius: float) -> dict[str, str | float]:
    """Конвертує показник датчика з градусів Цельсія у Фаренгейти та Кельвіни."""
    fahrenheit = celsius_to_fahrenheit(celsius)
    kelvin = round(celsius + 273.15, 2)
    return {
        "sensor_id": sensor_id,
        "celsius": celsius,
        "fahrenheit": fahrenheit,
        "kelvin": kelvin,
    }


def main() -> None:
    """Точка входу для демонстрації замикань і декораторів."""
    log(f"Крок {step_counter()}: Перший виклик (cache miss)")
    print(convert_sensor_record("S-01", 25.0))

    log(f"Крок {step_counter()}: Повторний виклик (cache hit)")
    print(convert_sensor_record("S-01", 25.0))

    log(f"Крок {step_counter()}: Інший датчик (cache miss)")
    print(convert_sensor_record("S-02", 100.0))

    log(f"Статистика кешу: {convert_sensor_record.cache_stats()}")
    log(f"Фактичних обчислень функції: {convert_sensor_record.get_calls()}")

    removed = convert_sensor_record.cache_invalidate(lambda args, _: args[0] == "S-01")
    log(f"Інвалідовано записів для S-01: {removed}")

    log(f"Крок {step_counter()}: Виклик після інвалідації (cache miss)")
    print(convert_sensor_record("S-01", 25.0))
    log(f"Фінальна статистика кешу: {convert_sensor_record.cache_stats()}")


if __name__ == "__main__":
    main()