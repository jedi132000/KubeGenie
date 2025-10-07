# Local IDE Development Guide for KubeGenie

This guide helps you set up KubeGenie for local development in your IDE, with a focus on VS Code.

## 🚀 Quick Start

### 1. Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**: [Download Python](https://www.python.org/downloads/)
- **VS Code**: [Download VS Code](https://code.visualstudio.com/)
- **Docker & Docker Compose**: [Download Docker](https://www.docker.com/products/docker-desktop)
- **kubectl**: [Install kubectl](https://kubernetes.io/docs/tasks/tools/)
- **Git**: [Download Git](https://git-scm.com/downloads)

### 2. Clone and Open in VS Code

```bash
# Clone the repository
git clone https://github.com/jedi132000/KubeGenie.git
cd KubeGenie

# Open in VS Code
code .

# Or open the workspace file for better organization
code KubeGenie.code-workspace
```

### 3. Install Recommended Extensions

When you open the project in VS Code, you'll be prompted to install recommended extensions. Click **Install All** to get:

- Python
- Pylance (Python language server)
- Python Debugger
- Docker
- Kubernetes
- YAML support
- And more...

Or install manually by pressing `Ctrl+Shift+X` and searching for the extension names.

### 4. Set Up Development Environment

**Option A: Using VS Code Task (Recommended)**

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: `Tasks: Run Task`
3. Select: `Setup: Install All Dependencies`
4. Wait for the setup to complete

**Option B: Using Terminal**

```bash
# Run the setup script
chmod +x scripts/setup-dev.sh
./scripts/setup-dev.sh
```

### 5. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-proj-your-openai-api-key-here
```

**Important**: Make sure to set your OpenAI API key in the `.env` file for the AI features to work.

### 6. Start Development

**Option A: Using Debug Configurations (Best for Development)**

1. Press `F5` or go to Run and Debug panel (`Ctrl+Shift+D`)
2. Select one of these configurations:
   - **Full Stack: Backend + UI** - Starts both backend and UI with debugging
   - **Backend: FastAPI Server** - Just the backend API
   - **UI: Gradio Simple** - Just the UI

**Option B: Using VS Code Tasks**

1. Press `Ctrl+Shift+P`
2. Type: `Tasks: Run Task`
3. Select: `Full Stack: Start All Services`

**Option C: Using Terminal**

```bash
# Terminal 1: Start Backend
source venv/bin/activate
cd backend
python main.py

# Terminal 2: Start UI
source venv/bin/activate
cd ui
python simple_main.py
```

### 7. Access the Application

Once started, you can access:

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Gradio UI**: http://localhost:7875 (or the port shown in terminal)
- **Health Check**: http://localhost:8000/health

## 🛠️ VS Code Features

### Debug Configurations

The project includes several debug configurations (`.vscode/launch.json`):

#### Backend Debugging
- **Backend: FastAPI Server** - Debug the main FastAPI backend
- **Backend: FastAPI + Gradio** - Debug backend with integrated Gradio UI

#### UI Debugging
- **UI: Gradio Simple** - Debug the standalone Gradio UI

#### Testing
- **Tests: Backend Unit Tests** - Run all tests with debugging
- **Tests: Backend Single Test** - Debug a single test file

#### CLI
- **CLI: KubeGenie CLI** - Debug the command-line interface

#### Compound Configurations
- **Full Stack: Backend + UI** - Debug both backend and UI simultaneously

### How to Use Debug Configurations

1. Open the Run and Debug panel (`Ctrl+Shift+D`)
2. Select a configuration from the dropdown
3. Press `F5` or click the green play button
4. Set breakpoints by clicking left of line numbers
5. Use debug controls to step through code

### VS Code Tasks

Press `Ctrl+Shift+P` → `Tasks: Run Task` to access:

#### Setup Tasks
- `Setup: Install All Dependencies` - Complete setup
- `Setup: Create Virtual Environment` - Create venv only
- `Backend: Install Dependencies` - Install backend packages
- `UI: Install Dependencies` - Install UI packages

#### Development Tasks
- `Backend: Start Server` - Run backend in background
- `UI: Start Gradio` - Run UI in background
- `Full Stack: Start All Services` - Run both (default build task)

#### Docker Tasks
- `Docker: Start Services` - Start with docker-compose
- `Docker: Stop Services` - Stop all containers
- `Docker: View Logs` - Follow container logs

#### Testing Tasks
- `Tests: Run All Backend Tests` - Execute all tests
- `Tests: Run with Coverage` - Tests with coverage report

#### Linting Tasks
- `Lint: Run Black (Format)` - Auto-format Python code
- `Lint: Run Flake8` - Check code style
- `Lint: Run isort (Import Sorting)` - Organize imports

#### Kubernetes Tasks
- `Kubectl: Get Pods` - List all pods
- `Kubectl: Get Services` - List all services

#### Utility Tasks
- `Clean: Remove Cache Files` - Clean Python cache files

### Keyboard Shortcuts

- `F5` - Start debugging
- `Shift+F5` - Stop debugging
- `Ctrl+Shift+B` - Run default build task (Full Stack)
- `Ctrl+Shift+P` - Command palette
- `Ctrl+Shift+T` - Run tasks
- `Ctrl+`` ` - Toggle terminal
- `Ctrl+Shift+D` - Open debug panel

## 📁 Project Structure

```
KubeGenie/
├── .vscode/                    # VS Code configuration
│   ├── settings.json          # Editor settings
│   ├── launch.json            # Debug configurations
│   ├── tasks.json             # Task definitions
│   └── extensions.json        # Recommended extensions
├── backend/                    # FastAPI backend
│   ├── app/                   # Application code
│   ├── main.py               # Main entry point
│   └── requirements.txt      # Python dependencies
├── ui/                        # Gradio web interface
│   ├── simple_main.py        # Standalone UI
│   └── requirements.txt      # UI dependencies
├── cli/                       # Command-line interface
├── tests/                     # Test suites
├── docs/                      # Documentation
├── scripts/                   # Build and setup scripts
│   └── setup-dev.sh          # Development setup
├── .env.example              # Environment template
├── .gitignore               # Git ignore rules
└── KubeGenie.code-workspace # VS Code workspace file
```

## 🧪 Testing

### Running Tests in VS Code

**Method 1: Using Test Explorer**
1. Open the Testing panel (flask icon in sidebar)
2. Click the play button to run all tests
3. Or click individual test cases to run them

**Method 2: Using Debug Configuration**
1. Open the Run and Debug panel
2. Select "Tests: Backend Unit Tests"
3. Press F5

**Method 3: Using Terminal**
```bash
source venv/bin/activate
pytest tests/ -v
```

### Test with Coverage

```bash
# Run task: Tests: Run with Coverage
# Or in terminal:
source venv/bin/activate
pytest tests/ -v --cov=backend --cov-report=html
```

Then open `htmlcov/index.html` in your browser to view the coverage report.

## 🎨 Code Formatting

The project uses Black and isort for code formatting:

### Auto-format on Save
The VS Code settings are configured to auto-format Python files on save.

### Manual Formatting
```bash
# Format all Python files
source venv/bin/activate
black backend/ ui/ cli/ --line-length 100
isort backend/ ui/ cli/ --profile black
```

Or use VS Code tasks:
- `Lint: Run Black (Format)`
- `Lint: Run isort (Import Sorting)`

## 🐛 Debugging Tips

### Debugging Backend

1. Set breakpoints in your Python code
2. Start with "Backend: FastAPI Server" configuration
3. Make API requests to trigger breakpoints
4. Use debug console to inspect variables

### Debugging UI

1. Set breakpoints in UI code
2. Start with "UI: Gradio Simple" configuration
3. Interact with the UI to trigger breakpoints

### Debugging Full Stack

1. Use "Full Stack: Backend + UI" compound configuration
2. Debug both frontend and backend simultaneously
3. Switch between debug sessions using the CALL STACK panel

### Common Debugging Scenarios

**API not responding?**
- Check if backend is running on port 8000
- Verify `.env` file is configured
- Check logs in the terminal

**UI can't connect to backend?**
- Ensure backend is running first
- Check `KUBEGENIE_BACKEND_URL` environment variable
- Verify CORS settings in backend

**OpenAI features not working?**
- Verify `OPENAI_API_KEY` is set in `.env`
- Check API key is valid
- Review logs for API errors

## 🔄 Development Workflow

### Typical Development Session

1. **Start VS Code**: Open `KubeGenie.code-workspace`
2. **Activate Environment**: Terminal will auto-activate venv
3. **Start Services**: Press `Ctrl+Shift+B` for full stack
4. **Make Changes**: Edit code with auto-formatting on save
5. **Test Changes**: 
   - Set breakpoints
   - Press F5 to debug
   - Or run tests with Testing panel
6. **Commit**: Use Source Control panel (`Ctrl+Shift+G`)

### Hot Reload

Both backend and UI support hot reload:
- Backend: Uses `--reload` flag with uvicorn
- UI: Gradio auto-reloads on file changes

Just save your files and see changes immediately!

## 🐳 Docker Development

### Using Docker Compose

```bash
# Start all services with Docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Or use VS Code tasks:
- `Docker: Start Services`
- `Docker: View Logs`
- `Docker: Stop Services`

## 📊 Monitoring and Observability

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/api/docs
```

### Logs

Backend logs are displayed in the terminal when running in debug mode. Look for:
- INFO level: Normal operations
- WARNING: Potential issues
- ERROR: Problems that need attention

## 🔧 Troubleshooting

### Virtual Environment Issues

```bash
# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
pip install -r ui/requirements.txt
```

### Port Conflicts

If ports 8000 or 7875 are in use:

1. Kill existing processes:
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:7875 | xargs kill -9
```

2. Or change ports in `.env`:
```bash
API_PORT=8001
```

### Import Errors

Ensure PYTHONPATH is set correctly:
```bash
export PYTHONPATH="${PYTHONPATH}:${PWD}/backend:${PWD}/ui"
```

VS Code settings handle this automatically.

### Docker Issues

```bash
# Clean up Docker
docker-compose down -v
docker system prune -a

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

## 📚 Additional Resources

- [Contributing Guide](CONTRIBUTING.md)
- [API Documentation](http://localhost:8000/api/docs) (when running)
- [README](../README.md)
- [Python Debugging in VS Code](https://code.visualstudio.com/docs/python/debugging)
- [VS Code Tasks](https://code.visualstudio.com/docs/editor/tasks)

## 💡 Tips for Productivity

1. **Use the workspace file**: Open `KubeGenie.code-workspace` for better project organization
2. **Learn keyboard shortcuts**: They speed up development significantly
3. **Use compound debug configurations**: Debug backend + UI together
4. **Enable auto-save**: File → Auto Save for automatic file saving
5. **Use tasks**: Quick access to common operations
6. **Install GitHub Copilot**: AI-powered code completion
7. **Use split editor**: View multiple files side by side
8. **Terminal multiplexing**: Use VS Code's terminal splitting

## 🎯 Next Steps

Now that you have your IDE set up:

1. Read the [Contributing Guide](CONTRIBUTING.md)
2. Check out [open issues](https://github.com/jedi132000/KubeGenie/issues)
3. Join the community discussions
4. Start coding! 🚀

---

Happy coding! If you encounter any issues, please open an issue on GitHub.
