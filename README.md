# Claude-Code MCP Controller 🚀

A local MCP (Model Context Protocol) server for remotely controlling and monitoring Claude-Code sessions via ChatGPT mobile. Perfect for mobile workflows, remote development, and managing multiple coding sessions from anywhere.

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
│   ChatGPT       │◄──►│   Local MCP      │◄──►│  Mac Supervisor │
│   Mobile App    │    │   + ngrok tunnel │    │  (Local Agent) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                       HTTPS via ngrok                   │
                       No Authentication                 ▼
                       (until OpenAI fixes OAuth)    ┌─────────────────┐
                                                     │ Existing Claude │
                                                     │ Sessions (PTYs) │
                                                     │ • session_1     │
                                                     │ • session_2     │
                                                     │ • session_N     │
                                                     └─────────────────┘
```

## 🚀 Quick Start

### ⚡ One-Command Setup (Recommended)

```bash
# Clone and setup everything
git clone <your-repo>
cd claude-code-mcp-controller
make setup

# Add session creation alias to your shell
echo "alias cs='claude_session() { tmux new-session -d -s \"claude-\${1:-session}\" -c \"\${2:-\$(pwd)}\" \"claude\" && echo \"✅ Started claude-\$1\"; }; claude_session'" >> ~/.zshrc
source ~/.zshrc

# Create your first Claude session
cs myproject
```

### ⚙️ Configuration (Optional)

The system uses sensible defaults, but you can customize settings:

```bash
# Copy example config
cp env.example .env

# Edit as needed (optional)
nano .env
```

**Key settings:**
- `SUPERVISOR_PORT=8080` - Supervisor HTTP server port
- `MCP_PORT=8000` - MCP server port for ChatGPT
- `NGROK_PORT=8000` - Port for ngrok tunnel
- `LOG_LEVEL=INFO` - Logging level (DEBUG, INFO, WARNING, ERROR)

### 🔧 Essential Make Commands

```bash
# Show available commands
make help

# Complete project setup
make setup

# Start services
make run-supervisor    # Start supervisor
make run-server        # Start MCP server
make ngrok             # Start ngrok tunnel for ChatGPT (requires ngrok installed)

# Development
make test              # Test the system
make format            # Format code
make lint              # Lint code

# Cleanup
make clean             # Clean up files
```

### 🚀 Creating & Managing Claude Sessions

The supervisor discovers and manages tmux sessions with names starting with `claude-`. You can create sessions manually or via ChatGPT.

#### Quick Setup: Shell Alias (Recommended)

Add this alias to your shell for easy session creation:

```bash
# Add to ~/.zshrc or ~/.bashrc
alias cs='claude_session() {
    local name="${1:-session}"
    local dir="${2:-$(pwd)}"
    tmux new-session -d -s "claude-$name" -c "$dir" "claude" &&
    echo "✅ Started claude-$name in $dir"
    tmux list-sessions | grep "claude-$name"
}; claude_session'

# Reload your shell config
source ~/.zshrc  # or ~/.bashrc
```

**Usage:**
```bash
# Create a session in current directory
cs myproject

# Create a session in specific directory
cs webapp ~/projects/webapp

# List all Claude sessions
tmux list-sessions | grep claude-

# Attach to a session to see what's happening
tmux attach -t claude-myproject
# (Detach with Ctrl+B, then D)

# Kill a session when done
tmux kill-session -t claude-myproject
```

#### Via ChatGPT (Once Connected)
```bash
# 1. Start supervisor (in one terminal)
make run-supervisor

# 2. Start MCP server (in another terminal)  
make run-server

# 3. Connect ChatGPT to your MCP server
# 4. Use ChatGPT commands:
```

**ChatGPT Commands:**
```
"Create a new Claude-Code session called 'my-project'"
"List my active sessions"
"Send message to session 'my-project': 'ls -la'"
"Show me logs from session 'my-project'"
"Terminate session 'my-project'"
```

#### Via Direct HTTP API
```bash
# Create session
curl -X POST http://localhost:8080/sessions \
  -H "Content-Type: application/json" \
  -d '{"name": "test-session", "working_dir": "/path/to/project"}'

# List sessions
curl http://localhost:8080/sessions

# Send message
curl -X POST http://localhost:8080/sessions/SESSION_ID/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Claude-Code!"}'

# Get logs
curl http://localhost:8080/sessions/SESSION_ID/logs

# Terminate session
curl -X DELETE http://localhost:8080/sessions/SESSION_ID
```

### 1. Test Locally with ChatGPT (Recommended)

```bash
# Clone and setup
git clone <your-repo>
cd claude-code-mcp-controller
make setup

# Start supervisor (Terminal 1)
make run-supervisor

# Start MCP server (Terminal 2)
make run-server

# Start ngrok tunnel (Terminal 3)
make ngrok

# Test the system (Terminal 4)
make test
```

**Configure ChatGPT:**
- Add MCP connector: `https://your-ngrok-url.ngrok.app` (root path, no `/mcp` suffix)
- Test: *"What Claude-Code tools are available?"*

### 2. Local Development Setup (Current Approach)

**Why Local over Cloud:**
- Need access to your Mac's existing Claude sessions
- Supervisor must run locally to manage local processes
- Cloud deployment can't control local Mac sessions

