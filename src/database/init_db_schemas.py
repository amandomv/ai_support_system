from pathlib import Path

# Get the directory where this file is located
SCHEMAS_DIR = Path(__file__).parent / "db_schemas"

# List of schema files in order of execution
SCHEMA_FILES = [
    "init_user.sql",
    "init_faq_documents.sql",
    # Add more schema files here in the order they should be executed
]


def get_schema_paths() -> list[Path]:
    """Get the full paths of schema files in the correct order."""
    return [SCHEMAS_DIR / schema_file for schema_file in SCHEMA_FILES]
