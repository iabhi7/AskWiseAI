.PHONY: install run test lint format docker-build docker-run clean

# Installation
install:
	pip install -e .

# Run the application
run:
	uvicorn app.main:app --reload

# Testing
test:
	pytest

# Linting and formatting
lint:
	flake8 app tests
	black --check app tests
	isort --check-only app tests

format:
	black app tests
	isort app tests

# Docker commands
docker-build:
	docker build -t askwiseai .

docker-run:
	docker run -p 8000:8000 --env-file .env askwiseai

# Clean up
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf *.egg-info
	rm -rf dist
	rm -rf build 