# Claude-Code MCP Controller 🚀

A production-ready, cloud-first MCP (Model Context Protocol) server for remotely controlling and monitoring Claude-Code sessions via ChatGPT. Perfect for mobile workflows, remote development, and managing multiple coding sessions.

## 🎯 What This Solves

**Problem**: You're away from your Mac but need to check on or control your Claude-Code sessions.

**Solution**: Use ChatGPT as a remote control for your Claude-Code sessions through MCP.

### Real-World Use Cases

- 📱 **Mobile Development**: Check session status while commuting
- 🏠 **Remote Work**: Monitor long-running tasks from anywhere
- 🔄 **Multi-Project Management**: Control multiple Claude-Code sessions simultaneously
- 🚨 **Stuck Command Recovery**: Handle interactive prompts that block sessions
- 📊 **Session Monitoring**: Get logs and status updates in natural language

## ⚡ Quick Demo

```
You: "What Claude-Code sessions are running?"
ChatGPT: "You have 2 active sessions:
- web-app_a1b2: Building user dashboard (last active 5 min ago)
- api_c3d4: Adding authentication (last active 2 min ago)"

You: "Tell the web-app session to run the tests"
ChatGPT: "✅ Message sent! The session is now running tests..."

You: "Any sessions stuck waiting for input?"
ChatGPT: "Yes! The api session is asking: 'Install new dependency? [y/n]'"

You: "Tell it yes"
ChatGPT: "✅ Response sent! Session will continue with installation."
```

> **💡 Test this demo locally!** Start the server + supervisor, then `ngrok http 8000` to try it yourself with real ChatGPT before deploying.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   ChatGPT +     │◄──►│   FastMCP Cloud  │◄──►│  Mac Supervisor │
│   MCP Connector │    │   (MCP Server)   │    │  (Local Agent) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                │                        ▼
                                │               ┌─────────────────┐
                                │               │ Claude-Code     │
                                │               │ Sessions        │
                                │               │ (Multiple PTYs) │
                                └───────────────┤ • session_1     │
                                  WebSocket/    │ • session_2     │
                                  HTTP          │ • session_N     │
                                                └─────────────────┘
```

## 🚀 Quick Start

### 1. Test Locally with ChatGPT (Recommended)

```bash
# Clone and setup
git clone <your-repo>
cd claude-code-mcp-controller

# Install dependencies (using Python 3.10+)
python3 -m pip install -r requirements.txt

# Start supervisor
python3 supervisor/main.py
```

**In another terminal:**
```bash
# Start FastMCP server
python3 -c "from server import mcp; mcp.run(transport='http', host='0.0.0.0', port=8000, path='/mcp')"

# In a third terminal, make server public for ChatGPT
ngrok http 8000
```

**Configure ChatGPT:**
- Add MCP connector: `https://your-ngrok-url.ngrok-free.app/mcp`
- Test: *"What Claude-Code tools are available?"*

### 2. Deploy to FastMCP Cloud (When Ready)

**Step 1: Create GitHub Repository**
```bash
# Add GitHub remote and push
git remote add origin https://github.com/YOUR_USERNAME/claude-code-mcp-controller.git
git push -u origin main
```

**Step 2: Deploy to FastMCP Cloud**
1. **Sign in**: Go to https://fastmcp.cloud with GitHub account
2. **Create project**:
   - **Name**: `claude-code-controller`
   - **Repository**: `YOUR_USERNAME/claude-code-mcp-controller`
   - **Entrypoint**: `server.py:mcp`
3. **Deploy**: Automatic deployment to `https://claude-code-controller.fastmcp.app/mcp`

**Step 3: Connect ChatGPT**
- **Team/Enterprise**: Add MCP connector with your FastMCP Cloud URL
- **Development**: Use compatible MCP clients with the endpoint
- **Test**: *"List my Claude-Code sessions"*

## 🛠️ MCP Tools Available

| Tool | Purpose | ChatGPT Example |
|------|---------|-----------------|
| `list_sessions` | Show all active sessions | *"What sessions are running?"* |
| `create_session` | Start new Claude-Code | *"Create a session in my project folder"* |
| `send_message` | Send commands to session | *"Tell the web-app session to add tests"* |
| `get_logs` | Retrieve session output | *"Show me recent logs from api session"* |
| `get_session_status` | Check session details | *"What's the status of session X?"* |
| `terminate_session` | Stop a session | *"Terminate the stuck session"* |
| `check_prompts` | Find pending prompts | *"Any sessions waiting for input?"* |
| `respond_to_prompt` | Answer interactive prompts | *"Tell it 'yes'"* |

## 📋 Testing & Development

### 🎯 Local ChatGPT Testing (Recommended)

Test the **real end-to-end experience** with ChatGPT locally before deploying:

```bash
# Terminal 1: Start supervisor
python3 supervisor/main.py

# Terminal 2: Start FastMCP server
python3 -c "from server import mcp; mcp.run(transport='http', host='0.0.0.0', port=8000, path='/mcp')"
```

**Then connect ChatGPT:**
1. **Make public**: `ngrok http 8000`
2. **Configure ChatGPT**: Add MCP connector with `https://your-ngrok-url.ngrok-free.app/mcp`
3. **Test mobile workflow**: Use ChatGPT mobile app to control Claude-Code remotely

