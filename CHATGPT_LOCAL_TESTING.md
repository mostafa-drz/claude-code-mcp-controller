# ChatGPT Local Testing Guide

Test your FastMCP server locally with **real ChatGPT** before deploying to FastMCP Cloud.

## 🎯 Local ChatGPT Testing Setup

### Step 1: Start Local HTTP Server

```bash
# Terminal 1: Start FastMCP server with HTTP transport
python3 -c "
from server import mcp
print('🚀 Starting FastMCP server for ChatGPT local testing...')
print('📍 Server will be available at: http://localhost:8000/mcp')
print('🔗 Make this public with ngrok for ChatGPT access')
mcp.run(transport='http', host='0.0.0.0', port=8000, path='/mcp')
"
```

### Step 2: Make Server Public with ngrok

```bash
# Terminal 2: Expose local server to internet
ngrok http 8000

# This gives you a public URL like:
# https://abc123.ngrok-free.app
```

### Step 3: Start Supervisor (for full functionality)

```bash
# Terminal 3: Start supervisor for real Claude-Code sessions
python3 supervisor/main.py

# Update environment to point to local supervisor
export SUPERVISOR_URL="http://localhost:8080"
```

### Step 4: Configure ChatGPT MCP Connector

**Option A: ChatGPT Team/Enterprise (Recommended)**
1. Go to ChatGPT Organization Settings
2. Navigate to Connectors → Add Connector
3. Configure:
   - **Name**: `Claude-Code Controller (Local)`
   - **URL**: `https://your-ngrok-url.ngrok-free.app/mcp`
   - **Type**: HTTP transport
   - **Authentication**: None (for testing)

**Option B: Development Testing**
Use any MCP-compatible client that can connect to your ngrok URL.

## 🧪 ChatGPT Test Scenarios

### Test 1: Basic Tool Discovery
In ChatGPT, ask:
```
"What Claude-Code tools are available?"
```
**Expected**: List of 8 tools (list_sessions, create_session, etc.)

### Test 2: Session Management
```
"List my Claude-Code sessions"
```
**Expected**: Shows active sessions or "No sessions found" message

### Test 3: Create New Session
```
"Create a new Claude-Code session called 'test-project' in my home directory"
```
**Expected**: Success message with session details

### Test 4: Send Commands
```
"Tell the test-project session to list files in the current directory"
```
**Expected**: Command sent, can check logs

### Test 5: Get Session Logs
```
"Show me recent logs from the test-project session"
```
**Expected**: Formatted logs with recent activity

### Test 6: Error Handling
```
"Terminate a session called 'nonexistent'"
```
**Expected**: Helpful error message with suggestions

## 🚀 Quick Local Test Setup Script

Save this as `start_local_chatgpt_test.sh`:

```bash
#!/bin/bash

echo "🚀 Starting Local ChatGPT Testing Environment"
echo "=============================================="

# Check if FastMCP is installed
python3 -c "import fastmcp; print('✅ FastMCP available')" || {
    echo "❌ FastMCP not installed"
    exit 1
}

echo "📍 Starting services..."

# Start supervisor in background
echo "🔧 Starting supervisor..."
python3 supervisor/main.py &
SUPERVISOR_PID=$!

# Wait for supervisor to start
sleep 2

# Start FastMCP server
echo "🚀 Starting FastMCP server on port 8000..."
export SUPERVISOR_URL="http://localhost:8080"
python3 -c "
from server import mcp
print('✅ FastMCP server ready at http://localhost:8000/mcp')
print('🌐 Run: ngrok http 8000')
print('📱 Configure ChatGPT with your ngrok URL + /mcp')
print('🛑 Press Ctrl+C to stop')
mcp.run(transport='http', host='0.0.0.0', port=8000, path='/mcp')
" &
MCP_PID=$!

# Cleanup function
cleanup() {
    echo "🛑 Stopping services..."
    kill $SUPERVISOR_PID $MCP_PID 2>/dev/null
    exit
}

trap cleanup EXIT INT TERM

# Wait for user interrupt
wait
```

Make executable and run:
```bash
chmod +x start_local_chatgpt_test.sh
./start_local_chatgpt_test.sh
```

## 📱 Mobile Testing (The Real Test!)

This is the **ultimate test** - using ChatGPT mobile app:

1. **Start local setup** (script above)
2. **Configure ngrok URL** in ChatGPT
3. **Test mobile workflow**:
   ```
   "I'm away from my Mac - what Claude-Code sessions are running?"
   "Create a new session for my mobile app project"
   "Tell that session to run the test suite"
   "Check the logs - did the tests pass?"
   ```

## 🔧 Troubleshooting Local ChatGPT Testing

### ngrok Issues
```bash
# If ngrok is busy
pkill ngrok
ngrok http 8000

# Free plan limitations
# - Use ngrok's static domain if available
# - Restart ngrok if it times out
```

### ChatGPT Connection Issues
- **Check ngrok URL**: Must include `/mcp` path
- **Verify server**: `curl https://your-ngrok-url.ngrok-free.app/mcp`
- **Check logs**: FastMCP server shows connection attempts

### Supervisor Not Accessible
```bash
# Make sure supervisor is accessible
curl http://localhost:8080/health

# If issues, check supervisor logs
```

## ✅ Success Criteria for Local ChatGPT Testing

**Basic Functionality**:
- [ ] ChatGPT discovers all 8 tools
- [ ] Can list sessions (empty is OK)
- [ ] Can create new session
- [ ] Error messages are helpful

**Full Integration**:
- [ ] Can send commands to Claude-Code
- [ ] Can retrieve session logs
- [ ] Can handle interactive prompts
- [ ] Mobile ChatGPT app works smoothly

**Production Readiness**:
- [ ] Responses are mobile-friendly
- [ ] Error handling guides user
- [ ] Performance is acceptable
- [ ] All tools work as expected

## 🎯 Local vs Cloud Testing

| Feature | Local Testing | FastMCP Cloud |
|---------|---------------|---------------|
| **Speed** | ⚡ Instant changes | ⏳ Deploy delay |
| **Debugging** | 🔍 Full logs | 📊 Limited logs |
| **URL** | 🌐 ngrok (temporary) | 🌍 Permanent |
| **Reliability** | ⚠️ ngrok limits | ✅ Production |
| **ChatGPT Setup** | 🔧 Manual config | 🚀 One-time setup |

## 📋 Ready to Test with ChatGPT?

Your FastMCP server is **ready for local ChatGPT testing**:

1. ✅ **HTTP transport implemented**
2. ✅ **Proper `/mcp` endpoint**
3. ✅ **All 8 tools registered**
4. ✅ **Error handling optimized for ChatGPT**
5. ✅ **Mobile-friendly responses**

**Run the setup script and connect ChatGPT to test the real user experience!**