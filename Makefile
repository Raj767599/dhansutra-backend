.PHONY: install run test lint format format-check typecheck migrate makemigrations seed ci clean

PYTHON ?= python

install:
	$(PYTHON) -m pip install -U pip
	$(PYTHON) -m pip install -e ".[dev]"

run:
	$(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff format .

format-check:
	$(PYTHON) -m ruff format --check .

typecheck:
	$(PYTHON) -m mypy .

ci:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .
	$(PYTHON) -m mypy .
	$(PYTHON) -m pytest --cov=app --cov-report=term-missing

migrate:
	$(PYTHON) -m alembic upgrade head

makemigrations:
	$(PYTHON) -m alembic revision --autogenerate -m "migration"

seed:
	$(PYTHON) scripts/seed.py

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache','.mypy_cache','.ruff_cache','__pycache__']]; [shutil.rmtree(str(p), ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')];"

