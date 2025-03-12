#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run tests with coverage
pytest --cov=app tests/ 