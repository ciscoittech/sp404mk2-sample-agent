.PHONY: help install test test-unit test-integration test-e2e coverage lint format clean

help:
	@echo "Available commands:"
	@echo "  make install          Install all dependencies"
	@echo "  make test            Run all tests"
	@echo "  make test-unit       Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo "  make test-e2e        Run end-to-end tests only"
	@echo "  make coverage        Run tests with coverage report"
	@echo "  make lint            Run linting checks"
	@echo "  make format          Format code with black and isort"
	@echo "  make clean           Clean up generated files"
	@echo "  make pre-commit      Install pre-commit hooks"

install:
	pip install -r requirements.txt
	pip install -r requirements-test.txt
	pip install -e .

test:
	python run_tests.py

test-unit:
	python run_tests.py unit

test-integration:
	python run_tests.py integration

test-e2e:
	pytest tests/e2e/ -v

coverage:
	pytest --cov=src --cov-report=html --cov-report=term-missing

lint:
	flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503
	mypy src/ --ignore-missing-imports
	black --check src/ tests/
	isort --check-only src/ tests/

format:
	black src/ tests/ --line-length=100
	isort src/ tests/ --profile black --line-length=100

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -f .coverage
	rm -f coverage.xml
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info

pre-commit:
	pre-commit install
	pre-commit run --all-files