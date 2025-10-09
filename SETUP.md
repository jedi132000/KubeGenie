# KubeGenie Development Setup

## Quick Start

### 1. Install Dependencies
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install requirements
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# Required: OPENAI_API_KEY=your_key_here
```

### 3. Run the Application
```bash
# Development mode
python main.py

# Or install in development mode
pip install -e .
kubegenie --help
```

## Project Structure
```
kubegenie/
├── src/
│   ├── agents/        # LangChain agents (monitoring, cost, security)
│   ├── tools/         # Kubernetes tools and utilities  
│   ├── ui/            # Gradio interface components
│   └── utils/         # Shared utilities
├── main.py            # Application entry point
├── requirements.txt   # Python dependencies
└── .env.example       # Environment template
```

## Development Status
- ✅ Step 1: Project structure and dependencies
- 🔄 Step 2: Basic Gradio interface (in progress)
- ⏳ Step 3: LangChain tools for kubectl operations

## Tech Stack
- **LangChain**: Core AI framework
- **LangGraph**: Multi-agent workflows
- **LangSmith**: AI observability
- **Gradio**: Web interface
- **Kubernetes**: Cluster management