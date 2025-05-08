#!/bin/bash

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Create src directory if it doesn't exist
mkdir -p src

echo "Setup complete! Don't forget to activate the virtual environment with:"
echo "source venv/bin/activate"
