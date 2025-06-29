.PHONY: help install install-dev test test-coverage lint format type-check clean build publish examples run-server run-shell

# Default target
help:
	@echo "Universal File Editor - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install      - Install package with Poetry"
	@echo "  install-dev  - Install with development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  test         - Run test suite"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  lint         - Run linting (flake8)"
	@echo "  format       - Format code with black"
	@echo "  type-check   - Run mypy type checking"
	@echo ""
	@echo "Usage:"
	@echo "  examples     - Create example files"
	@echo "  run-server   - Start HTTP server on port 8080"
	@echo "  run-shell    - Start interactive shell"
	@echo ""
	@echo "Distribution:"
	@echo "  build        - Build package"
	@echo "  publish      - Publish to PyPI"
	@echo "  clean        - Clean build artifacts"

# Installation
install:
	poetry install --only=main

install-dev:
	poetry install
	poetry run pre-commit install

# Testing
test:
	poetry run pytest -v

test-cov:
	poetry run pytest --cov=file_editor --cov-report=term-missing --cov-report=html

test-watch:
	poetry run pytest-watch

# Code Quality
lint:
	poetry run flake8 file_editor/ tests/

format:
	poetry run black file_editor/ tests/

format-check:
	poetry run black --check file_editor/ tests/

type-check:
	poetry run mypy file_editor/

# All quality checks
check: format-check lint type-check test

# Usage Examples
examples:
	poetry run file-editor examples

run-server:
	poetry run file-editor server --port 8080

run-shell:
	poetry run file-editor shell

# Demo commands
demo-svg:
	poetry run file-editor examples
	poetry run file-editor load example.svg
	poetry run file-editor query "//text[@id='text1']"
	poetry run file-editor set "//text[@id='text1']" "Updated from Makefile!"
	poetry run file-editor save

demo-xml:
	poetry run file-editor examples
	poetry run file-editor load example.xml
	poetry run file-editor query "//record[@id='1']/name"
	poetry run file-editor list --xpath "//record"

# Development workflow
dev-setup: install-dev examples
	@echo "✅ Development environment ready!"
	@echo "Try: make demo-svg or make run-server"

# Build and Distribution
clean:
	rm -rf dist/ || true
	rm -rf build/ || true
	rm -rf *.egg-info/ || true
	rm -f .coverage || true
	rm -rf htmlcov/ || true
	rm -rf .pytest_cache/ || true
	rm -rf .mypy_cache/ || true
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

build: clean
	poetry build

publish: build
	poetry publish

publish-test: build
	poetry publish --repository testpypi

# Documentation
docs:
	@echo "📚 Documentation available at:"
	@echo "  README.md - Main documentation"
	@echo "  file_editor/ - Source code with docstrings"

# Docker targets (if needed in future)
docker-build:
	docker build -t universal-file-editor .

docker-run:
	docker run -p 8080:8080 universal-file-editor server

# Maintenance
update-deps:
	poetry update

security-check:
	poetry run safety check

# CI/CD helpers
ci-test: install-dev check

# Quick development cycle
dev: format type-check test
	@echo "✅ Development cycle complete!"

# Benchmark (if performance tests are added)
benchmark:
	poetry run python -m pytest tests/test_performance.py -v

# Package info
info:
	@echo "Package: universal-file-editor"
	@poetry version
	@echo "Python: $(shell python --version)"
	@echo "Poetry: $(shell poetry --version)"
	@echo "Dependencies:"
	@poetry show --tree
