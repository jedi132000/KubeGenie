# KubeGenie IDE Quick Reference

## 🚀 Quick Start Commands

```bash
# Complete setup
./scripts/ide-quickstart.sh

# Open in VS Code
code KubeGenie.code-workspace
```

## ⌨️ VS Code Keyboard Shortcuts

| Action | Shortcut | Description |
|--------|----------|-------------|
| **Start Debugging** | `F5` | Start debugging with selected configuration |
| **Stop Debugging** | `Shift+F5` | Stop current debug session |
| **Toggle Breakpoint** | `F9` | Add/remove breakpoint on current line |
| **Step Over** | `F10` | Step over current line (debugging) |
| **Step Into** | `F11` | Step into function (debugging) |
| **Step Out** | `Shift+F11` | Step out of current function |
| **Build Task** | `Ctrl+Shift+B` | Run default build task (Full Stack) |
| **Run Task** | `Ctrl+Shift+P` → Tasks | Show all available tasks |
| **Command Palette** | `Ctrl+Shift+P` | Show all commands |
| **Quick Open** | `Ctrl+P` | Quick file navigation |
| **Toggle Terminal** | `Ctrl+`` ` | Show/hide integrated terminal |
| **New Terminal** | `Ctrl+Shift+`` ` | Create new terminal instance |
| **Debug Console** | `Ctrl+Shift+Y` | Show debug console |
| **Problems Panel** | `Ctrl+Shift+M` | Show errors and warnings |
| **Source Control** | `Ctrl+Shift+G` | Show git changes |
| **Run Tests** | Testing panel | Run/debug tests |

## 🐛 Debug Configurations

Select from Run and Debug panel (`Ctrl+Shift+D`):

### Single Service
- **Backend: FastAPI Server** - Debug backend API only
- **Backend: FastAPI + Gradio** - Backend with integrated UI
- **UI: Gradio Simple** - Debug standalone UI

### Testing
- **Tests: Backend Unit Tests** - Debug all tests
- **Tests: Backend Single Test** - Debug current test file

### Full Stack
- **Full Stack: Backend + UI** - Debug both services simultaneously

### CLI
- **CLI: KubeGenie CLI** - Debug command-line interface
- **Python: Current File** - Debug any Python file

## 🛠️ VS Code Tasks

Press `Ctrl+Shift+P` → `Tasks: Run Task`:

### Setup & Installation
```
Setup: Install All Dependencies
Setup: Create Virtual Environment
Backend: Install Dependencies
UI: Install Dependencies
```

### Development
```
Backend: Start Server
UI: Start Gradio
Full Stack: Start All Services ← Default (Ctrl+Shift+B)
```

### Docker
```
Docker: Start Services
Docker: Stop Services
Docker: View Logs
```

### Testing
```
Tests: Run All Backend Tests
Tests: Run with Coverage
```

### Code Quality
```
Lint: Run Black (Format)
Lint: Run Flake8
Lint: Run isort (Import Sorting)
```

### Kubernetes
```
Kubectl: Get Pods
Kubectl: Get Services
```

### Utilities
```
Clean: Remove Cache Files
```

## 📁 Project Navigation

### Workspace Folders
- **KubeGenie** - Root project folder
- **Backend** - FastAPI backend service
- **UI** - Gradio web interface
- **CLI** - Command-line interface
- **Tests** - Test suites
- **Documentation** - Project docs

### Key Files
```
.vscode/
├── settings.json       # Editor configuration
├── launch.json         # Debug configurations
├── tasks.json          # Task definitions
└── extensions.json     # Recommended extensions

backend/
├── main.py            # FastAPI entry point
├── main_gradio.py     # FastAPI + Gradio
└── app/               # Application code

ui/
├── simple_main.py     # Standalone UI
└── requirements.txt   # UI dependencies

.env                   # Environment configuration
.env.example          # Environment template
```

## 🎯 Common Workflows

### Start Development Session
1. Open workspace: `code KubeGenie.code-workspace`
2. Press `F5`
3. Select "Full Stack: Backend + UI"
4. Set breakpoints and debug!

### Run Tests
1. Open Testing panel (beaker icon)
2. Click "Run All Tests"
3. Or press `F5` → "Tests: Backend Unit Tests"

### Format Code
- Save file - auto-formats with Black
- Or run task: "Lint: Run Black (Format)"

### View API Documentation
- Start backend
- Visit: http://localhost:8000/api/docs

### Quick Terminal Commands
```bash
# Activate venv (done automatically by VS Code)
source venv/bin/activate

# Start backend
cd backend && python main.py

# Start UI
cd ui && python simple_main.py

# Run tests
pytest tests/ -v

# Format code
black backend/ ui/ cli/ --line-length 100
```

## 🔧 Troubleshooting

### Virtual Environment Not Detected
```bash
# In VS Code:
Ctrl+Shift+P → Python: Select Interpreter
# Choose: ./venv/bin/python
```

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 7875
lsof -ti:7875 | xargs kill -9
```

### Import Errors
```bash
# Check PYTHONPATH (set in .vscode/settings.json)
echo $PYTHONPATH

# Or manually set:
export PYTHONPATH="${PWD}/backend:${PWD}/ui"
```

### Dependencies Issues
```bash
# Reinstall all dependencies
./scripts/ide-quickstart.sh

# Or manually:
source venv/bin/activate
pip install -r backend/requirements.txt
pip install -r ui/requirements.txt
```

### Configuration Not Loading
```bash
# Ensure .env exists
cp .env.example .env

# Edit and add your OPENAI_API_KEY
```

## 📊 Debugging Tips

### Set Breakpoints
- Click left of line number (red dot appears)
- Or press `F9` on the line

### Inspect Variables
- Hover over variables while debugging
- Check "Variables" panel in debug sidebar
- Use "Watch" panel for custom expressions

### Debug Console
- Press `Ctrl+Shift+Y`
- Execute Python expressions during debugging
- Example: `print(variable_name)`

### Conditional Breakpoints
- Right-click breakpoint → "Edit Breakpoint"
- Add condition: `variable == "value"`

### Logpoints
- Right-click line → "Add Logpoint"
- Add message to log without stopping execution

## 🌐 URLs to Bookmark

| Service | URL | Description |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | FastAPI backend |
| API Docs | http://localhost:8000/api/docs | Swagger UI |
| ReDoc | http://localhost:8000/api/redoc | Alternative docs |
| Health Check | http://localhost:8000/health | Service health |
| Gradio UI | http://localhost:7875 | Web interface |

## 📚 Documentation Links

- [Full IDE Setup Guide](LOCAL_IDE_SETUP.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [README](../README.md)

## 💡 Pro Tips

1. **Use workspace file**: Open `KubeGenie.code-workspace` for best experience
2. **Install GitHub Copilot**: AI-powered code completion
3. **Enable auto-save**: File → Auto Save
4. **Use split editor**: Drag file tabs to split view
5. **Terminal multiplexing**: Split terminal with `+` icon
6. **Multi-cursor editing**: Alt+Click or Ctrl+Alt+↑/↓
7. **Zen mode**: View → Appearance → Zen Mode (Ctrl+K Z)
8. **Minimap navigation**: Right side shows code overview

---

**Quick Help**: Press `Ctrl+Shift+P` → "Help: Show All Commands"
