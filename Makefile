.PHONY: install test lint format typecheck verify clean vscode-install vscode-build vscode-test vscode-package

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

vscode-install:
	cd extensions/vscode && npm install

vscode-build:
	cd extensions/vscode && npm run build

vscode-test:
	cd extensions/vscode && npm test

vscode-package: vscode-build
	mkdir -p dist
	cd extensions/vscode && npx @vscode/vsce package --no-dependencies -o ../../dist/kubelings-vscode.vsix

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +

