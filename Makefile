# Variables
PYTHON := poetry run python
POETRY := poetry
PACKAGE_NAME := llm_interviewer

# Default target
.DEFAULT_GOAL := help

# Help command
help:
	@echo "Available commands:"
	@echo "  make install        - Install all dependencies"
	@echo "  make update         - Update all dependencies"
	@echo "  make format         - Format code using black and isort"
	@echo "  make lint           - Run linting checks (flake8)"
	@echo "  make type-check     - Run type checking (mypy)"
	@echo "  make test           - Run tests"
	@echo "  make test-cov       - Run tests with coverage"
	@echo "  make clean          - Clean up cache files"
	@echo "  make setup          - Initial project setup"
	@echo "  make pre-commit     - Run pre-commit hooks on all files"

# Installation
install:
	$(POETRY) install

# Update dependencies
update:
	$(POETRY) update
	$(POETRY) export -f requirements.txt --output requirements.txt

# Code formatting
format:
	$(POETRY) run black src tests
	$(POETRY) run isort src tests

# Linting
lint:
	$(POETRY) run flake8 src tests

# Type checking
type-check:
	$(POETRY) run mypy src

# Testing
test:
	$(POETRY) run pytest tests/ -v

test-cov:
	$(POETRY) run pytest tests/ --cov=src/$(PACKAGE_NAME) --cov-report=term-missing

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete

# Initial setup
setup: install
	$(POETRY) run pre-commit install
	@echo "Creating .env file if it doesn't exist..."
	@test -f .env || touch .env
	@echo "Please add your OPENAI_API_KEY to the .env file"

# Run pre-commit hooks
pre-commit:
	$(POETRY) run pre-commit run --all-files

# Development environment setup
dev-setup: setup format lint type-check test

# Create new virtual environment and install dependencies
venv-setup:
	$(POETRY) env use python3.12
	$(POETRY) install

# Export requirements
export-reqs:
	$(POETRY) export -f requirements.txt --output requirements.txt
	$(POETRY) export -f requirements.txt --output requirements-dev.txt --with dev

# Check for outdated packages
check-updates:
	$(POETRY) show --outdated

# Run the application
run:
	$(POETRY) run python -m src.$(PACKAGE_NAME)

# Add new dependency
add-dep:
	@read -p "Enter package name: " package; \
	read -p "Is this a dev dependency? (y/n): " is_dev; \
	if [ "$$is_dev" = "y" ]; then \
		$(POETRY) add --group dev $$package; \
	else \
		$(POETRY) add $$package; \
	fi

# Remove dependency
rm-dep:
	@read -p "Enter package name: " package; \
	read -p "Is this a dev dependency? (y/n): " is_dev; \
	if [ "$$is_dev" = "y" ]; then \
		$(POETRY) remove --group dev $$package; \
	else \
		$(POETRY) remove $$package; \
	fi

.PHONY: help install update format lint type-check test test-cov clean setup pre-commit dev-setup venv-setup export-reqs check-updates run add-dep rm-dep
