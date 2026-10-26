BASE_PYTHON = python3.12
VENV = .venv
VENV_PYTHON = $(VENV)/bin/python
.PHONY: install run debug clean lint lint-strict test build check
install:
	$(BASE_PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -e .
	$(VENV_PYTHON) -m pip install -r requirements-dev.txt
run:
	$(BASE_PYTHON) a_maze_ing.py config.txt
debug:
	$(BASE_PYTHON) -m pdb a_maze_ing.py config.txt
clean:
	rm -rf __pycache__ display/__pycache__ mazegen/__pycache__ parsing/__pycache__ tests/__pycache__ .mypy_cache .pytest_cache build dist maze.txt *.egg-info
lint:
	$(VENV)/bin/flake8 . --exclude .venv,build,dist
	$(VENV)/bin/mypy . --exclude '(^\.venv/|^build/|^dist/)' --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
lint-strict:
	$(VENV)/bin/flake8 . --exclude .venv,build,dist
	$(VENV)/bin/mypy . --exclude '(^\.venv/|^build/|^dist/)' --strict
test:
	$(VENV_PYTHON) -m pytest tests
build:
	$(VENV_PYTHON) -m pip wheel . --no-deps --wheel-dir .
check: lint lint-strict test build
