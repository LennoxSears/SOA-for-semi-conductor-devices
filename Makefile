# Makefile for SOA Semiconductor Rules project

.PHONY: help install install-dev test lint format clean extract demo validate audit

help:  ## Show this help message
	@echo "SOA Semiconductor Rules - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install the project dependencies
	poetry install --no-dev

install-dev:  ## Install the project with development dependencies
	poetry install

test:  ## Run tests
	poetry run pytest tests/ -v

test-cov:  ## Run tests with coverage
	poetry run pytest tests/ -v --cov=src/soa_rules --cov-report=html --cov-report=term

lint:  ## Run linting checks
	poetry run flake8 src/ tests/
	poetry run mypy src/

format:  ## Format code with black
	poetry run black src/ tests/

format-check:  ## Check code formatting
	poetry run black --check src/ tests/

clean:  ## Clean up generated files
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

extract:  ## Extract SOA rules grouped by devices
	poetry run soa-extract

extract-all:  ## Extract all SOA rules (744 parameters)
	poetry run soa-extract-all

demo:  ## Run SOA DSL demonstration
	poetry run soa-demo

validate:  ## Validate extracted rules against Excel
	poetry run soa-validate

audit:  ## Audit extraction completeness
	poetry run soa-audit

build:  ## Build the package
	poetry build

publish:  ## Publish to PyPI (requires authentication)
	poetry publish

shell:  ## Open poetry shell
	poetry shell

env-info:  ## Show environment information
	poetry env info

deps-update:  ## Update dependencies
	poetry update

deps-show:  ## Show dependency tree
	poetry show --tree