# Contributing to qBittorrent Peer-IP Clustering & ProtonVPN Server Recommender

Thank you for considering contributing to this project! Here are some guidelines to help you get started.

## Getting Started

1. Fork the repository
1. Clone your fork: `git clone https://github.com/YOUR_USERNAME/qbScripts.git`
1. Create a virtual environment: `uv sync --dev`
1. Install pre-commit hooks: `pre-commit install`

## Development Workflow

### Branch Naming Conventions

Create descriptive branch names using these prefixes:

- `feat/` - For new features (e.g., `feat/add-custom-clustering`)
- `fix/` - For bug fixes (e.g., `fix/geolocation-timeout`)
- `docs/` - For documentation updates (e.g., `docs/update-readme`)
- `refactor/` - For code refactoring (e.g., `refactor/simplify-clustering`)
- `test/` - For test additions/updates (e.g., `test/add-vpn-data-tests`)
- `chore/` - For maintenance tasks (e.g., `chore/update-dependencies`)

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Types

- `feat:` - A new feature
- `fix:` - A bug fix
- `docs:` - Documentation only changes
- `style:` - Changes that don't affect code meaning (whitespace, formatting)
- `refactor:` - Code change that neither fixes a bug nor adds a feature
- `perf:` - Performance improvements
- `test:` - Adding or correcting tests
- `chore:` - Changes to build process or auxiliary tools

#### Examples

```bash
feat: add support for custom VPN server lists
fix: correct distance calculation in clustering
docs: update installation instructions
refactor: simplify peer fetching logic
test: add tests for map visualization
```

#### Breaking Changes

For breaking changes, add `!` after the type or include `BREAKING CHANGE:` in the footer:

```bash
feat!: change CLI argument structure

BREAKING CHANGE: --output renamed to --map
```

### Code Style

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check . --fix

# Format code
uv run ruff format .
```

### Testing

Write tests for all new features and bug fixes:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/qb_peer_vpn --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_peer_fetcher.py
```

#### Test Guidelines

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names
- Mock external dependencies (API calls, file I/O)
- Aim for high coverage (>80%)

### Pre-commit Hooks

Pre-commit hooks will automatically run before each commit:

- Ruff linting and formatting
- Commit message validation (commitlint)

If hooks fail, fix the issues and commit again.

### Pull Request Process

1. Create a feature branch from `main`
1. Make your changes following the guidelines above
1. Write/update tests for your changes
1. Update documentation if needed
1. Ensure all tests pass: `uv run pytest`
1. Ensure linting passes: `uv run ruff check .`
1. Push to your fork
1. Create a Pull Request

#### PR Title Format

Use the same format as commit messages:

```
feat: add dark mode support for maps
fix: resolve caching issue in geolocator
```

#### PR Description

Include:

- What changes were made
- Why the changes were necessary
- How to test the changes
- Related issues (if any)

### Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality
- **PATCH** version for backwards-compatible bug fixes

Version bumps are automated using commitizen based on commit messages.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the community
- Show empathy towards other contributors

## Questions?

Feel free to open an issue for:

- Bug reports
- Feature requests
- Questions about contributing
- Discussion of ideas

Thank you for contributing! 🎉
