# KubeGenie

**Smart Kubernetes and Crossplane automation agent**

KubeGenie is an intelligent agent that empowers platform engineers, DevOps, and SRE teams to manage Kubernetes clusters and provision cloud infrastructure via Crossplane using natural language commands.

## 🚀 Features

- **Conversational Interface**: Interact via CLI, web app, or chat platforms
- **Kubernetes Operations**: Deploy, scale, and manage workloads with natural language
- **Persistent Storage**: Dynamic PVC/PV management with backup/restore capabilities
- **Crossplane Integration**: Multi-cloud infrastructure provisioning and management
- **Safety Controls**: Policy engine with RBAC, audit logging, and operation previews
- **Observability**: Integration with Prometheus, Grafana, and GitOps workflows

## 🏗️ Architecture

```
kubegenie/
├── backend/           # FastAPI backend service
├── ui/               # Gradio web interface
├── cli/              # Command-line interface
├── shared/           # Shared libraries and utilities
├── docs/             # Documentation
├── tests/            # Test suites
├── deployments/      # Kubernetes manifests
└── scripts/          # Build and deployment scripts
```

## 🛠️ Development

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

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the UI**
   ```bash
   cd ui
   pip install -r requirements.txt
   ```

4. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Environment Setup

Copy the environment template and configure your settings:
```bash
cp .env.example .env
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
Navigate to `http://localhost:7860` to access the interactive Gradio web interface with:
- **Chat Interface**: Natural language conversation with KubeGenie
- **Kubernetes Management**: Direct cluster operations and monitoring
- **Crossplane Resources**: Cloud resource provisioning and management
- **Real-time Status**: Live cluster health and monitoring dashboards

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