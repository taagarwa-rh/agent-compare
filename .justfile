_default:
    @ just --list

# Run recipes for MR approval
pre-mr: format lint test

# Formats Code
format:
    uv run ruff check --select I --fix src
    uv run ruff format src

# Lints Code
lint *options:
    uv run ruff check src {{ options }}

# Tests code
test *options:
    uv run pytest -s tests/ {{ options }}

# Build docs
build-docs:
    uv run mkdocs serve