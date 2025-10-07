# VS Code Setup Visual Guide

## 📸 Step-by-Step Setup with Screenshots

### Step 1: Open the Project

**Option A: Open Workspace (Recommended)**
```bash
code KubeGenie.code-workspace
```

**Option B: Open Folder**
```bash
code .
```

> 💡 **Tip**: Using the workspace file provides better organization with multiple folders.

---

### Step 2: Install Extensions

When you first open the project, VS Code will show a notification:

```
This workspace has extension recommendations.
[Show Recommendations] [Install All] [Ignore]
```

Click **"Install All"** to install:
- Python
- Pylance (Python IntelliSense)
- Python Debugger
- Black Formatter
- isort
- Docker
- Kubernetes
- YAML
- GitLens
- Error Lens
- And more...

**Manual Installation:**
1. Press `Ctrl+Shift+X` to open Extensions panel
2. Search for "Python"
3. Click "Install" on the Microsoft Python extension

---

### Step 3: Select Python Interpreter

VS Code should auto-detect the virtual environment. If not:

1. Press `Ctrl+Shift+P`
2. Type: "Python: Select Interpreter"
3. Choose: `./venv/bin/python` or `Python 3.11.x ('venv')`

You'll see the selected interpreter in the bottom-left status bar.

---

### Step 4: Run Setup (If Not Done)

**Option A: Using Terminal**
```bash
./scripts/ide-quickstart.sh
```

**Option B: Using VS Code Task**
1. Press `Ctrl+Shift+P`
2. Type: "Tasks: Run Task"
3. Select: "Setup: Install All Dependencies"

Wait for the setup to complete (installs dependencies, creates venv, etc.)

---

### Step 5: Configure Environment

1. Ensure `.env` file exists (created by setup script)
2. Edit `.env` and add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=sk-proj-your-actual-api-key-here
   ```

---

### Step 6: Start Debugging

#### Method A: Using F5 (Recommended)

1. Press `F5` or click "Run and Debug" icon in sidebar
2. Select a debug configuration:
   - **Full Stack: Backend + UI** (starts both)
   - **Backend: FastAPI Server** (backend only)
   - **UI: Gradio Simple** (UI only)
3. Application starts with debugging enabled

#### Method B: Using Tasks

1. Press `Ctrl+Shift+B` (runs default build task)
   - This starts both backend and UI
2. Or `Ctrl+Shift+P` → "Tasks: Run Task" → "Full Stack: Start All Services"

---

### Step 7: Set Breakpoints and Debug

**Setting Breakpoints:**
1. Open a Python file (e.g., `backend/main.py`)
2. Click left of line number (red dot appears)
3. Or press `F9` on the line

**Debug Controls:**
- `F5` - Continue
- `F10` - Step Over
- `F11` - Step Into
- `Shift+F11` - Step Out
- `Shift+F5` - Stop Debugging

**Debug Panels:**
- **Variables**: See all variables in current scope
- **Watch**: Add expressions to monitor
- **Call Stack**: See execution path
- **Breakpoints**: Manage all breakpoints
- **Debug Console**: Execute Python code during debugging

---

### Step 8: Access the Running Application

Once started, open these URLs in your browser:

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/api/docs |
| Gradio UI | http://localhost:7875 |
| Health Check | http://localhost:8000/health |

---

## 🎯 Common Tasks

### Running Tests

**Method A: Test Explorer**
1. Click "Testing" icon in sidebar (beaker icon)
2. Click "Run All Tests" button
3. Or click individual test to run it

**Method B: Debug Configuration**
1. Open Run and Debug panel (`Ctrl+Shift+D`)
2. Select "Tests: Backend Unit Tests"
3. Press `F5`

**Method C: Terminal**
```bash
source venv/bin/activate
pytest tests/ -v
```

---

### Formatting Code

**Auto-format (Recommended):**
- Just save the file (`Ctrl+S`)
- Black formatter runs automatically

**Manual Format:**
1. Right-click in editor
2. Select "Format Document"
3. Or press `Shift+Alt+F`

**Format All Files:**
1. Press `Ctrl+Shift+P`
2. Type: "Tasks: Run Task"
3. Select: "Lint: Run Black (Format)"

---

### Using Terminal

**Open Terminal:**
- Press `` Ctrl+` `` (backtick)
- Or View → Terminal

**Multiple Terminals:**
1. Click `+` icon in terminal panel
2. Or `Ctrl+Shift+`` ` (new terminal)

**Terminal automatically:**
- Activates virtual environment
- Sets PYTHONPATH
- Uses project root as working directory

---

### Git Operations

**View Changes:**
1. Press `Ctrl+Shift+G` (Source Control panel)
2. See modified files

