# Makefile for Puls Events Culturs RAG POC
# Compatible with Windows (using PowerShell), Linux, and Mac

.PHONY: help install install-dev lint format test test-cov clean build-index run run-debug docker-build docker-run docker-stop

# Detect OS
ifeq ($(OS),Windows_NT)
	PYTHON := .venv/Scripts/python.exe
	PIP := .venv/Scripts/pip.exe
	PYTEST := .venv/Scripts/pytest.exe
	RUFF := .venv/Scripts/ruff.exe
	UVICORN := .venv/Scripts/uvicorn.exe
	RM := powershell -Command "Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
else
	PYTHON := .venv/bin/python
	PIP := .venv/bin/pip
	PYTEST := .venv/bin/pytest
	RUFF := .venv/bin/ruff
	UVICORN := .venv/bin/uvicorn
	RM := rm -rf
endif

help:
	@echo "=== Puls Events Culturs RAG - Make Commands ==="
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install production dependencies"
	@echo "  make install-dev    Install all dependencies (dev included)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           Run linting checks with ruff"
	@echo "  make format         Format code with ruff"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run all tests"
	@echo "  make test-cov       Run tests with coverage report"
	@echo ""
	@echo "Data & Index:"
	@echo "  make build-index    Build FAISS index from OpenAgenda"
	@echo ""
	@echo "Run:"
	@echo "  make run            Start FastAPI server"
	@echo "  make run-debug      Start FastAPI server with debug mode"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   Build Docker image"
	@echo "  make docker-run     Run Docker container"
	@echo "  make docker-stop    Stop Docker containers"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          Remove cache and build artifacts"
	@echo ""

install:
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e .

install-dev:
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e ".[dev]"

lint:
	$(RUFF) check .

format:
	$(RUFF) format .
	$(RUFF) check --fix .

test:
	$(PYTEST) tests -v

test-cov:
	$(PYTEST) tests -v --cov=src --cov=api --cov-report=term-missing --cov-report=html

build-index:
	$(PYTHON) scripts/build_index.py

run:
	$(UVICORN) api.main:app --host 0.0.0.0 --port 8000

run-debug:
	$(UVICORN) api.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

docker-build:
	docker build -t puls-events-rag:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

clean:
	$(RM) .pytest_cache
	$(RM) .ruff_cache
	$(RM) .mypy_cache
	$(RM) htmlcov
	$(RM) .coverage
	$(RM) dist
	$(RM) build
	$(RM) *.egg-info
	find . -type d -name __pycache__ -exec $(RM) {} +
	find . -type f -name "*.pyc" -delete
