# Deployment Guide

## FastMCP Cloud Deployment (Recommended)

### Prerequisites
- Install FastMCP CLI: `pip install fastmcp`
- Authenticate: `fastmcp auth login`

### Deploy to FastMCP Cloud

1. **Set environment variables**:
```bash
export SUPERVISOR_URL="https://your-mac.ngrok.io"  # Your Mac's public URL
```

2. **Deploy the MCP server**:
```bash
fastmcp deploy server.py --config deploy/fastmcp-cloud.yml --name claude-code-controller
```

3. **Get your MCP endpoint**:
```bash
fastmcp info claude-code-controller
```

### Configure Supervisor URL

Your supervisor must be accessible from the cloud. Options:

1. **ngrok (easiest for development)**:
```bash
# Install ngrok
brew install ngrok

# Expose supervisor (running on port 8080)
ngrok http 8080
```

2. **VPN or public IP**: Configure your router/firewall to forward port 8080

## Self-Hosted Deployment

### Using Docker

1. **Build the image**:
```bash
docker build -f deploy/Dockerfile -t claude-code-controller .
```

2. **Run the container**:
```bash
docker run -d \
  --name claude-code-controller \
  -p 8000:8000 \
  -e SUPERVISOR_URL="http://host.docker.internal:8080" \
  claude-code-controller
```

### Using Cloud Run

1. **Build and push to GCR**:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/claude-code-controller
```

2. **Deploy to Cloud Run**:
```bash
gcloud run deploy claude-code-controller \
  --image gcr.io/YOUR_PROJECT_ID/claude-code-controller \
  --platform managed \
  --region us-central1 \
  --set-env-vars SUPERVISOR_URL="https://your-supervisor-url"
```

## ChatGPT Integration

After deployment, register your MCP endpoint in ChatGPT:

1. Go to ChatGPT Settings > Beta Features
2. Enable "Model Context Protocol"
3. Add your MCP server endpoint
4. Test with: "List my Claude-Code sessions"

## Monitoring

- **FastMCP Cloud**: Built-in monitoring dashboard
- **Self-hosted**: Check logs with `docker logs claude-code-controller`

## Security

- Enable authentication in FastMCP Cloud
- Use HTTPS for all endpoints
- Consider VPN for supervisor communication
- Rotate API keys regularly