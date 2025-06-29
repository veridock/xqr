# Contributing to XQR

Thank you for considering contributing to XQR! We welcome all contributions, including bug reports, feature requests, documentation improvements, and code contributions.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
   ```bash
   git clone https://github.com/your-username/xqr.git
   cd xqr
   ```
3. **Set up** the development environment
   ```bash
   poetry install
   ```
4. **Create a branch** for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use type hints for all new code
- Keep lines under 100 characters
- Use docstrings for all public functions and classes

### Testing

1. Run the test suite:
   ```bash
   pytest
   ```
2. Ensure all tests pass before submitting a PR
3. Add tests for new features

### Documentation

- Update relevant documentation when adding new features
- Keep docstrings up to date
- Add examples for new functionality

## Submitting Changes

1. **Commit** your changes with a clear message:
   ```bash
   git commit -m "Add feature X"
   ```
2. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
3. Open a **Pull Request** on GitHub

## Issue Reporting

When reporting issues, please include:

1. Steps to reproduce the issue
2. Expected behavior
3. Actual behavior
4. Environment details (OS, Python version, etc.)
5. Any relevant error messages

## Code Review Process

1. A maintainer will review your PR
2. Address any feedback or requested changes
3. Once approved, your changes will be merged

## License

By contributing to XQR, you agree that your contributions will be licensed under the [MIT License](LICENSE).
