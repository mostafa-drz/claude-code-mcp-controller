#!/usr/bin/env python3
"""
Test script to demonstrate the Claude-Code MCP Controller

This script shows how to:
1. Create a new Claude-Code session via supervisor
2. Send commands to the session
3. Retrieve logs and status
4. Clean up the session

Run this after starting the supervisor: python3 -m supervisor.main
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, List

from config import config

async def test_supervisor():
    """Test the supervisor API directly"""
    
    async with aiohttp.ClientSession() as session:
        print("🧪 Testing Claude-Code MCP Controller Supervisor")
        print("=" * 50)
        
        # 1. Check supervisor health
        print("\n1. Checking supervisor health...")
        async with session.get(f"{config.SUPERVISOR_URL}/health") as resp:
            health = await resp.json()
            print(f"   ✅ Supervisor status: {health['status']}")
            print(f"   📊 Active sessions: {health['session_health']['active_sessions']}")
        
        # 2. List existing sessions
        print("\n2. Listing existing sessions...")
        async with session.get(f"{config.SUPERVISOR_URL}/sessions") as resp:
            sessions = await resp.json()
            print(f"   📋 Found {len(sessions['sessions'])} session(s)")
            for s in sessions['sessions']:
                print(f"   - {s['session_id']} ({s['status']})")
        
        # 3. Create a new test session
        print("\n3. Creating new test session...")
        session_data = {
            "name": "test-demo",
            "working_dir": "/tmp"
        }
        async with session.post(f"{config.SUPERVISOR_URL}/sessions", json=session_data) as resp:
            if resp.status == 201:
                result = await resp.json()
                session_id = result['session_id']
                print(f"   ✅ Created session: {session_id}")
            else:
                print(f"   ❌ Failed to create session: {resp.status}")
                return
        
        # 4. Send a command to the session
        print(f"\n4. Sending command to session {session_id}...")
        message_data = {"message": "echo 'Hello from Claude-Code MCP Controller!'"}
        async with session.post(f"{config.SUPERVISOR_URL}/sessions/{session_id}/message", json=message_data) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"   ✅ Message sent: {result['status']}")
            else:
                print(f"   ❌ Failed to send message: {resp.status}")
        
        # 5. Get session logs
        print(f"\n5. Retrieving logs from session {session_id}...")
        async with session.get(f"{config.SUPERVISOR_URL}/sessions/{session_id}/logs?lines=10") as resp:
            if resp.status == 200:
                result = await resp.json()
                logs = result.get('logs', [])
                print(f"   📝 Recent logs ({len(logs)} lines):")
                for log in logs[-5:]:  # Show last 5 lines
                    print(f"      {log}")
            else:
                print(f"   ❌ Failed to get logs: {resp.status}")
        
        # 6. Get session status
        print(f"\n6. Checking session status...")
        async with session.get(f"{config.SUPERVISOR_URL}/sessions/{session_id}/status") as resp:
            if resp.status == 200:
                status = await resp.json()
                print(f"   📊 Session status: {status['status']}")
                print(f"   🕒 Created: {status['created_at']}")
                print(f"   📁 Working dir: {status['working_dir']}")
                if 'memory_usage' in status:
                    print(f"   💾 Memory: {status['memory_usage']:.1f} MB")
            else:
                print(f"   ❌ Failed to get status: {resp.status}")
        
        # 7. Clean up - terminate session
        print(f"\n7. Cleaning up - terminating session {session_id}...")
        async with session.delete(f"{config.SUPERVISOR_URL}/sessions/{session_id}") as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"   ✅ Session terminated: {result['status']}")
            else:
                print(f"   ❌ Failed to terminate session: {resp.status}")
        
        print("\n🎉 Test completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Start MCP server: python3 start_mcp_server.py")
        print("   2. Connect ChatGPT to your MCP server")
        print("   3. Use ChatGPT to control Claude-Code sessions remotely!")

if __name__ == "__main__":
    try:
        asyncio.run(test_supervisor())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except aiohttp.ClientConnectorError:
        print("\n❌ Cannot connect to supervisor at http://localhost:8080")
        print("   Make sure to start the supervisor first:")
        print("   python3 -m supervisor.main")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