**Test scenarios in ChatGPT:**
```
"What Claude-Code tools are available?"
"List my Claude-Code sessions"
"Create a new session called mobile-test"
"Tell the mobile-test session to list files"
"Show me recent logs from that session"
```

### 🔧 Development Testing (Automated)

For code validation and CI/CD:

```bash
# Validate FastMCP patterns
python3 pattern_validation.py

# Test server import and tools
python3 test_client.py

# Test specific components
python3 supervisor/main.py  # Test supervisor
python3 server.py           # Test MCP server (STDIO)
```

### Local vs Production Testing

| Testing Method | Purpose | When to Use |
|---------------|---------|-------------|
| **ChatGPT Local** | Real UX validation | Before deployment, mobile testing |
| **Automated Tests** | Code validation | Development, CI/CD |
| **FastMCP Cloud** | Production testing | Final validation |

**Priority**: Always test with **ChatGPT locally first** - it's your source of truth for user experience.

## 🚢 Deployment Options

### FastMCP Cloud (Recommended)
- ✅ Zero infrastructure management
- ✅ Built-in OAuth 2.1 authentication with PKCE
- ✅ Monitoring and health checks
- ✅ Production-ready MCP 2025-03-26 compliance
- ✅ Server-Sent Events (SSE) for real-time updates

### Self-Hosted with HTTP Transport
- 🔒 **OAuth 2.1 + PKCE**: Full authentication flow
- 🌐 **HTTP+SSE Transport**: JSON-RPC 2.0 over HTTPS
- 🛡️ **Security Features**: Origin validation, secure sessions
- 🐳 **Container Support**: Docker with FastMCP framework

### Enterprise Integration
- 🏢 **ChatGPT Connectors**: Team/Enterprise plan integration
- 🔧 **Custom Deployment**: Self-hosted with OAuth
- 📊 **Audit & Compliance**: Full request logging

**Production Requirements** (Based on MCP Specification):
- HTTPS endpoints mandatory
- Origin header validation for DNS rebinding protection
- Secure session ID generation (UUIDs)
- Bearer token authentication on all requests

See [`deploy/README.md`](deploy/README.md) for detailed deployment guides.

## 🔒 Security Features (MCP 2025-03-26 Compliant)

- 🔐 **OAuth 2.1 with PKCE**: RFC-compliant authorization flows
- 🏢 **Dynamic Client Registration**: RFC7591 support for new clients
- 🔍 **Authorization Server Metadata**: RFC8414 endpoint discovery
- 🛡️ **DNS Rebinding Protection**: Origin header validation
- 🔒 **Secure Sessions**: Cryptographically secure UUID session IDs
- 🌐 **HTTPS Only**: All authorization endpoints encrypted
- 🚪 **Session Isolation**: Each Claude-Code session sandboxed
- 📝 **Audit Logging**: Complete MCP request/response tracking
- 🔄 **Token Rotation**: Access token expiration and refresh
- 🚫 **Command Validation**: Restrict dangerous operations

## 📱 Mobile Workflow Example

**Morning Commute:**
```
You: "Start a new session for my mobile app project"
ChatGPT: "Created session mobile-app_x7y8 in ~/projects/mobile-app"

You: "Tell it to run the test suite and fix any failures"
ChatGPT: "Message sent! The session is running tests..."
```

**Lunch Break:**
```
You: "How's the mobile app session doing?"
ChatGPT: "Session is active. Recent activity shows:
- Fixed 3 test failures ✅
- Updated component tests ✅
- Waiting for your input on TypeScript migration"

You: "Tell it to proceed with TypeScript migration"
ChatGPT: "Message sent! Session will begin TypeScript migration."
```

**End of Day:**
```
You: "Show me what the mobile session accomplished today"
ChatGPT: "Session mobile-app_x7y8 completed:
- Fixed all test failures
- Migrated 15 components to TypeScript
- Added new authentication module
- Session has been active for 8 hours"

You: "Great! Terminate that session"
ChatGPT: "✅ Session terminated. All work has been committed."
```

## 🎯 Roadmap

**v0.1.0** (Current)
- [x] Core MCP server with all 8 tools
- [x] Local supervisor with PTY management
- [x] FastMCP 2.12.4 integration (production-ready)
- [x] MCP 2025-03-26 specification compliance
- [x] OAuth 2.1 + PKCE authentication architecture
- [x] HTTP+SSE transport implementation
- [x] Comprehensive user journey testing (10 scenarios)

**v0.2.0** (Next)
- [ ] Enhanced error handling and recovery
- [ ] Session persistence across reboots
- [ ] Notification system for completed tasks
- [ ] Web dashboard for session monitoring

**v0.3.0** (Future)
- [ ] Multi-host support (control multiple Macs)
- [ ] Terminal playback and session recording
- [ ] Advanced session templates and presets
- [ ] Integration with CI/CD pipelines

## 🤝 Contributing

This is an open-source project designed for the Claude-Code community!

1. **Fork the repo**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Test your changes**: `python3 scripts/test-local.py`
4. **Commit with good messages**: Follow our commit message format
5. **Submit pull request**

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the Claude-Code community**

*Turn your iPhone into a remote control for your Mac's Claude-Code sessions.*