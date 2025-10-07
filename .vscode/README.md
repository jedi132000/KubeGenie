# VS Code Configuration for KubeGenie

This directory contains VS Code configuration files for KubeGenie development.

## Files

### `settings.json`
Editor and workspace settings including:
- Python interpreter path (uses project's venv)
- Code formatting (Black, isort)
- Linting (flake8)
- File exclusions (cache, venv, etc.)
- Python testing configuration

### `launch.json`
Debug configurations for:
- **Backend**: FastAPI server with debugging
- **UI**: Gradio interface debugging  
- **Tests**: Run tests with debugger
- **CLI**: Command-line debugging
- **Full Stack**: Debug backend + UI together

Press `F5` to start debugging with the selected configuration.

### `tasks.json`
Automated tasks accessible via `Ctrl+Shift+P` → "Tasks: Run Task":
- Setup and dependency installation
- Start backend and UI services
- Docker operations
- Testing and coverage
- Code formatting and linting
- Kubernetes utilities

Press `Ctrl+Shift+B` to run the default build task (Full Stack).

### `extensions.json`
Recommended VS Code extensions for KubeGenie development:
- Python language support (Pylance)
- Python debugging
- Code formatting (Black, isort)
- Docker and Kubernetes tools
- Git tools (GitLens)
- Markdown support

VS Code will prompt you to install these when opening the project.

## Usage

### Quick Start
1. Open workspace: `code KubeGenie.code-workspace`
2. Install recommended extensions when prompted
3. Press `F5` to start debugging

### Documentation
- [Full IDE Setup Guide](../docs/LOCAL_IDE_SETUP.md)
- [Quick Reference](../docs/IDE_QUICK_REFERENCE.md)
- [Contributing Guide](../docs/CONTRIBUTING.md)

## Customization

These files are version controlled and shared with the team for consistency.
For personal settings, use VS Code's User Settings:
- `Ctrl+,` → User tab

Workspace settings (in these files) override user settings.
