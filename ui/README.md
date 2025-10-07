# KubeGenie Gradio UI

A modern, interactive web interface built with Gradio for the KubeGenie Kubernetes and Crossplane automation agent.

## Features

- **🤖 Conversational Interface**: Chat with KubeGenie using natural language
- **☸️ Kubernetes Management**: Deploy, scale, and monitor applications
- **☁️ Crossplane Resources**: Provision and manage cloud infrastructure
- **📊 Real-time Monitoring**: Live cluster status and health dashboards
- **🎨 Beautiful Interface**: Modern, responsive design with intuitive navigation

## Quick Start

### Prerequisites

- Python 3.11+
- KubeGenie backend running on `http://localhost:8000`

### Running Locally

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the UI**
   ```bash
   ./start.sh
   ```

3. **Access the interface**
   Open your browser and navigate to `http://localhost:7860`

### Using Docker

```bash
# Build the Docker image
docker build -t kubegenie-ui .

# Run the container
docker run -p 7860:7860 -e KUBEGENIE_API_URL=http://localhost:8000 kubegenie-ui
```

## Configuration

Set the following environment variables to configure the UI:

- `KUBEGENIE_API_URL`: Backend API URL (default: `http://localhost:8000`)
- `KUBEGENIE_UI_PORT`: UI port (default: `7860`)
- `KUBEGENIE_UI_HOST`: UI host (default: `0.0.0.0`)

## Usage Examples

### Chat Interface

Try these natural language commands in the chat:

- "deploy nginx with 3 replicas"
- "scale redis to 5 replicas"
- "show me all pods in production namespace"
- "provision an S3 bucket on AWS"
- "check cluster health"

### Direct Operations

Use the dedicated tabs for:

- **Kubernetes**: Direct cluster operations, pod management, deployments
- **Crossplane**: Cloud resource provisioning and management
- **Status**: Real-time monitoring and health checks

## Development

The UI is built with:

- **Gradio 4.7.1**: Modern ML/AI web interface framework
- **Requests**: HTTP client for API communication
- **Pandas**: Data manipulation and display

### File Structure

```
ui/
├── gradio_app.py      # Main Gradio application
├── requirements.txt   # Python dependencies
├── Dockerfile        # Container configuration
├── start.sh          # Startup script
└── README.md         # This file
```

### Adding New Features

1. **New Chat Commands**: Update the `process_chat_message` method in `KubeGenieUI` class
2. **New Tabs**: Add new tab sections in the `create_kubegenie_ui` function
3. **New API Integrations**: Add methods to the `KubeGenieUI` class for new backend endpoints

## Deployment

### Kubernetes

Use the provided Kubernetes manifests in `../deployments/ui.yaml`:

```bash
kubectl apply -f ../deployments/ui.yaml
```

### Docker Compose

The UI is included in the main docker-compose configuration:

```bash
docker-compose up -d
```

## Troubleshooting

### Common Issues

1. **UI not connecting to backend**: Check `KUBEGENIE_API_URL` environment variable
2. **Port conflicts**: Change `KUBEGENIE_UI_PORT` to an available port
3. **Permission errors**: Ensure the startup script is executable: `chmod +x start.sh`

### Logs

Check application logs for debugging:

```bash
# If running locally
python gradio_app.py

# If using Docker
docker logs <container-name>
```

## Contributing

See the main [Contributing Guidelines](../docs/CONTRIBUTING.md) for information on how to contribute to the KubeGenie project.

---

**KubeGenie Gradio UI** - Making Kubernetes management conversational and intuitive! 🧞‍♂️