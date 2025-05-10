#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Only proceed with git-related tasks if we're in a git repository
# if [ -d ".git" ]; then
#     # Install pre-commit hooks
#     pre-commit install
# else
#     echo "Not a git repository, skipping git-related tasks"
#     # Remove pre-commit from requirements if it exists
#     if grep -q "pre-commit" requirements.txt; then
#         pip uninstall -y pre-commit
#     fi
# fi

# Create src directory if it doesn't exist
mkdir -p src

# Create database if it doesn't exist
PGPASSWORD=${POSTGRES_PASSWORD:-postgres} psql -h ${POSTGRES_HOST:-localhost} -U ${POSTGRES_USER:-postgres} -tc "SELECT 1 FROM pg_database WHERE datname = '${POSTGRES_DB:-ai_support_system}'" | grep -q 1 || \
    PGPASSWORD=${POSTGRES_PASSWORD:-postgres} psql -h ${POSTGRES_HOST:-localhost} -U ${POSTGRES_USER:-postgres} -c "CREATE DATABASE ${POSTGRES_DB:-ai_support_system}"

# Initialize base data if INIT_BASE_DATA is true
echo "INIT_BASE_DATA value: $INIT_BASE_DATA"
if [ "$INIT_BASE_DATA" = "true" ]; then
    echo "Initializing base data..."
    python init_db.py
    python init_base_data.py
else
    echo "Skipping base data initialization"
fi

echo "Setup complete! Don't forget to activate the virtual environment with:"
echo "source .venv/bin/activate"

echo "Running app in port: $APP_PORT"
python main.py
