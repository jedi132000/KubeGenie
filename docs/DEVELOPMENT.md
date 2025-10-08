
# KubeGenie Development Guide

Welcome to KubeGenie development! This guide now reflects our new implementation plan for agent abstraction, multi-cluster management, cloud/bare metal support, extensibility, lifecycle, custom resources, documentation, and testing.


## 🚀 What's Been Implemented

### ✅ Completed Features

1. **Core Architecture**
   - FastAPI backend with microservices pattern
   - Gradio UI for conversational interface
   - CLI tool with rich terminal output
   - Docker containerization and Kubernetes deployments

2. **Authentication System**
   - JWT-based authentication
   - Role-based access control (RBAC)
   - User management with permissions
   - Secure API endpoints

3. **AI/LLM Integration**
   - Rule-based natural language processing
   - OpenAI GPT integration (optional)
   - Intent recognition and command parsing
   - Context-aware conversations

4. **Database Models**
   - User management
   - Audit logging
   - Chat history
   - Resource operation tracking
   - Crossplane resource management

## 🆕 Implementation Plan

### 1. Agent Abstraction
- Create base `KubernetesAgent` class for cluster operations, lifecycle, and health
- Refactor client logic into agent classes
- Implement lifecycle hooks: `initialize`, `health_check`, `shutdown`, `self_heal`

### 2. Multi-Cluster Management
- Design `ClusterManager` for registering, listing, and switching clusters
- Support dynamic registration for cloud and bare metal clusters
- Add API endpoints for cluster management

### 3. Cloud Cluster Provisioning
- Implement modules for EKS, GKE, AKS cluster provisioning
- Integrate with Crossplane for cluster creation
- Add endpoints for cluster provisioning and status

### 4. Bare Metal Support
- Document and implement connection flows for bare metal clusters
- Add support for custom endpoints and authentication

### 5. Extensibility
- Provider/agent registry for new cluster types
- Plugin architecture for cloud/bare metal providers

### 6. Agent Lifecycle Management
- Health checks, self-healing routines, and lifecycle management
- Periodic health monitoring and auto-recovery
- Expose agent status via API endpoints

### 7. Custom Resource & Operator Support
- Endpoints for managing CRDs and operators
- Logic for custom controllers and reconciliation loops

### 8. Documentation & Examples
- Update docs for new abstractions and flows
- Example configs for cloud/bare metal clusters
- Usage guides for multi-cluster and agent features

### 9. Testing & Validation
- Unit/integration tests for agent, manager, and provisioning logic
- Validate multi-cluster operations in CI/CD pipeline
- Test cases for cloud and bare metal scenarios

## 🛠️ Development Setup

### 1. Prerequisites

```bash
# System requirements
- Python 3.11+
- Docker & Docker Compose
- kubectl (for Kubernetes testing)
- jq (for API testing)

# Optional
- OpenAI API key (for advanced LLM features)
- Access to Kubernetes cluster
```

git clone https://github.com/jedi132000/KubeGenie.git
cd kubegenie

# Run setup script
./scripts/setup-dev.sh

# Copy environment file
### 2. Environment Setup & Repo Hygiene

```bash
# Clone and setup
git clone https://github.com/jedi132000/KubeGenie.git
cd kubegenie

# Run setup script
./scripts/setup-dev.sh

# Install backend dependencies
pip install -r backend/requirements.txt
# Install UI dependencies
pip install -r ui/requirements.txt

# Start backend
cd backend
python main.py

# In a separate terminal, start UI
cd ../ui
python simple_main.py

# All unnecessary files (venv/, __pycache__, log files) are excluded for repo hygiene.
cp .env.example .env

# Edit .env with your configuration
# Add OpenAI API key if you have one
# Configure Kubernetes cluster access
```

### 3. Start Services

```bash
# Option 1: Docker Compose (Recommended for development)
docker-compose up -d

# Option 2: Manual startup
# Terminal 1: Backend
cd backend && source venv/bin/activate && python main.py

# Terminal 2: UI  
cd ui && ./start.sh

# Terminal 3: Test APIs
./scripts/test-api.sh
```

### 4. Access Points

- **Gradio UI**: http://localhost:7860
- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

## 🧪 Testing the Implementation

### Authentication Test