**Commit Changes:**
1. Stage files (click `+` next to file)
2. Enter commit message
3. Click ✓ (checkmark) or press `Ctrl+Enter`

**Push Changes:**
1. Click `...` menu in Source Control
2. Select "Push"

---

### Docker Operations

**Start Docker Services:**
1. Press `Ctrl+Shift+P`
2. Type: "Tasks: Run Task"
3. Select: "Docker: Start Services"

**View Docker Logs:**
1. Select: "Docker: View Logs"

**Stop Docker Services:**
1. Select: "Docker: Stop Services"

---

## 🐛 Debugging Examples

### Example 1: Debug Backend API Endpoint

1. Open `backend/app/api/v1/endpoints/kubernetes.py`
2. Find the endpoint function you want to debug
3. Set breakpoint on first line of the function
4. Start debugging with "Backend: FastAPI Server"
5. Make API request to http://localhost:8000/api/v1/...
6. Debugger pauses at breakpoint
7. Inspect variables, step through code

### Example 2: Debug UI Button Click

1. Open `ui/simple_main.py`
2. Find the handler function (e.g., `handle_message`)
3. Set breakpoint inside the function
4. Start debugging with "UI: Gradio Simple"
5. Click button in the UI
6. Debugger pauses at breakpoint
7. Step through the code execution

### Example 3: Debug Full Stack Flow

1. Set breakpoint in UI handler (`ui/simple_main.py`)
2. Set breakpoint in backend endpoint (`backend/app/api/...`)
3. Start with "Full Stack: Backend + UI" configuration
4. Trigger action in UI
5. Debugger stops at UI breakpoint first
6. Continue (`F5`) - request goes to backend
7. Debugger stops at backend breakpoint
8. See the complete flow!

---

## 💡 Pro Tips

### Tip 1: Use Multi-Cursor Editing
- Hold `Alt` and click to add cursors
- Or `Ctrl+Alt+↑/↓` to add cursor above/below
- Edit multiple lines simultaneously!

### Tip 2: Quick File Navigation
- Press `Ctrl+P`, type filename
- Instantly jump to any file
- Add `:` and line number to jump to line

### Tip 3: Go to Definition
- Hold `Ctrl` and click on function/class
- Or press `F12`
- Jumps to definition

### Tip 4: Find All References
- Right-click on function/variable
- Select "Find All References"
- Or press `Shift+F12`

### Tip 5: Rename Symbol
- Right-click on variable/function
- Select "Rename Symbol"
- Or press `F2`
- Renames everywhere in project!

### Tip 6: Use Command Palette
- Press `Ctrl+Shift+P`
- Type any command
- Fuzzy search works!

### Tip 7: Split Editor
- Drag file tab to side
- Or `Ctrl+\` to split current file
- View multiple files side-by-side

### Tip 8: Zen Mode
- Press `Ctrl+K Z`
- Distraction-free coding
- Press `Esc Esc` to exit

---

## 🔧 Troubleshooting Visual Guide

### Problem: Python Not Found

**Symptoms:**
- Import errors
- "Python" not recognized
- Linting not working

**Solution:**
1. Check bottom-left status bar for Python version
2. If wrong or missing, press `Ctrl+Shift+P`
3. Type: "Python: Select Interpreter"
4. Choose: `./venv/bin/python`

### Problem: Terminal Not Activating venv

**Symptoms:**
- Terminal doesn't show `(venv)` prefix
- Import errors when running commands

**Solution:**
```bash
# Manually activate:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Problem: Port Already in Use

**Symptoms:**
- Error: "Address already in use"
- Cannot start backend/UI

**Solution:**
```bash
# Find and kill process on port 8000:
lsof -ti:8000 | xargs kill -9

# Find and kill process on port 7875:
lsof -ti:7875 | xargs kill -9
```

### Problem: Extensions Not Loading

**Symptoms:**
- IntelliSense not working
- No code formatting
- No debug configurations

**Solution:**
1. Press `Ctrl+Shift+X`
2. Search for extension name
3. Click "Reload Required" or "Install"
4. Restart VS Code if needed

---

## 📚 Additional Resources

- **[Full Documentation](LOCAL_IDE_SETUP.md)** - Complete setup guide
- **[Quick Reference](IDE_QUICK_REFERENCE.md)** - Keyboard shortcuts and commands
- **[Contributing Guide](CONTRIBUTING.md)** - Development guidelines

---

## 🎬 Video Tutorials (Coming Soon)

- Setting up your first development session
- Debugging backend and UI together
- Using VS Code tasks effectively
- Git workflow in VS Code

---

**Need Help?**
- Check [Troubleshooting](LOCAL_IDE_SETUP.md#troubleshooting)
- Open an issue on GitHub
- Ask in discussions

Happy coding! 🚀
