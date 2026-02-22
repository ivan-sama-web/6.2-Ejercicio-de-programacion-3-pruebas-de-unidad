# Hotel Reservation System

## Project Information

### 5.2 Ejercicio de programación 2 y análisis estático
A lightweight, JSON-backed hotel reservation system built entirely with
Python's standard library — **no external dependencies required**.

#### Tecnológico de Monterrey
#### Maestría en Inteligencia Artificial Aplicada
#### Pruebas de software y aseguramiento de la calidad
#### Profesor titular: Dr. Gerardo Padilla Zárate
#### Profesor asistente: Mtra. Viridiana Rodríguez González
#### Alumno: Iván Troy Santaella Martínez – A01120515

## Project Structure

```
project_root/
├── run_tests.py                    # Cross-platform test runner
├── setup.cfg                       # Linter/coverage configuration
├── README.md
├── reservation_system/
│   ├── __init__.py                 # Package exports
│   ├── cli.py                      # A single-prompt REPL with short commands
│   ├── models.py                   # Hotel, Customer, Reservation dataclasses
│   ├── managers.py                 # CRUD manager classes
│   ├── persistence.py              # JSON file read/write utilities
│   └── generate_sample_data.py     # Sample data generation script
└── tests/
    ├── __init__.py
    ├── test_models.py              # 36 tests for domain models
    ├── test_persistence.py         #  6 tests for JSON I/O
    ├── test_managers.py            # 45 tests for manager operations
    └── test_generate_sample_data.py#  2 tests for sample data generation
```

## Quick Start


### 1. Generate sample data

```bash
python -m reservation_system.generate_sample_data
```

### 2. Launch the CLI

```bash
python -m reservation_system.cli
```

Press **?** for help and **q** to quit the system.

## Running Tests

**All platforms — recommended method:**

```bash
python run_tests.py        # standard output
python run_tests.py -v     # verbose output
```

**Alternative (Linux / macOS):**

```bash
python -m unittest discover -s tests -t . -v
```

**With coverage** (requires `pip install coverage`):

```bash
python -m coverage run run_tests.py
python -m coverage report -m
```

**Coverage: 100% line coverage.**

## Linting

```bash
# Flake8 — 0 warnings
flake8 reservation_system/ tests/ --max-line-length=79

# Pylint — 10.00/10
pylint reservation_system/ tests/ --disable=C0103,R1732
```

The two disabled pylint checks are for `unittest`'s `setUp`/`tearDown`
naming convention (camelCase) and `TemporaryDirectory()` allocation that
is cleaned up in `tearDown`.

## Design Decisions

- **Dataclasses** for clean, immutable-style domain models with built-in
  `__init__`, `__eq__`, and `__repr__`.
- **Manager pattern** separates persistence logic from domain models.
- **Graceful error handling**: corrupt JSON files and invalid records are
  logged to the console and skipped — execution always continues.
- **No external dependencies**: uses only `json`, `os`, `uuid`,
  `dataclasses`, `datetime`, and `unittest`.
- **Room availability tracking**: creating/cancelling reservations
  automatically adjusts hotel room counts.

## Requirements

- Python 3.10+ (uses `X | Y` union type syntax)
