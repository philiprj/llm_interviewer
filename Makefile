# Variables
PYTHON := poetry run python
POETRY := poetry
PACKAGE_NAME := llm_interviewer
STREAMLIT_PORT := 8501
STREAMLIT_HOST := localhost

# Default target
.DEFAULT_GOAL := help

# Help command
help:
	@echo "Available commands:"
	@echo ""
	@echo "🔧 Setup & Installation:"
	@echo "  make install        - Install dependencies (with lock)"
	@echo "  make install-dev    - Install with dev dependencies"
	@echo "  make setup          - Initial project setup"
	@echo "  make lock           - Lock dependencies"
	@echo "  make sync           - Sync dependencies with lock file"
	@echo ""
	@echo "📦 Dependency Management:"
	@echo "  make update         - Update all dependencies"
	@echo "  make add-dep        - Add new dependency interactively"
	@echo "  make rm-dep         - Remove dependency interactively"
	@echo "  make check-updates  - Check for outdated packages"
	@echo "  make export-reqs    - Export requirements files"
	@echo ""
	@echo "🚀 Development:"
	@echo "  make streamlit      - Launch Streamlit dashboard"
	@echo "  make streamlit-dev  - Launch Streamlit in dev mode"
	@echo "  make notebook       - Launch Jupyter notebook"
	@echo ""
	@echo "🧹 Code Quality:"
	@echo "  make format         - Format code (black + isort)"
	@echo "  make lint           - Run linting checks"
	@echo "  make type-check     - Run type checking"
	@echo "  make pre-commit     - Run pre-commit hooks"
	@echo "  make qa             - Run all quality checks"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test           - Run tests"
	@echo "  make test-cov       - Run tests with coverage"
	@echo "  make test-watch     - Run tests in watch mode"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo ""
	@echo "🧽 Cleanup:"
	@echo "  make clean          - Clean cache files"
	@echo "  make clean-all      - Deep clean including venv"

# Poetry Lock Management
lock:
	@echo "🔒 Locking dependencies..."
	$(POETRY) lock

# Installation with proper locking
install: lock
	@echo "📦 Installing dependencies..."
	$(POETRY) install


install-no-dev: lock
	@echo "📦 Installing with dev dependencies..."
	$(POETRY) install --only main

# Sync dependencies with lock file
sync:
	@echo "🔄 Syncing dependencies with lock file..."
	$(POETRY) install --sync

# Update dependencies
update:
	@echo "🔄 Updating dependencies..."
	$(POETRY) update
	$(POETRY) export -f requirements.txt --output requirements.txt --without-hashes

# Streamlit Dashboard Commands
streamlit:
	@echo "🚀 Starting Streamlit dashboard..."
	@echo "Dashboard will be available at: http://$(STREAMLIT_HOST):$(STREAMLIT_PORT)"
	$(POETRY) run streamlit run streamlit_app.py --server.port $(STREAMLIT_PORT) --server.address $(STREAMLIT_HOST)

streamlit-dev:
	@echo "🚀 Starting Streamlit in development mode..."
	@echo "Dashboard will be available at: http://$(STREAMLIT_HOST):$(STREAMLIT_PORT)"
	$(POETRY) run streamlit run streamlit_app.py \
		--server.port $(STREAMLIT_PORT) \
		--server.address $(STREAMLIT_HOST) \
		--server.runOnSave true \
		--server.fileWatcherType watchdog

streamlit-public:
	@echo "🌐 Starting Streamlit dashboard (public access)..."
	@echo "Dashboard will be available at: http://0.0.0.0:$(STREAMLIT_PORT)"
	$(POETRY) run streamlit run streamlit_app.py \
		--server.port $(STREAMLIT_PORT) \
		--server.address 0.0.0.0

# Notebook support
notebook:
	@echo "📓 Starting Jupyter notebook..."
	$(POETRY) run jupyter notebook

# Code formatting
format:
	@echo "🎨 Formatting code..."
	$(POETRY) run black src tests streamlit_app.py
	$(POETRY) run isort src tests streamlit_app.py

# Linting
lint:
	@echo "🔍 Running linting checks..."
	$(POETRY) run flake8 src tests streamlit_app.py

# Type checking
type-check:
	@echo "🔎 Running type checks..."
	$(POETRY) run mypy src streamlit_app.py

# Testing
test:
	@echo "🧪 Running tests..."
	$(POETRY) run pytest tests/ -v

test-cov:
	@echo "🧪 Running tests with coverage..."
	$(POETRY) run pytest tests/ --cov=src/$(PACKAGE_NAME) --cov-report=term-missing --cov-report=html

test-watch:
	@echo "🔄 Running tests in watch mode..."
	$(POETRY) run pytest-watch tests/ -- -v

# Quality assurance - run all checks
qa: format lint type-check test
	@echo "✅ All quality checks completed!"

# Clean up
clean:
	@echo "🧹 Cleaning up cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete

clean-all: clean
	@echo "🧹 Deep cleaning..."
	$(POETRY) env remove --all 2>/dev/null || true
	rm -rf .venv/

# Initial setup
setup: install-dev
	@echo "⚙️ Setting up development environment..."
	$(POETRY) run pre-commit install
	@echo "Creating .env file if it doesn't exist..."
	@test -f .env || touch .env
	@echo ""
	@echo "🎉 Setup complete!"
	@echo "📝 Please add your OPENAI_API_KEY to the .env file"

# Run pre-commit hooks
pre-commit:
	@echo "🪝 Running pre-commit hooks..."
	$(POETRY) run pre-commit run --all-files

# Development environment setup
dev-setup: setup qa
	@echo "🚀 Development environment ready!"

# Poetry environment management
venv-info:
	@echo "📍 Poetry virtual environment info:"
	$(POETRY) env info

venv-setup:
	@echo "🐍 Setting up virtual environment with Python 3.12..."
	$(POETRY) env use python3.12
	$(POETRY) install

# Export requirements
export-reqs:
	@echo "📋 Exporting requirements..."
	$(POETRY) export -f requirements.txt --output requirements.txt --without-hashes
	$(POETRY) export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes

# Check for outdated packages
check-updates:
	@echo "🔍 Checking for outdated packages..."
	$(POETRY) show --outdated

# Add new dependency
add-dep:
	@echo "📦 Adding new dependency..."
	@read -p "Enter package name: " package; \
	read -p "Is this a dev dependency? (y/n): " is_dev; \
	if [ "$$is_dev" = "y" ]; then \
		$(POETRY) add --group dev $$package; \
	else \
		$(POETRY) add $$package; \
	fi
	@echo "📋 Updating requirements..."
	@$(MAKE) export-reqs

# Remove dependency
rm-dep:
	@echo "🗑️ Removing dependency..."
	@read -p "Enter package name: " package; \
	read -p "Is this a dev dependency? (y/n): " is_dev; \
	if [ "$$is_dev" = "y" ]; then \
		$(POETRY) remove --group dev $$package; \
	else \
		$(POETRY) remove $$package; \
	fi
	@echo "📋 Updating requirements..."
	@$(MAKE) export-reqs

# Docker support (if needed)
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t $(PACKAGE_NAME) .

docker-run:
	@echo "🐳 Running Docker container..."
	docker run -p $(STREAMLIT_PORT):$(STREAMLIT_PORT) --env-file .env $(PACKAGE_NAME)

.PHONY: help install install-dev update format lint type-check test test-cov test-watch clean clean-all setup pre-commit dev-setup venv-setup venv-info export-reqs check-updates run add-dep rm-dep streamlit streamlit-dev streamlit-public notebook qa lock sync docker-build docker-run