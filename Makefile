.PHONY: install test lint format typecheck verify clean

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .
	ruff check --fix .

typecheck:
	pyright

verify: lint typecheck test

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
