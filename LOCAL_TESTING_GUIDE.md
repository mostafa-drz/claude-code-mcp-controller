# Local Testing Guide for FastMCP Server

You can test the FastMCP server locally in multiple ways before deploying to FastMCP Cloud.

## 🧪 Testing Methods

### Method 1: Direct STDIO Testing (Quickest)

Run the server directly and interact via STDIO:

```bash
# Start the server in STDIO mode (default)
python3 server.py
```

This will start the server and wait for JSON-RPC messages via standard input.

### Method 2: FastMCP Client Testing (Recommended)

Create a test client to interact with your server:

```python
# test_client.py
import asyncio
from fastmcp import Client

async def test_server():
    # Import your server
    from server import mcp

    # Connect directly to server instance (in-memory)
    async with Client(mcp) as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        # Test listing sessions
        result = await client.call_tool("list_sessions", {})
        print(f"List sessions result: {result}")

        # Test creating a session
        result = await client.call_tool("create_session", {
            "name": "test-session",
            "working_dir": "/tmp"
        })
        print(f"Create session result: {result}")

if __name__ == "__main__":
    asyncio.run(test_server())
```

Run it:
```bash
python3 test_client.py
```

### Method 3: HTTP Transport Testing

Test with HTTP transport for more realistic cloud simulation:

```python
# test_http.py
from server import mcp
import asyncio
from fastmcp import Client

async def start_http_server():
    # Start server in background
    server_task = asyncio.create_task(
        asyncio.to_thread(
            mcp.run,
            transport="http",
            host="127.0.0.1",
            port=8002,
            path="/mcp"
        )
    )

    # Give server time to start
    await asyncio.sleep(2)

    # Connect via HTTP
    async with Client("http://127.0.0.1:8002/mcp") as client:
        tools = await client.list_tools()
        print(f"Tools via HTTP: {[t.name for t in tools]}")

    server_task.cancel()

if __name__ == "__main__":
    asyncio.run(start_http_server())
```

### Method 4: Interactive Testing Script

I'll create a comprehensive test script for you:

```python
# interactive_test.py
import asyncio
from fastmcp import Client
from server import mcp

async def interactive_test():
    """Interactive testing of all MCP tools."""

    print("🧪 FastMCP Local Testing Interface")
    print("=" * 40)

    async with Client(mcp) as client:
        # Get available tools
        tools = await client.list_tools()
        print(f"\n📦 Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        print("\n" + "=" * 40)
        print("Testing each tool:\n")

        # 1. Test list_sessions
        print("1️⃣ Testing list_sessions...")
        result = await client.call_tool("list_sessions", {})
        print(f"   Result: {result.content[0].text if result.content else 'Empty'}")

        # 2. Test create_session (mock supervisor must be running)
        print("\n2️⃣ Testing create_session...")
        try:
            result = await client.call_tool("create_session", {
                "name": "test",
                "working_dir": "/tmp"
            })
            print(f"   Result: {result.content[0].text if result.content else 'Empty'}")
        except Exception as e:
            print(f"   ⚠️  Expected error (supervisor not running): {e}")

        # 3. Test other tools...
        # Add more tests as needed

        print("\n✅ Local testing complete!")

if __name__ == "__main__":
    asyncio.run(interactive_test())
```

### Method 5: Full Integration Test with Mock Supervisor

Test with the supervisor running:

```bash
# Terminal 1: Start the supervisor
python3 supervisor/main.py

# Terminal 2: Run test
python3 test_client.py
```

### Method 6: Using cURL for HTTP Testing

If running HTTP transport:

```bash
# Start server with HTTP
python3 -c "from server import mcp; mcp.run(transport='http', host='127.0.0.1', port=8002, path='/mcp')"

# In another terminal, test with curl
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
  }'
```

## 🎯 Quick Test Commands

### 1. Test Server Starts Successfully
```bash
timeout 5s python3 server.py
```

### 2. Test Import Works
```bash
python3 -c "from server import mcp; print(f'✅ Server ready: {mcp.name}')"
```

### 3. Test Pattern Validation
```bash
python3 pattern_validation.py
```

## 📋 Testing Checklist

Before deployment, ensure:

- [ ] Server starts without errors
- [ ] All 8 tools are registered
- [ ] Both resources are registered
- [ ] Can connect with FastMCP Client
- [ ] Error handling works correctly
- [ ] Logging outputs properly
- [ ] HTTP transport works (optional)

## 🚨 Common Issues

### Supervisor Not Running
Most tools will fail if the supervisor isn't running. This is expected. You can:
1. Start the supervisor: `python3 supervisor/main.py`
2. Or test with mock responses

### Port Already in Use
If testing HTTP and get port conflict:
```bash
# Kill process on port
lsof -ti:8002 | xargs kill -9
# Or use different port
```

### Import Errors
Ensure FastMCP is installed:
```bash
python3 -m pip install fastmcp
```

## 🎯 Recommended Test Flow

1. **Basic validation**: `python3 pattern_validation.py`
2. **Import test**: `python3 -c "from server import mcp"`
3. **Client test**: Create and run `test_client.py`
4. **Full integration**: Start supervisor and test all tools
5. **HTTP test**: Verify HTTP transport for cloud readiness

You can thoroughly test everything locally before deploying to FastMCP Cloud!