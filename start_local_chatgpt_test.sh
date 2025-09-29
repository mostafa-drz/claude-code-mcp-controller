#!/bin/bash

echo "🚀 Starting Local ChatGPT Testing Environment"
echo "=============================================="

# Check if FastMCP is installed
python3 -c "import fastmcp; print('✅ FastMCP available')" || {
    echo "❌ FastMCP not installed. Run: pip install fastmcp"
    exit 1
}

# Check if supervisor exists
if [ ! -f "supervisor/main.py" ]; then
    echo "❌ Supervisor not found. Make sure you're in the project root."
    exit 1
fi

echo "📍 Starting services..."

# Start supervisor in background
echo "🔧 Starting supervisor on localhost:8080..."
python3 supervisor/main.py &
SUPERVISOR_PID=$!

# Wait for supervisor to start
sleep 3

# Check if supervisor started
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ Supervisor running on localhost:8080"
else
    echo "⚠️  Supervisor may not be ready yet (that's OK)"
fi

# Set environment for local supervisor
export SUPERVISOR_URL="http://localhost:8080"

echo "🚀 Starting FastMCP server on port 8000..."
echo ""
echo "📍 Server URL: http://localhost:8000/mcp"
echo "🌐 Run in another terminal: ngrok http 8000"
echo "📱 Configure ChatGPT with: https://your-ngrok-url.ngrok-free.app/mcp"
echo ""
echo "🛑 Press Ctrl+C to stop all services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Start FastMCP server (this will block)
python3 -c "
from server import mcp
import os
import signal
import sys

def signal_handler(sig, frame):
    print('\n🛑 Shutting down FastMCP server...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print('✅ FastMCP server starting...')
print('📡 Endpoint: http://localhost:8000/mcp')
print('🔗 Ready for ChatGPT connection!')

try:
    mcp.run(transport='http', host='0.0.0.0', port=8000, path='/mcp')
except KeyboardInterrupt:
    print('\n🛑 Server stopped by user')
" &
MCP_PID=$!

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $SUPERVISOR_PID $MCP_PID 2>/dev/null
    echo "✅ Cleanup complete"
    exit
}

trap cleanup EXIT INT TERM

# Wait for either process to exit
wait