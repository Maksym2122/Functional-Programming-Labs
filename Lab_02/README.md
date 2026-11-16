# Лабораторна робота №2 — Функції вищого порядку, `lambda`, композиція

**Варіант 12:** Мобільні абоненти (`id`, `name`, `tariff`, `payments`).

## Структура проєкту
- `main.py` — єдина точка входу в застосунок.
- `core.py` — чисті функції трансформації без мутацій, композиція (`compose`, `pipe`, `juxt`) та `reduce`-агрегація.
- `app.py` — CLI-інтерфейс та читання вхідних даних.
- `tests/test_core.py` — модульні тести `pytest`.
- `report/` — звіт з лабораторної роботи у форматі PDF.

## Встановлення та запуск

Перейдіть у папку `Lab_02`:
```bash
cd Lab_02
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt