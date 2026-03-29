# Contributing to OpenLlama

Thank you for your interest in contributing to OpenLlama!

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Create a detailed bug report including:
   - Python version
   - Operating system
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages/logs

### Suggesting Features

1. Open an issue describing the feature
2. Explain the use case
3. Provide examples if possible

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass: `pytest open_llama/tests/ -v`
6. Commit with clear messages
7. Push to your fork
8. Submit a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/open_llama.git
cd open_llama

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -e .
pip install pytest

# Run tests
pytest open_llama/tests/ -v
```

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to public functions
- Keep functions focused and small

## Testing

All new features should include tests. Run the test suite:

```bash
pytest open_llama/tests/ -v
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