```bash
# Login as admin user
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use the returned token for authenticated requests
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/auth/me
```

### Chat Interface Test

```bash
# Test natural language processing
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "deploy nginx with 3 replicas"}'
```

### Default Users

| Username | Password | Permissions |
|----------|----------|-------------|
| admin | admin123 | Full admin access |
| operator | operator123 | Cluster read/write |
| viewer | viewer123 | Read-only access |

⚠️ **Change these passwords in production!**

## 🎯 Next Development Priorities

### Phase 1: Core Functionality (Week 1-2)

1. **Real Kubernetes Integration**
   ```bash
   # Current status: Using mock responses
   # Next: Connect to actual Kubernetes cluster
   # Files to modify:
   - backend/app/core/kubernetes.py
   - backend/app/api/v1/endpoints/kubernetes.py
   ```

2. **Database Setup**
   ```bash
   # Initialize database migrations
   cd backend
   alembic init alembic  # If not already done
   alembic revision --autogenerate -m "initial tables"
   alembic upgrade head
   ```

3. **Enhanced LLM Processing**
   ```bash
   # Add OpenAI API key to .env
   OPENAI_API_KEY=your-key-here
   
   # Test advanced chat features
   # Files to enhance:
   - backend/app/core/llm.py
   ```

### Phase 2: Production Features (Week 3-4)

1. **Security Enhancements**
   - Input validation and sanitization
   - Rate limiting
   - Audit logging implementation
   - Secrets management

2. **Real-time Features**
   - WebSocket integration for live updates
   - Streaming responses in Gradio
   - Real-time cluster monitoring

3. **Error Handling**
   - Comprehensive error handling
   - User-friendly error messages
   - Recovery mechanisms

## 🔧 Key Files to Work On

### Backend Priority Files
```
backend/
├── app/core/kubernetes.py     # Real K8s integration
├── app/core/llm.py           # Enhanced AI processing  
├── app/core/auth.py          # Security improvements
├── app/api/v1/endpoints/     # API enhancements
└── alembic/                  # Database migrations
```

### UI Priority Files
```
ui/
├── gradio_app.py            # Authentication integration
└── requirements.txt         # Additional dependencies
```

### Infrastructure
```
deployments/                 # K8s deployment updates
docker-compose.yml          # Service configuration
scripts/                    # Development tools
```

## 🐛 Known Issues to Fix

1. **Authentication in Gradio UI**
   - Currently UI doesn't handle auth tokens
   - Need to implement login flow in Gradio

2. **Mock Data Responses**  
   - Kubernetes endpoints return mock data
   - Crossplane endpoints return mock data
   - Need real cluster integration

3. **Database Not Initialized**
   - Models defined but not created
   - Need to run Alembic migrations
   - Need to seed initial data

4. **Error Handling**
   - Many endpoints have basic error handling
   - Need comprehensive validation
   - Need user-friendly error messages

## 📋 Development Workflow

### Adding New Features

1. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Follow the architecture**
   - Backend: Add API endpoints in `app/api/v1/endpoints/`
   - Models: Add database models in `app/models/`
   - UI: Update Gradio interface in `ui/gradio_app.py`

3. **Test your changes**
   ```bash
   # Test backend
   pytest tests/
   
   # Test API endpoints
   ./scripts/test-api.sh
   
   # Manual testing via Gradio UI
   cd ui && ./start.sh
   ```

4. **Update documentation**
   - Add to ROADMAP.md for significant features
   - Update API documentation
   - Add examples to README

### Code Quality

- Use type hints throughout
- Add docstrings to all functions
- Follow PEP 8 for Python code
- Add unit tests for new functionality
- Run linting: `black`, `isort`, `mypy`

## 🆘 Getting Help

1. **Check existing issues** in the GitHub repository
2. **Read the logs** when things don't work
3. **Test incrementally** - don't make big changes at once  
4. **Use the test scripts** to verify functionality

## 🎉 Ready to Start!

You now have a solid foundation with:
- ✅ Authentication system
- ✅ AI/LLM integration framework
- ✅ Database models
- ✅ Gradio UI framework
- ✅ Comprehensive API structure

The next step is to connect these pieces to real Kubernetes clusters and enhance the user experience!

---

**Happy coding!** 🧞‍♂️✨