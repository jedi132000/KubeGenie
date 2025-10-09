# KubeGenie - AI Kubernetes Assistant
LangChain + LangGraph + LangSmith + Gradio Stack

## Development Plan

### Phase 1: Foundation (Steps 1-5)
- [x] Step 1: Project structure & dependencies
- [x] Step 2: Basic Gradio interface
- [x] Step 3: Kubernetes client setup
- [ ] Step 4: LangChain basic agent
- [ ] Step 5: LangGraph router setup

### Phase 2: Core Agents (Steps 6-10)
- [ ] Step 6: Monitoring agent implementation
- [ ] Step 7: Cost optimization agent
- [ ] Step 8: Security agent
- [ ] Step 9: Agent integration testing
- [ ] Step 10: LangSmith observability

### Phase 3: Advanced Features (Steps 11-15)
- [ ] Step 11: Multi-cluster support
- [ ] Step 12: Advanced workflows
- [ ] Step 13: Custom tools
- [ ] Step 14: Production hardening
- [ ] Step 15: Documentation & deployment

## Quick Start

```bash
# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Current Status: Step 3 - Kubernetes Client Integration ✅

Building a modern AI-powered Kubernetes assistant using:
- **LangChain**: Agent orchestration and tool integration
- **LangGraph**: State machine workflows for complex interactions
- **LangSmith**: Observability and debugging for LLM applications  
- **Gradio**: Conversational UI for real-time chat interface
- **Kubernetes**: Direct cluster connectivity and operations

## New in Step 3: Real Kubernetes Integration 🚀

- ✅ **Full Kubernetes Client**: Connect to any cluster via kubeconfig
- ✅ **Interactive Commands**: "Connect to cluster", "List pods", "Show nodes"
- ✅ **Multi-Context Support**: Switch between different Kubernetes contexts
- ✅ **Real-Time Status**: Live cluster health and resource monitoring
- ✅ **Error Handling**: Graceful failures with helpful troubleshooting

**Try These Commands:**
- "Connect to cluster" - Connect to your default kubeconfig
- "Show cluster status" - Get comprehensive cluster overview
- "List nodes" - See all cluster nodes with details
- "List pods" - Show pods in default namespace
- "List all pods" - Show pods across all namespaces