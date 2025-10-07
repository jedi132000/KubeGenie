# 📋 Local IDE Setup Checklist

Use this checklist to ensure your local development environment is properly configured.

## ✅ Initial Setup

- [ ] **Install Prerequisites**
  - [ ] Python 3.11 or higher installed (`python3 --version`)
  - [ ] VS Code installed ([Download](https://code.visualstudio.com/))
  - [ ] Docker installed (optional) (`docker --version`)
  - [ ] kubectl installed (optional) (`kubectl version --client`)
  - [ ] Git installed (`git --version`)

- [ ] **Clone Repository**
  ```bash
  git clone https://github.com/jedi132000/KubeGenie.git
  cd KubeGenie
  ```

- [ ] **Run Quick Start Script**
  ```bash
  chmod +x scripts/ide-quickstart.sh
  ./scripts/ide-quickstart.sh
  ```
  - [ ] Virtual environment created (`venv/` directory exists)
  - [ ] Dependencies installed (no errors in output)
  - [ ] `.env` file created

- [ ] **Configure Environment**
  - [ ] Open `.env` file
  - [ ] Add your OpenAI API key: `OPENAI_API_KEY=sk-proj-...`
  - [ ] Save the file

## ✅ VS Code Setup

- [ ] **Open in VS Code**
  ```bash
  code KubeGenie.code-workspace
  ```
  Or: `File → Open Workspace from File → KubeGenie.code-workspace`

- [ ] **Install Extensions**
  - [ ] Click "Install All" when prompted for recommended extensions
  - [ ] Or manually install from Extensions panel (`Ctrl+Shift+X`):
    - [ ] Python (Microsoft)
    - [ ] Pylance
    - [ ] Python Debugger
    - [ ] Black Formatter
    - [ ] isort
    - [ ] Docker (optional)
    - [ ] Kubernetes (optional)

- [ ] **Select Python Interpreter**
  - [ ] Press `Ctrl+Shift+P`
  - [ ] Type "Python: Select Interpreter"
  - [ ] Choose `./venv/bin/python` or `Python 3.11.x ('venv')`
  - [ ] Verify interpreter shown in bottom-left status bar

- [ ] **Verify Configuration**
  - [ ] Open a Python file (e.g., `backend/main.py`)
  - [ ] Check for syntax highlighting
  - [ ] Check for IntelliSense (auto-complete)
  - [ ] Check for import suggestions

## ✅ Test Development Environment

- [ ] **Test Backend**
  - [ ] Press `F5`
  - [ ] Select "Backend: FastAPI Server"
  - [ ] Wait for "Application startup complete" message
  - [ ] Open browser to http://localhost:8000
  - [ ] Check http://localhost:8000/health returns `{"status": "healthy"}`
  - [ ] Open http://localhost:8000/api/docs - Swagger UI should load
  - [ ] Stop debugging (`Shift+F5`)

- [ ] **Test UI**
  - [ ] Press `F5`
  - [ ] Select "UI: Gradio Simple"
  - [ ] Wait for "Running on local URL" message
  - [ ] Open browser to http://localhost:7875
  - [ ] UI should load
  - [ ] Stop debugging (`Shift+F5`)

- [ ] **Test Full Stack**
  - [ ] Press `F5`
  - [ ] Select "Full Stack: Backend + UI"
  - [ ] Both services should start
  - [ ] Check both URLs work (see above)
  - [ ] Stop debugging (`Shift+F5`)

- [ ] **Test Breakpoints**
  - [ ] Open `backend/main.py`
  - [ ] Set breakpoint on any line (click left of line number)
  - [ ] Start "Backend: FastAPI Server" debug
  - [ ] Make request to trigger breakpoint
  - [ ] Debugger should pause at breakpoint
  - [ ] Verify you can inspect variables
  - [ ] Press `F5` to continue

## ✅ Test Tasks

- [ ] **Run Build Task**
  - [ ] Press `Ctrl+Shift+B`
  - [ ] Should start "Full Stack: Start All Services"
  - [ ] Both backend and UI should start

- [ ] **Test Other Tasks**
  - [ ] Press `Ctrl+Shift+P`
  - [ ] Type "Tasks: Run Task"
  - [ ] Try: "Tests: Run All Backend Tests" (if tests exist)
  - [ ] Try: "Lint: Run Black (Format)"
  - [ ] Try: "Clean: Remove Cache Files"

## ✅ Test Auto-Formatting

- [ ] **Verify Auto-Format on Save**
  - [ ] Open any Python file
  - [ ] Make some formatting issues (e.g., extra spaces, long lines)
  - [ ] Save file (`Ctrl+S`)
  - [ ] File should auto-format with Black
  - [ ] Imports should be sorted with isort

## ✅ Test Git Integration

- [ ] **Source Control Panel**
  - [ ] Press `Ctrl+Shift+G`
  - [ ] Should see Source Control panel
  - [ ] Make a small change to any file
  - [ ] File should appear in "Changes" section
  - [ ] Revert the change

## ✅ Test Terminal

- [ ] **Integrated Terminal**
  - [ ] Press `` Ctrl+` ``
  - [ ] Terminal should open
  - [ ] Should see `(venv)` prefix
  - [ ] Try: `python --version` (should show Python 3.11+)
  - [ ] Try: `which python` (should point to venv)

## ✅ Verify Documentation

- [ ] **Check Documentation Files**
  - [ ] Open `docs/LOCAL_IDE_SETUP.md` - Complete guide exists
  - [ ] Open `docs/IDE_QUICK_REFERENCE.md` - Quick reference exists
  - [ ] Open `docs/IDE_VISUAL_GUIDE.md` - Visual guide exists
  - [ ] Open `docs/IDE_SETUP_SUMMARY.md` - Summary exists

## ✅ Optional: Docker Setup

- [ ] **Test Docker (if using)**
  - [ ] Press `Ctrl+Shift+P`
  - [ ] Type "Tasks: Run Task"
  - [ ] Select "Docker: Start Services"
  - [ ] Run `docker ps` - should see containers
  - [ ] Select "Docker: Stop Services" to stop

## 🎯 You're Ready When...

All of the following work:
- [x] VS Code opens the workspace
- [x] Python interpreter is detected
- [x] Extensions are installed
- [x] Can start backend with F5
- [x] Can start UI with F5
- [x] Can set and hit breakpoints
- [x] Auto-formatting works on save
- [x] Terminal auto-activates venv
- [x] Can access http://localhost:8000/api/docs
- [x] Can access UI at http://localhost:7875

## 🐛 Troubleshooting

If any items above fail, check:

### Python Not Found
```bash
# Verify Python installation
python3 --version

# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
pip install -r ui/requirements.txt
```

### Extensions Not Loading
- Restart VS Code
- Manually install from Extensions panel
- Check VS Code is up to date

### Port Already in Use
```bash
# Kill process on port
lsof -ti:8000 | xargs kill -9
lsof -ti:7875 | xargs kill -9
```

### Import Errors
- Verify Python interpreter is selected (bottom-left)
- Check `.vscode/settings.json` has correct PYTHONPATH
- Restart VS Code

### OpenAI Features Not Working
- Verify `OPENAI_API_KEY` is set in `.env`
- Check API key is valid
- Ensure backend can read `.env` file

## 📚 Next Steps

Once everything is checked:

1. **Read the docs**: Familiarize yourself with `docs/LOCAL_IDE_SETUP.md`
2. **Learn shortcuts**: Review `docs/IDE_QUICK_REFERENCE.md`
3. **Follow visual guide**: Step through `docs/IDE_VISUAL_GUIDE.md`
4. **Start coding**: Create a feature branch and start developing!
5. **Refer to contributing**: Read `docs/CONTRIBUTING.md` for guidelines

## 🎉 All Done!

If all items are checked, your local IDE development environment is ready!

Start coding with:
```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Start developing
# Press F5 in VS Code to debug

# Make changes, test, commit
git add .
git commit -m "Your changes"
git push origin feature/your-feature-name
```

---

**Need Help?**
- Check [Troubleshooting Guide](LOCAL_IDE_SETUP.md#troubleshooting)
- Open an issue on GitHub
- Ask in discussions

Happy coding! 🚀
