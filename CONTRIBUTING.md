# Contributing to Algorepo

Algorepo is built to lower the barrier for anyone wanting to maintain their own algorithmic solutions repository. Our goal is to remove the friction of routine tasks—fetching statements, setting up boilerplate, and manual testing—so developers can focus on solving problems and sharing high-quality code.

We value contributions that sharpen this experience, whether by refining platform parsers or helping language experts make our runners more idiomatic and robust.

## Table of Contents
- [Getting Started](#getting-started)
- [Priority: Improving Runners](#priority-improving-runners)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Architecture & Extensions](#architecture--extensions)
- [Commit Guidelines](#commit-guidelines)
- [Security (Blue Team Perspective)](#security-blue-team-perspective)

---

## Getting Started

### 1. Prerequisites
- **Python 3.10+**
- **uv**: We use `uv` for lightning-fast dependency management.
  - [Install uv](https://github.com/astral-sh/uv) if you haven't already.

### 2. Local Setup
1. Fork and clone the repository.
2. Sync dependencies:
   ```bash
   uv sync
   ```
3. Install pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

## Priority: Improving Runners
As noted in the README, the highest-value contribution right now is improving our **language runners**. If you are experienced in one of the supported languages (C, C++, Rust, Go, etc.) and see a way to make its execution more idiomatic or handle complex data structures (like custom Trees/Graphs) better, please open a PR.

Check `src/algorepo/testers/runners/` to see the current implementations.

## Development Workflow

We prefer standards for code quality and consistency.

### Linting & Formatting
We use **Ruff** for both linting and formatting.
```bash
# Check for linting errors
uv run ruff check

# Format code
uv run ruff format
```

### Type Checking
We use **Pyright** for static type analysis. Ensure your changes pass strict type checking:
```bash
uv run pyright
```

### Testing
Write tests for every new feature or bug fix.
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=algorepo
```

## Coding Standards

- **Functional Style:** Prefer a functional approach. Use classes primarily for external interfaces and orchestrators.
- **Pure Functions:** Aim for functions without side effects or mutations of input arguments.
- **Strict Typing:** Explicit type hints are mandatory for all function signatures and variables. Avoid `Any`.
- **Data Validation:** Use **Pydantic v2** models for all structured data (see `src/algorepo/models.py`).
- **Simplicity:** Adhere to KISS (Keep It Simple, Stupid) and YAGNI (You Ain't Gonna Need It).

## Architecture & Extensions

Algorepo is designed to be extensible.

### Adding a New Platform
1. Create a new file in `src/algorepo/platforms/`.
2. Inherit from the `Platform` base class in `src/algorepo/platforms/base.py`.
3. Implement `fetch`, `parse`, `extract_test_cases`, and `get_filename`.

### Adding a New Language Runner
1. Create a new file in `src/algorepo/testers/runners/`.
2. Inherit from `BaseRunner` in `src/algorepo/testers/runners/base.py`.
3. Implement the `run` method (handling compilation and execution).
4. Update `src/algorepo/languages/languages.py` to register the new language.

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` for new features.
- `fix:` for bug fixes.
- `refactor:` for code changes that neither fix a bug nor add a feature.
- `chore:` for updating build tasks, package manager configs, etc.
- `docs:` for documentation changes.

Example: `feat: add support for HackerRank platform`

## Security

Always analyze your changes from a security standpoint:
- **No Code Injection:** Never use `eval()` or unsanitized shell execution for test runners. Use JSON marshaling and subprocess with argument lists.
- **Input Sanitization:** Sanitize problem titles and IDs before using them in file paths.
- **Credential Safety:** Ensure that sensitive tokens (like `leetcode_session`) are never logged or leaked.

---

## Pull Request Process

1. Create a new branch for your feature/fix.
2. Ensure all tests pass and there are no linting/typing errors.
3. Update documentation if necessary.
4. Submit the PR with a clear description of the changes and the problem they solve.
