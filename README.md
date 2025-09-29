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

### 1. Setup Local Supervisor

```bash
# Clone and setup
git clone <your-repo>
cd claude-code-mcp-controller

# Install dependencies (using Python 3.10+)
python3 -m pip install -r requirements.txt

# Run local tests (includes mock Claude-Code)
python3 scripts/test-local.py

# Start supervisor (runs on localhost:8080)
python3 supervisor/main.py
```

### 2. Deploy to FastMCP Cloud

```bash
# Install FastMCP CLI (verified production-ready)
python3 -m pip install fastmcp
# or using uv (recommended): uv add fastmcp

# Make your Mac accessible (development)
ngrok http 8080  # Note the public URL

# Deploy MCP server
export SUPERVISOR_URL="https://your-ngrok-url.ngrok.io"
fastmcp deploy server.py --config deploy/fastmcp-cloud.yml

# Get your MCP endpoint
fastmcp info claude-code-controller
```

### 3. Connect ChatGPT

**Option A: MCP Connectors (Team/Enterprise)**
1. Admin: Go to ChatGPT Organization Settings
2. Deploy custom MCP connector with your FastMCP endpoint
3. Users can access via standard ChatGPT interface

**Option B: Manual Integration (Development)**
1. Use your deployed MCP endpoint with compatible MCP clients
2. Test with: `fastmcp run server.py` locally first
3. Verify with: *"List my Claude-Code sessions"*

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

### Run Local Tests
```bash
# Full integration test suite
python3 scripts/test-local.py

# Unit tests
pytest tests/

# Test specific components
python3 supervisor/main.py  # Test supervisor
python3 server.py           # Test MCP server
```

### Development vs Production
- **Development**: Includes mock implementations for local testing
  - Mock Claude-Code: Simulates Claude-Code behavior when not installed
  - Local FastMCP: Test MCP server functionality without cloud deployment
- **Production**: Real FastMCP 2.12.4 framework with full MCP specification compliance
  - Full OAuth 2.1 authorization flows with PKCE
  - HTTP+SSE transport with Server-Sent Events
  - Production-grade security and session management

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