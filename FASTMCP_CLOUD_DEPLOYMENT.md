# FastMCP Cloud Deployment Guide

This document provides the exact steps to deploy the Claude-Code MCP Controller to FastMCP Cloud, following the official FastMCP documentation.

## ✅ Prerequisites (Completed)

- [x] **FastMCP 2.12.4** installed and tested
- [x] **Real FastMCP server** implemented (`server.py`)
- [x] **HTTP transport** tested and working
- [x] **All 8 MCP tools** implemented and ready
- [x] **Requirements.txt** configured with `fastmcp>=2.0.0`
- [x] **Git repository** initialized with committed code

## 🚀 Deployment Steps

### Step 1: Create GitHub Repository

1. **Create new GitHub repository**:
   - Repository name: `claude-code-mcp-controller`
   - Description: "FastMCP server for controlling Claude-Code sessions remotely via ChatGPT"
   - Visibility: Public (recommended for FastMCP Cloud)

2. **Add GitHub remote**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/claude-code-mcp-controller.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to FastMCP Cloud

1. **Sign in to FastMCP Cloud**:
   - Go to https://fastmcp.cloud
   - Sign in with GitHub account
   - Grant repository access permissions

2. **Create new project**:
   - **Project Name**: `claude-code-controller`
   - **GitHub Repository**: `YOUR_USERNAME/claude-code-mcp-controller`
   - **Entrypoint**: `server.py:mcp`
   - **Authentication**: Public (or restricted to organization)

3. **Configure environment variables** (if needed):
   ```
   SUPERVISOR_URL=https://your-ngrok-url.ngrok.io
   ```

4. **Deploy**:
   - FastMCP Cloud will automatically:
     - Clone the repository
     - Install dependencies from `requirements.txt`
     - Build the FastMCP server
     - Deploy to: `https://claude-code-controller.fastmcp.app/mcp`

## 🔗 Expected Deployment URL

After successful deployment:
```
https://claude-code-controller.fastmcp.app/mcp
```

## 🛠️ Local Supervisor Setup

Before connecting ChatGPT, ensure your local supervisor is accessible:

1. **Start supervisor**:
   ```bash
   python3 supervisor/main.py
   ```

2. **Make supervisor public** (for development):
   ```bash
   ngrok http 8080
   ```

3. **Update environment variable**:
   ```bash
   export SUPERVISOR_URL="https://your-ngrok-url.ngrok.io"
   ```

## 📱 ChatGPT Integration

### Option 1: MCP Connectors (Team/Enterprise)

1. **Admin setup**:
   - Go to ChatGPT Organization Settings
   - Navigate to Connectors section
   - Add new MCP connector:
     - **Name**: Claude-Code Controller
     - **URL**: `https://claude-code-controller.fastmcp.app/mcp`
     - **Type**: HTTP transport

2. **User access**:
   - Users can access via standard ChatGPT interface
   - Tools appear automatically in conversation

### Option 2: Manual Integration (Development)

1. **Test with compatible MCP clients**
2. **Verify all 8 tools are available**:
   - `list_sessions`
   - `create_session`
   - `send_message`
   - `get_logs`
   - `get_session_status`
   - `terminate_session`
   - `check_prompts`
   - `respond_to_prompt`

## 🧪 Testing Deployment

1. **Verify server accessibility**:
   ```bash
   curl https://claude-code-controller.fastmcp.app/mcp
   ```

2. **Test tool availability**:
   - Use MCP client to connect
   - List available tools
   - Test basic functionality

## 📋 Deployment Checklist

- [ ] GitHub repository created and pushed
- [ ] FastMCP Cloud project configured
- [ ] Deployment successful at `*.fastmcp.app/mcp`
- [ ] Local supervisor running and accessible
- [ ] Environment variables configured
- [ ] ChatGPT MCP connector configured
- [ ] End-to-end functionality tested

## 🔧 Troubleshooting

### Common Issues

1. **Deployment fails**:
   - Check `requirements.txt` syntax
   - Verify `server.py:mcp` entrypoint
   - Review FastMCP Cloud build logs

2. **Cannot connect to supervisor**:
   - Verify `SUPERVISOR_URL` environment variable
   - Check ngrok tunnel status
   - Test supervisor accessibility

3. **Tools not appearing in ChatGPT**:
   - Verify MCP connector configuration
   - Check server deployment status
   - Confirm authentication settings

### Support Resources

- **FastMCP Documentation**: https://gofastmcp.com
- **FastMCP Cloud**: https://fastmcp.cloud
- **MCP Specification**: https://modelcontextprotocol.io

## 🎯 Success Criteria

✅ **Deployment successful**: Server running at FastMCP Cloud URL
✅ **Tools accessible**: All 8 MCP tools available
✅ **ChatGPT integration**: Can control Claude-Code sessions remotely
✅ **Mobile workflow**: Full functionality on mobile ChatGPT app

---

**Status**: Ready for deployment
**Next Step**: Create GitHub repository and deploy to FastMCP Cloud