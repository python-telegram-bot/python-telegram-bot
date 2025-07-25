This is a python project which is a wrapper for the Telegram Bot API. Please read the contributing
guidelines mentioned in .github/CONTRIBUTING.rst to know how to contribute to this project.

### Development Environment:

Your development environment is set up using `uv`, a tool for managing Python environments and dependencies.
Your environment has all extra dependencies and groups installed, on Python 3.13. Please continue using `uv` for managing your development environment,
and for any scripts or tools you need to run.

Some example commands on `uv`:
- `uv sync --all-extras --all-groups` to install all dependencies and groups required by the project.
- `uv run -p 3.14 --all-groups --all-extras tests/` to run tests on a specific Python version. Please use the `-p` flag often.
- `uv pip install <package>` to install a package in the current environment.

If uv is somehow not available, you can install it using `pip install uv`.

### Repository Structure:

The repository follows a standard structure for Python projects. Here are some key directories and files:

- `src/`: This directory contains the main source code for the project.
- `tests/`: This directory contains test cases for the project.
- `pyproject.toml`: This file contains the project metadata and dependencies.
- `.github/`: This directory contains GitHub-specific files, including workflows and issue templates.

### Pull Requests:

When you create a pull request, please also add the appropriate labels to it.
