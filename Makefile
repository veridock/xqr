.PHONY: help
help:  ## Display this help message
	@echo "Please use 'make <target>' where <target> is one of"
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo

# Development
.PHONY: install
install:  ## Install the package in development mode
	@echo "Installing package in development mode..."
	pip install -e .[dev]

.PHONY: install-all
install-all:  ## Install with all optional dependencies
	@echo "Installing package with all optional dependencies..."
	pip install -e ".[dev,data]"

.PHONY: install-tools
install-tools:  ## Install development tools
	@echo "Installing development tools..."
	pip install -U pip setuptools wheel
	pip install -U black isort flake8 mypy pytest pytest-cov build twine

# Formatting and Linting
.PHONY: format
format:  ## Format code with black and isort
	@echo "Formatting code..."
	black src tests
	isort src tests

.PHONY: lint
lint:  ## Run linters (black, isort, flake8, mypy)
	@echo "Running linters..."
	black --check --diff src tests
	isort --check-only src tests
	flake8 src tests
	mypy src

# Testing
.PHONY: test
TEST_PATH=./tests
.PHONY: test
test:  ## Run tests
	@echo "Running tests..."
	pytest $(TEST_PATH) -v --cov=xqr --cov-report=term-missing --cov-report=xml:coverage.xml

.PHONY: test-cov
test-cov:  ## Run tests with coverage report
	@echo "Running tests with coverage..."
	pytest --cov=xqr --cov-report=html:htmlcov

.PHONY: test-all
test-all:  ## Run all tests with coverage and linting
	@echo "Running all tests with coverage and linting..."
	make lint
	make test
	make test-cov

# Documentation
.PHONY: docs
docs:  ## Generate documentation
	@echo "Generating documentation..."
	cd docs && $(MAKE) html

.PHONY: docs-serve
docs-serve: docs  ## Serve documentation locally
	@echo "Serving documentation at http://localhost:8000"
	python -m http.server --directory docs/_build/html 8000

# Build and Release
.PHONY: build
build:  ## Build source and wheel packages
	@echo "Building source and wheel packages..."
	python3 -m build

.PHONY: check-build
check-build:  ## Check the built package
	@echo "Checking built package..."
	twine check dist/*

.PHONY: publish-test
publish-test: build check-build  ## Upload to test PyPI
	@echo "Uploading to test PyPI..."
	twine upload --repository testpypi dist/*

.PHONY: publish
publish:  ## Upload to PyPI
	poetry version patch
	poetry build
	poetry publish

.PHONY: push
push:  ## Push code to remote repository
	@echo "Pushing to remote repository..."
	git push origin $(shell git rev-parse --abbrev-ref HEAD)
	git push --tags

# Cleanup
.PHONY: clean
clean:  ## Remove build artifacts, cache, and test artifacts
	@echo "Cleaning up..."
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ .coverage coverage.xml htmlcov/ .tox/ .cache/ .eggs/ .hypothesis/
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*~' -delete
	find . -type f -name '*.swp' -delete
	find . -type f -name '*.swo' -delete

# Virtual Environment
.PHONY: venv
venv:  ## Create a virtual environment
	@echo "Creating virtual environment..."
	python -m venv venv

.PHONY: activate
activate:  ## Activate the virtual environment
	@echo "Run 'source venv/bin/activate' to activate the virtual environment"

# Development Server
.PHONY: run
run:  ## Run the development server
	@echo "Starting development server..."
	python -m xqr

# Dependencies
.PHONY: deps-outdated
deps-outdated:  ## Check for outdated dependencies
	@echo "Checking for outdated dependencies..."
	pip list --outdated

.PHONY: deps-upgrade
deps-upgrade:  ## Upgrade all dependencies
	@echo "Upgrading all dependencies..."
	pip install --upgrade -r requirements.txt

# Git Hooks
.PHONY: install-hooks
install-hooks:  ## Install git hooks
	@echo "Installing git hooks..."
	echo '#!/bin/sh\nmake lint test' > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

# Docker
.PHONY: docker-build
docker-build:  ## Build Docker image
	@echo "Building Docker image..."
	docker build -t xqr .

.PHONY: docker-run
docker-run:  ## Run Docker container
	@echo "Running Docker container..."
	docker run -it --rm xqr

# Default target
.DEFAULT_GOAL := help