**Current Status:**
- ✅ Local MCP server working with FastMCP 2.12.4
- ✅ ngrok tunnel for ChatGPT connectivity
- ⏳ OAuth pending (ChatGPT OAuth currently has known issues)
- ⏳ Supervisor component for Claude session management

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
| `search` | Search sessions (ChatGPT requirement) | *"Find sessions with 'web-app' in name"* |
| `fetch` | Get session data (ChatGPT requirement) | *"Get full details for session X"* |

## 📋 Testing & Development

### 🎯 Local ChatGPT Testing (Recommended)

Test the **real end-to-end experience** with ChatGPT locally before deploying:

```bash
# Terminal 1: Start supervisor
make run-supervisor

# Terminal 2: Start MCP server
make run-server

# Terminal 3: Start ngrok tunnel
make ngrok

# Terminal 4: Test the system
make test
```

**Then connect ChatGPT:**
1. **Configure ChatGPT**: Add MCP connector with `https://your-ngrok-url.ngrok.app` (root path)
2. **Test mobile workflow**: Use ChatGPT mobile app to control Claude-Code remotely

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
# Test the system
make test

# Format code
make format

# Lint code
make lint
```

### Local vs Production Testing

| Testing Method | Purpose | When to Use |
|---------------|---------|-------------|
| **ChatGPT Local** | Real UX validation | Before deployment, mobile testing |
| **Automated Tests** | Code validation | Development, CI/CD |
| **FastMCP Cloud** | Production testing | Final validation |

**Priority**: Always test with **ChatGPT locally first** - it's your source of truth for user experience.

## 🚢 Deployment Approach

### Current: Local with ngrok (Recommended)
- ✅ **Direct Mac Access**: Control local Claude sessions
- ✅ **FastMCP 2.12.4**: Production-ready MCP framework
- ✅ **SSE Transport**: JSON-RPC 2.0 over HTTPS via ngrok
- ✅ **Ephemeral Security**: ngrok URLs expire when tunnel closes
- ⏳ **No Authentication**: Temporary until OpenAI fixes OAuth

### Authentication Status
**Current Reality:**
- ChatGPT requires OAuth for MCP connectors (per OpenAI docs)
- OAuth implementation is broken in ChatGPT (community confirmed)
- No authentication works as temporary solution
- Ephemeral ngrok URLs provide reasonable security for personal use

**Future:**
- OAuth 2.1 + PKCE implementation ready
- Will enable when OpenAI resolves ChatGPT OAuth issues

### Why Not Cloud Deployment?
Cloud deployment (FastMCP Cloud, etc.) **cannot solve the core use case**:
- Need local supervisor to access existing Claude sessions
- Sessions run as local processes on your Mac
- Remote server cannot control local Mac processes

## 🔒 Security Architecture & Session Management

### Why the Supervisor Only Manages Sessions It Creates

**Important**: The supervisor **only tracks sessions it creates** - this is intentional security design, not a limitation.

#### 🔒 Security Principles
- **Session Isolation**: Each session is sandboxed with controlled lifecycle
- **Process Ownership**: Only manages processes it spawns (prevents hijacking)
- **Secure IDs**: Cryptographically secure UUIDs for all session identifiers  
- **Audit Trail**: Complete tracking of session creation → management → termination
- **Least Privilege**: No automatic access to external processes

#### 🎯 What This Means
- ✅ **Safe**: Can't accidentally control random processes on your system
- ✅ **Predictable**: All sessions follow same security model
- ✅ **Auditable**: Complete history of session management
- ❌ **Convenient**: Won't auto-detect existing Claude-Code sessions

#### 🔄 Architecture Flow
```
ChatGPT → MCP Server → Supervisor → SessionManager → ClaudeWrapper → Claude-Code Process
```
Each layer adds security controls and isolation.

### Security Features (MCP 2025-03-26 Compliant)

**Current Implementation:**
- 🔒 **Secure Sessions**: Cryptographically secure UUID session IDs
- 🌐 **HTTPS Only**: All endpoints encrypted via ngrok
- 🚪 **Session Isolation**: Each Claude-Code session sandboxed
- 📝 **Audit Logging**: Complete MCP request/response tracking
- 🚫 **Command Validation**: Restrict dangerous operations
- ⏳ **Ephemeral URLs**: ngrok tunnels expire when closed

**Ready for OAuth (when ChatGPT fixes issues):**
- 🔐 **OAuth 2.1 with PKCE**: RFC-compliant authorization flows
- 🏢 **Dynamic Client Registration**: RFC7591 support for new clients
- 🔍 **Authorization Server Metadata**: RFC8414 endpoint discovery
- 🛡️ **DNS Rebinding Protection**: Origin header validation
- 🔄 **Token Rotation**: Access token expiration and refresh

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
- [x] Core MCP server with 10 tools (8 session + 2 ChatGPT-required)
- [x] FastMCP 2.12.4 integration (production-ready)
- [x] MCP 2025-03-26 specification compliance
- [x] HTTP+SSE transport implementation
- [x] ngrok tunnel integration for ChatGPT
- [x] No-auth implementation (temporary solution)
- [ ] Local supervisor with PTY management (next phase)
- [ ] OAuth 2.1 + PKCE authentication (pending OpenAI fixes)

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
3. **Setup and test**: `make setup && make test`
4. **Format and lint**: `make format && make lint`
5. **Commit with good messages**: Follow our commit message format
6. **Submit pull request**

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the Claude-Code community**

*Turn your iPhone into a remote control for your Mac's Claude-Code sessions.*