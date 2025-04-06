#!/bin/bash

# Install development dependencies
pip install -r requirements-dev.txt

# Install package in development mode
pip install -e .

# Run tests with coverage
pytest 