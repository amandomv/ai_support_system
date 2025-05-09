#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install development requirements
pip install -r requirements-dev.txt

# Install pre-commit hooks if in a git repository
if [ -d ".git" ]; then
    pre-commit install
else
    echo "Not a git repository, skipping pre-commit installation"
fi

echo "Development setup complete! Don't forget to activate the virtual environment with:"
echo "source .venv/bin/activate"
