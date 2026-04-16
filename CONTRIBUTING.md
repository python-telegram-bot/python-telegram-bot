# Contributing to python-telegram-bot-improved

Thanks for your interest in contributing! This guide covers setup, code style, and the PR process.

## Setup

1. **Fork** the repository and clone your fork.
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Code Style

- Follow **PEP 8** with a line length of 99 characters.
- Use **type hints** for all public APIs.
- Write **docstrings** in Google style for all public modules, classes, and functions.
- Run `ruff check .` and `ruff format .` before committing.

## Tests

- Run the test suite: `pytest`
- Write tests for new features and bug fixes.
- Aim for meaningful coverage — don't just chase numbers.

## Pull Request Process

1. Create a **feature branch** from `master` (e.g., `feature/my-feature`).
2. Make your changes with clear, atomic commits.
3. Ensure all tests pass and pre-commit hooks succeed.
4. Open a PR against `master` with a clear description of the change and motivation.
5. Address review feedback and keep the branch up to date with `master`.

## Reporting Issues

- Use GitHub Issues with clear reproduction steps.
- Include Python version, library version, and OS.

Thank you for contributing!