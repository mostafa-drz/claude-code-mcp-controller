# Claude-Code MCP Controller Development Guidelines

## 🚨 CRITICAL LEARNING: Never Make Assumptions About New Technologies

### Major Error Correction
**Initial Assumption**: FastMCP package doesn't exist on PyPI
**Reality**: FastMCP 2.12.4 is fully available and production-ready

**What went wrong:**
- Made assumptions without proper verification
- Used wrong pip environment initially
- Created mock implementations instead of using real FastMCP
- Misguided entire project architecture based on false assumptions

**Key Learning:** MCP and FastMCP are very new technologies. **ALWAYS**:
1. ✅ Ask clarifying questions instead of making assumptions
2. ✅ Verify package availability with multiple installation methods
3. ✅ Test in proper development environment
4. ✅ Research thoroughly before declaring something "doesn't exist"

## FastMCP Production Status (VERIFIED)

### ✅ Confirmed Available
- **Package**: `fastmcp==2.12.4` on PyPI
- **Installation**: `uv add fastmcp` or `pip install fastmcp`
- **CLI**: `fastmcp` command available
- **Documentation**: https://gofastmcp.com/

### ✅ Production Ready Features
- Enterprise authentication (Google, GitHub, WorkOS, Azure, Auth0)
- Deployment tools for cloud deployment
- Complete MCP server framework
- Testing utilities and client libraries

### ✅ Real Deployment Options
- FastMCP Cloud (managed hosting)
- Self-hosted with Docker
- Cloud providers (AWS, GCP, Azure)
- Local development with `fastmcp run server.py`

## Development Rules for New Technologies

### 🚫 NEVER ASSUME
- Package availability
- Feature capabilities
- Deployment options
- Integration possibilities

### ✅ ALWAYS VERIFY
- Test installations in clean environment
- Read official documentation completely
- Verify with multiple sources
- Ask user for clarification when uncertain

### ✅ ASK CLARIFYING QUESTIONS
Examples of what I should have asked:
- "Have you tested FastMCP installation recently?"
- "What deployment method are you targeting?"
- "Are there specific FastMCP features you want to use?"
- "Should I verify FastMCP availability before proceeding?"

## MCP Technology Stack (VERIFIED)

### Model Context Protocol (MCP)
- **Specification**: https://modelcontextprotocol.io/specification/2025-06-18
- **Purpose**: Connect LLMs to external data sources and tools
- **Protocol**: JSON-RPC 2.0 over STDIO/HTTP+SSE
- **Security**: OAuth 2.1 framework for HTTP servers

### FastMCP Framework
- **Repository**: https://github.com/jlowin/fastmcp
- **Current Version**: 2.12.4
- **Python Requirements**: ≥3.10
- **Production Features**: Auth, deployment, testing, monitoring

### ChatGPT Integration
- **Method**: MCP Connectors (Team/Enterprise plans)
- **Custom Connectors**: Can be built with MCP
- **Authentication**: OAuth flows supported
- **Access**: Admins can deploy custom connectors

## Architecture Analysis (Based on Real MCP Documentation)

### Production MCP Architecture Options

After analyzing real MCP specifications and FastMCP capabilities, there are multiple valid production architectures:

#### Option 1: FastMCP Cloud Deployment
```
ChatGPT → FastMCP Cloud → MCP Server → Supervisor → Claude-Code
          (managed hosting via gofastmcp.com)
```

#### Option 2: Self-Hosted with HTTP+SSE Transport
```
ChatGPT → Public Endpoint → FastMCP HTTP Server → Supervisor → Claude-Code
          (OAuth 2.1 + PKCE, JSON-RPC 2.0 over HTTP+SSE)
```

#### Option 3: Enterprise MCP Connector
```
ChatGPT → MCP Connector → Custom MCP Server → Supervisor → Claude-Code
          (Team/Enterprise plans with custom connectors)
```

### Key MCP Transport & Security Requirements (Verified from Specs)

**Transport Protocol (MCP 2025-03-26)**:
- JSON-RPC 2.0 over STDIO (preferred) or Streamable HTTP
- HTTP transport MUST validate Origin headers (DNS rebinding protection)
- Supports Server-Sent Events for streaming and server-to-client notifications
- Session management with secure session IDs (UUIDs recommended)

**Authorization (OAuth 2.1)**:
- PKCE required for all clients (public client model)
- Dynamic client registration (RFC7591) recommended
- Authorization Server Metadata discovery (RFC8414)
- Bearer token authentication on all requests
- Third-party authorization flow support (for enterprise integrations)

**Security Requirements**:
- HTTPS mandatory for all authorization endpoints
- Secure session ID generation (cryptographically secure UUIDs)
- Origin header validation for HTTP transport
- Token rotation and expiration enforcement
- Local binding (127.0.0.1 only) for development servers

## Project Status Update

### What Actually Works
1. ✅ **FastMCP Server**: Can be built with real FastMCP
2. ✅ **Cloud Deployment**: FastMCP Cloud available
3. ✅ **ChatGPT Integration**: MCP connectors support custom servers
4. ✅ **Local Supervisor**: Already implemented and working
5. ✅ **End-to-End Flow**: Completely possible with real stack

### Next Steps (Updated with Real MCP Knowledge)

**Production Deployment Decision Required**:
1. **Choose Architecture**: FastMCP Cloud vs Self-Hosted vs Enterprise Connector
2. **Implement OAuth 2.1**: With PKCE, dynamic client registration, metadata discovery
3. **Security Hardening**: Origin validation, secure session management, HTTPS enforcement
4. **Test Integration**: End-to-end ChatGPT → MCP Server → Claude-Code flow

**For Single-User Use Case** (most likely scenario):
- FastMCP Cloud deployment (simplest)
- No dynamic client registration needed (single known client)
- Bearer token authentication sufficient
- Focus on reliable HTTP+SSE transport implementation

## Communication Protocol

### Response Structure Rule
**ALWAYS start responses with clear action items first, then provide context:**

1. **Action Items** (what to do immediately)
2. **Brief explanation** (why)
3. **Technical details** (if needed)

Example:
```
## Action Required:
1. Run: python3 supervisor/main.py
2. Run: ngrok http 8080
3. Use ngrok URL in ChatGPT

## Why: FastMCP HTTP transport has bugs, supervisor works directly.
```

### When Working with New/Emerging Technologies Like MCP:

### Before Making Technical Decisions
- **Ask**: "Should I verify this technology's current status?"
- **Ask**: "Are there specific deployment requirements?"
- **Ask**: "Have you used this technology recently?"

### When Encountering Issues
- **Don't assume**: "This probably doesn't work"
- **Do investigate**: Test multiple approaches
- **Do ask**: "Can you help me understand why X failed?"

### When Documenting
- **Mark assumptions clearly**: "I believe X but need to verify"
- **Provide evidence**: "Tested with Y environment on Z date"
- **Update when wrong**: Correct documentation immediately

## Key Takeaways

1. **FastMCP is production-ready** - my initial assessment was completely wrong
2. **Always verify before assuming** - especially with new technologies
3. **Ask clarifying questions** - avoid making decisions based on assumptions
4. **Test in proper environment** - environment issues can mislead assessment
5. **Update documentation immediately** - when errors are discovered

This error could have led to:
- ❌ Building unnecessary mock implementations
- ❌ Missing real deployment opportunities
- ❌ Incorrect project architecture
- ❌ Wasted development time

**Going forward**: No assumptions about MCP/FastMCP capabilities without explicit verification and user confirmation.