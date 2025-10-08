<!-- 
KubeGenie - Smart Kubernetes and Crossplane Automation Agent
A production-ready AI-driven infrastructure management platform with conversational interface.

Project Overview:
- FastAPI backend with agent abstraction, multi-cluster management, and Kubernetes/Crossplane integration
- Modern Gradio UI for conversational AI interactions
- CLI tool for terminal-based operations
- Complete containerization and deployment solutions
- Enterprise-grade safety controls and audit logging

Tech Stack:
- Backend: Python 3.11+, FastAPI, Kubernetes Python Client, Crossplane
- UI: Gradio 4.7+, Python-based web interface
- CLI: Typer, Rich, Click
- Infrastructure: Docker, Kubernetes, PostgreSQL, Redis
- Observability: Prometheus, Grafana integration

Architecture:
kubegenie/
├── app/               # FastAPI REST API, agent and cluster manager modules
├── ui/                # Gradio web interface with chat and dashboards  
├── cli/               # Command-line interface
├── shared/            # Common utilities and libraries
├── deployments/       # Kubernetes manifests
├── tests/             # Comprehensive test suite
├── docs/              # Documentation and guides
└── scripts/           # Development and deployment scripts

Key Features Implemented:
✅ Agent abstraction for cluster operations, lifecycle, and health
✅ Multi-cluster management (cloud and bare metal)
✅ Cloud cluster provisioning (EKS, GKE, AKS) and bare metal support
✅ Extensibility via provider/agent registry
✅ Conversational AI interface for natural language Kubernetes management
✅ Complete Kubernetes operations (deploy, scale, monitor, troubleshoot)
✅ Crossplane integration for multi-cloud resource provisioning
✅ Real-time monitoring with WebSocket support
✅ Safety controls with validation, audit logging, and approval workflows
✅ Enterprise security with RBAC and policy engine
✅ Production-ready containerization and deployment
✅ Comprehensive testing and documentation

Quick Start Commands:
- Development: ./scripts/setup-dev.sh
- Docker: docker-compose up -d
- Backend: cd app && python main.py
- UI: cd ui && ./start.sh (http://localhost:7860)
- CLI: cd cli && python main.py --help
- Tests: pytest tests/

Service Endpoints:
- Gradio UI: http://localhost:7860 (main interface)
- FastAPI: http://localhost:8000 (API backend)
- API Docs: http://localhost:8000/api/docs
- Health: http://localhost:8000/health

Deployment:
- Kubernetes: kubectl apply -f deployments/
- Docker Compose: docker-compose up -d
- Build: ./scripts/build.sh [version] [push] [deploy]

When working on this project:
1. Always consider the conversational AI aspect - this is an intelligent agent
2. Maintain safety-first approach with validation and audit trails  
3. Follow microservices patterns for scalability
4. Use natural language processing for user interactions
5. Implement proper error handling and user feedback
6. Keep security and RBAC in mind for all operations
7. Write tests for all new functionality
8. Update documentation for user-facing changes
9. Consider multi-cloud and multi-cluster scenarios
10. Maintain backward compatibility for CLI and API

The project is production-ready and follows enterprise best practices for
AI-driven infrastructure automation with strong safety controls.
-->