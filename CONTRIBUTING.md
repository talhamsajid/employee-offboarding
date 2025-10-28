# Contributing to Employee Offboarding Tool

First off, thank you for considering contributing to Employee Offboarding Tool! It's people like you that make this tool better for everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, command outputs)
- **Describe the behavior you observed** and what you expected
- **Include details about your environment** (OS, Python version, dependency versions)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the proposed feature
- **Explain why this enhancement would be useful**
- **List examples** of how it would be used

### Pull Requests

1. Fork the repository and create your branch from `main`
2. Make your changes following our coding standards
3. Test your changes thoroughly
4. Update documentation if needed
5. Submit a pull request

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/employee-offboarding.git
   cd employee-offboarding
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google API credentials**
   - Follow the README instructions for obtaining credentials
   - Place your `credentials.json` in the project root (never commit this!)

5. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Pull Request Process

1. **Update the README.md** with details of changes if applicable
2. **Ensure your code follows PEP 8** style guidelines
3. **Add docstrings** to new functions and classes
4. **Test your changes** with both dry-run and actual execution
5. **Update version numbers** if applicable
6. **The PR will be merged** once approved by a maintainer

### PR Checklist

- [ ] Code follows PEP 8 style guidelines
- [ ] All functions have docstrings
- [ ] Changes have been tested with dry-run mode
- [ ] Documentation has been updated
- [ ] No sensitive data is committed
- [ ] Commit messages are clear and descriptive

## Coding Standards

### Python Style Guide

We follow PEP 8 with these specifics:

- **Indentation**: 4 spaces (no tabs)
- **Line length**: Maximum 100 characters
- **Imports**: Grouped and sorted (stdlib, third-party, local)
- **Naming**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`

### Documentation

- **Docstrings**: Use Google-style docstrings
  ```python
  def function_name(param1, param2):
      """Brief description.
      
      Detailed description if needed.
      
      Args:
          param1 (type): Description.
          param2 (type): Description.
          
      Returns:
          type: Description.
          
      Raises:
          ExceptionType: When this happens.
      """
  ```

- **Comments**: Use inline comments sparingly, prefer self-documenting code
- **README updates**: Keep README in sync with code changes

### Security Guidelines

This is a security tool, so security is paramount:

- **Never commit credentials** (`credentials.json`, `token.json`, `.env`)
- **Validate all inputs** from users
- **Use try-except blocks** for API calls
- **Log security-relevant actions**
- **Test with dry-run mode** first
- **Preserve audit trails** in reports

## Testing Guidelines

### Manual Testing

Before submitting a PR:

1. **Test with dry-run mode**
   ```bash
   python main.py
   # Choose option 3 (Dry run)
   ```

2. **Test all report formats**
   - CSV
   - Excel
   - JSON

3. **Test cache functionality**
   ```bash
   python main.py --cache-info
   python main.py --refresh-cache
   python main.py --clear-cache
   ```

4. **Test error handling**
   - Invalid credentials
   - Network interruption
   - Invalid email addresses

### Test Coverage

While we don't have automated tests yet (contributions welcome!), please manually verify:

- Normal operation flow
- Edge cases (empty results, no permissions, etc.)
- Error conditions
- All command-line arguments

## Development Tips

### Debugging

- Enable verbose output by modifying log levels
- Use dry-run mode to test logic without making changes
- Check `reports/` directory for detailed output

### Common Pitfalls

- **API Rate Limits**: Add appropriate delays between API calls
- **Authentication**: Token may expire, test re-authentication
- **Permissions**: Some operations require admin privileges
- **Cache**: Remember to invalidate cache when testing changes

## Questions?

Feel free to open an issue with the `question` label if you have any questions about contributing!

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- Future CONTRIBUTORS.md file
- Release notes for significant contributions

Thank you for contributing to make employee offboarding safer and more efficient!
