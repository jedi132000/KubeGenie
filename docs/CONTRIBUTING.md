# Contributing to KubeGenie

Thank you for your interest in contributing to KubeGenie! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

- Use the GitHub issue tracker to report bugs
- Include detailed information about your environment
- Provide steps to reproduce the issue
- Include relevant logs and error messages

### Feature Requests

- Submit feature requests as GitHub issues
- Clearly describe the use case and expected behavior
- Include mockups or examples if applicable

### Pull Requests

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation as needed
7. Submit a pull request

## 🛠️ Development Setup & Repo Hygiene

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- kubectl (for Kubernetes integration)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/kubegenie.git
   cd kubegenie
   ```

2. **Run setup script**
   ```bash
   chmod +x scripts/setup-dev.sh
   ./scripts/setup-dev.sh
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Run backend and UI**
   ```bash
   cd backend
   python main.py

   # In a separate terminal
   cd ../ui
   python simple_main.py
   ```

### Repo Hygiene

- Do not commit venv/, __pycache__, or log files.
- Keep only essential code, configs, and documentation.

### Documentation

- Update docs to reflect live cluster data, production readiness, and safety controls.
   source venv/bin/activate
   python main.py
   ```

5. **Run frontend**
   ```bash
   cd frontend
   npm start
   ```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration tests
cd tests
pytest integration/
```

## 📝 Coding Standards

### Python (Backend)

- Follow PEP 8 style guidelines
- Use type hints
- Write docstrings for all functions and classes
- Maximum line length: 100 characters
- Use `black` for code formatting
- Use `isort` for import sorting
- Use `mypy` for type checking

### TypeScript/React (Frontend)

- Follow TypeScript best practices
- Use functional components with hooks
- Use ESLint and Prettier for code formatting
- Write unit tests for components
- Use semantic HTML and accessibility best practices

### General Guidelines

- Write clear, self-documenting code
- Include comments for complex logic
- Follow single responsibility principle
- Use meaningful variable and function names
- Keep functions small and focused

## 🧪 Testing

### Backend Testing

- Unit tests for all business logic
- Integration tests for API endpoints
- Mock external dependencies (Kubernetes, databases)
- Test error handling and edge cases

### Frontend Testing

- Unit tests for components
- Integration tests for user workflows
- End-to-end tests for critical paths
- Accessibility testing

## 📚 Documentation

- Update README.md for significant changes
- Update API documentation for new endpoints
- Include code examples in documentation
- Keep changelog updated

## 🔒 Security

- Never commit secrets or credentials
- Use environment variables for configuration
- Follow secure coding practices
- Report security vulnerabilities privately

## 🎯 Git Workflow

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes
- `docs/description` - Documentation updates

### Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

Example:
```
feat(api): add Crossplane resource provisioning

Implements POST /api/v1/crossplane/resources endpoint
to provision cloud resources via Crossplane compositions.

Closes #123
```

## 📋 Code Review Process

1. All changes must be reviewed by at least one maintainer
2. CI/CD checks must pass
3. Tests must maintain or improve coverage
4. Documentation must be updated for user-facing changes

## 🆘 Getting Help

- Join our Discord server: [link]
- Check existing issues and discussions
- Tag maintainers for urgent issues
- Use draft PRs for early feedback

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

Thank you for contributing to KubeGenie! 🎉