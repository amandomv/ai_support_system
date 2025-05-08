# AI Support System

A Python project with modern development tools and configurations.

## Features

- Ruff for fast Python linting
- Pyright for static type checking
- Pre-commit hooks for code quality
- Black for code formatting
- isort for import sorting

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ai_support_system
```

2. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

## Development

The project uses several tools to maintain code quality:

- **Ruff**: Fast Python linter
- **Pyright**: Static type checker
- **Pre-commit**: Git hooks for code quality
- **Black**: Code formatter
- **isort**: Import sorter

All these tools are configured to run automatically on commit. The configuration files are:

- `pyproject.toml`: Contains configurations for Ruff, Pyright, Black, and isort
- `.pre-commit-config.yaml`: Defines pre-commit hooks

## Project Structure

```
ai_support_system/
├── src/               # Source code directory
├── requirements.txt   # Python dependencies
├── pyproject.toml    # Project configuration
├── .pre-commit-config.yaml  # Pre-commit hooks
└── install.sh        # Installation script
```

## Contributing

1. Make sure you have the pre-commit hooks installed:
```bash
pre-commit install
```

2. Create a new branch for your changes
3. Make your changes
4. Commit your changes (pre-commit hooks will run automatically)
5. Push your changes and create a pull request
