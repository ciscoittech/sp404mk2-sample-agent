.PHONY: help install test test-unit test-integration test-e2e coverage lint format clean docker-build docker-up docker-down docker-logs docker-test docker-shell

help:
	@echo "Available commands:"
	@echo ""
	@echo "Development:"
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
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build    Build all Docker images"
	@echo "  make docker-up       Start all services"
	@echo "  make docker-down     Stop all services"
	@echo "  make docker-logs     View service logs"
	@echo "  make docker-test     Run tests in Docker"
	@echo "  make docker-shell    Shell into backend container"

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

# Docker commands
docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-test:
	docker compose run --rm test

docker-shell:
	docker compose exec backend bash

docker-clean:
	docker compose down -v
	docker system prune -f

docker-db-init:
	docker compose --profile init run --rm db-init

docker-dev:
	docker compose --profile dev up

docker-prod:
	docker compose --profile prod up -d

docker-e2e:
	docker compose run --rm e2e-tests