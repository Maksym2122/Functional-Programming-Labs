# Лабораторна робота №7: `functools` та `operator` (Варіант 12)

## Предметна область
Обробка та ранжування **навчальних онлайн-курсів** (`title`, `category`, `students`, `rating`, `price`) у функціональному стилі без мутації вхідних даних.

## Структура проєкту
- `models.py` — модель `CourseRank` із `@functools.total_ordering` (порівняння за `rating`, `students`, `title`).
- `loaders.py` — поліморфний API `load_courses` на базі `@functools.singledispatch` (підтримка JSON-рядків, шляхів `str`/`Path` до JSON і CSV, `io.TextIOBase`, `list`).
- `core.py` — функціональний конвеєр `pipeline` через `functools.reduce`, комбінатори `mapf`/`filt` на `functools.partial`, примітиви `operator` (`itemgetter`, `attrgetter`, `methodcaller`) та агрегація студентів.
- `main.py` — демонстраційний запуск конвеєра.
- `tests/test_lab07.py` — модульні тести `pytest`.

## Запуск та перевірка
```powershell
python main.py
pytest -v
mypy .
black --check .
ruff check .