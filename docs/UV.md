uv migration notes

This project was migrated to use `uv` as the project package manager.

Quick steps to reproduce locally:

1. Install uv (Homebrew on macOS):

   brew install uv

2. Initialize project (if you want to convert existing requirements):

   uv init

3. Import existing `requirements.txt`:

   uv add -r requirements.txt

4. Sync the project environment:

   uv sync

Run tests or tools via `uv run` to ensure they use the locked environment, e.g.:

   uv run ruff check

See `https://github.com/astral-sh/uv` for full docs.
