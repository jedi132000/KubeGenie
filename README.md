# KubeGenie


**Smart Kubernetes and Crossplane Automation Agent**

KubeGenie is an intelligent agent for managing Kubernetes clusters (cloud and bare metal) and provisioning infrastructure via Crossplane, with multi-cluster support, agent abstraction, and extensibility.


## 🚀 Features

- **Agent Abstraction**: Modular agent classes for cluster operations, lifecycle, and health management
- **Multi-Cluster Management**: Register, list, and switch between cloud and bare metal clusters
- **Cloud & Bare Metal Support**: Provision and manage clusters in EKS, GKE, AKS, and on-prem
- **Extensibility**: Provider/agent registry for easy addition of new cluster types
- **Conversational AI Interface**: Natural language Kubernetes management
- **Gradio Web UI**: Real-time chat and dashboards
- **Authentication & Security**: JWT, RBAC, audit logging
- **Custom Resource & Operator Support**: Manage CRDs and operators
- **Safety Controls**: Validation, approval workflows
- **Observability**: Prometheus, Grafana integration


## 🏗️ Architecture

```
kubegenie/
├── app/               # FastAPI backend, agent and cluster manager modules
├── ui/                # Gradio web interface
├── cli/               # Command-line interface
├── shared/            # Shared libraries and utilities
├── docs/              # Documentation
├── tests/             # Test suites
├── deployments/       # Kubernetes manifests
└── scripts/           # Build and deployment scripts
```


## 🛠️ Development & Quick Start


### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- kubectl
- Helm (optional)


### Quick Start
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd kubegenie
   ```
2. **Install dependencies**
   ```bash
   # Install backend dependencies
   pip install -r app/requirements.txt
   # Install UI dependencies
   pip install -r ui/requirements.txt
   ```
3. **Start backend and UI**
   ```bash
   # Start backend
   cd backend
   python main.py

   # In a separate terminal, start UI
   cd ../ui
   python simple_main.py
   ```

4. **Access the platform**
   - Gradio UI: http://localhost:7860
   - FastAPI backend: http://localhost:8000

### Repo Hygiene

- All unnecessary files (venv/, __pycache__, log files) are excluded for a clean repo.
- Only essential code, configs, and docs are tracked.

### Live Data & Production Readiness

- KubeGenie now returns live Kubernetes cluster data (pods, namespaces, status) in all user-facing interfaces.
- All technical output (actions, suggestions, debug info) is suppressed for end users.
- Safety controls, RBAC, and audit logging are enforced by default.

For more details, see `docs/DEVELOPMENT.md` and `docs/ROADMAP.md`.
   # Install UI dependencies  
   pip install -r ui/requirements.txt
   
   # Install additional packages for OpenAI integration
   pip install openai gradio==4.20.0
   ```

4. **Environment Configuration**
   ```bash
   # Copy environment template and configure
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key:
   # OPENAI_API_KEY=sk-proj-your-openai-api-key-here
   ```

5. **Start the services**
   ```bash
   # Terminal 1: Start backend (with virtual environment)
   cd /path/to/kubegenie && source venv/bin/activate && cd backend && python main.py
   
   # Terminal 2: Start UI (with virtual environment)  
   cd /path/to/kubegenie && source venv/bin/activate && cd ui && python test_buttons.py
   ```

6. **Access the application**
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/api/docs
   - **Test UI**: http://localhost:7880 (Button testing interface)
   - **Health Check**: http://localhost:8000/health

### Docker Compose (Alternative)
```bash
docker-compose up -d
```

## 📋 Usage Examples

### CLI Commands
```bash
# Deploy an application
kubegenie deploy nginx --replicas=3

# Scale a deployment
kubegenie scale redis --replicas=5

# Provision cloud resources
kubegenie provision aws-rds --type=postgresql --size=db.t3.micro

# Check cluster status
kubegenie status --namespace=production
```

### Gradio Web Interface
Navigate to `http://localhost:7880` to access the interactive test interface with:
- **Authentication Testing**: Test login with credentials (admin/admin123)
- **Chat Interface**: Natural language conversation with OpenAI GPT-powered responses
- **Kubernetes Management**: Direct cluster operations and real-time monitoring
- **API Testing**: Test all backend endpoints with proper authentication

### Chat Examples
```
"show me cluster info"
"list all pods in default namespace"  
"what's the status of my cluster?"
"deploy nginx with 3 replicas"
"scale my redis deployment to 5 replicas"
```

## 🔒 Security

KubeGenie implements multiple security layers:

- RBAC and namespace-scoped permissions
- Policy engine for action validation
- Audit logging for all operations
- Secrets management with encryption
- Multi-level approval workflows

## 🤝 Contributing

Please read our [Contributing Guidelines](docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Documentation: [docs/](docs/)
- Issues: GitHub Issues
- Discussions: GitHub Discussions

---

**KubeGenie** - Making Kubernetes and cloud infrastructure management conversational and safe.