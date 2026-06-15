# Contribution Guide

Thank you for your interest in contributing to RisePyMinder!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/4r13lx/RisePyMinder/RisePyMinder.git`
3. Create a branch for your change: `git checkout -b feature/my-change`

## Prepare Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

## Before Making a Commit

1. Run tests: `make test`
2. Format code: `make format`
3. Run linters: `make lint`
4. Verify types: `make mypy`

Or run everything at once:

```bash
make all
```

## Code Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where possible
- Write docstrings in Google format
- Keep lines <= 100 characters (configured in black)

## Tests

- Write tests for new functionality
- Minimum coverage should be 80%
- Use pytest as testing framework

Run tests with coverage:

```bash
make test-cov
```

## Commit Messages

Follow the format:

```
[TYPE] Brief description

More detailed description if necessary.

Fixes: #123 (if there's a related issue)
```

**Common types:**
- `[FEAT]` - New feature
- `[FIX]` - Bug fix
- `[DOCS]` - Documentation changes
- `[STYLE]` - Code formatting
- `[REFACTOR]` - Code reorganization
- `[TEST]` - Test changes
- `[CHORE]` - Configuration/dependency changes

## Pull Requests

1. Provide a clear description of the change
2. Include references to related issues
3. Make sure all tests pass
4. Wait for review before merging

## Report Bugs

Open an issue with:

1. Clear problem description
2. Steps to reproduce
3. Expected vs actual behavior
4. Your environment (Python, OS, etc.)

## Suggestions and Improvements

Enhancement suggestions are also welcome. Open an issue marked as "enhancement".

---

Thank you for contributing! 🎉
