#!/usr/bin/env python3
"""
Local testing script for the Claude-Code MCP Controller.

This script helps test the complete system locally before deployment.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
import aiohttp
import subprocess
import signal
import os

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from supervisor.main import SupervisorServer


class LocalTester:
    """Test the complete MCP controller system locally."""

    def __init__(self):
        self.supervisor_process = None
        self.supervisor_server = None

    async def start_supervisor(self):
        """Start the supervisor server."""
        print("🚀 Starting supervisor server...")

        self.supervisor_server = SupervisorServer(host="localhost", port=8080)
        await self.supervisor_server.start()

        print("✅ Supervisor server started on http://localhost:8080")

    async def test_supervisor_health(self):
        """Test supervisor health endpoint."""
        print("\n🔍 Testing supervisor health...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8080/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Health check passed: {data['status']}")
                        return True
                    else:
                        print(f"❌ Health check failed: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

    async def test_session_creation(self):
        """Test creating a Claude-Code session."""
        print("\n🔍 Testing session creation...")

        try:
            async with aiohttp.ClientSession() as session:
                payload = {"name": "test", "working_dir": str(project_root)}

                async with session.post(
                    "http://localhost:8080/sessions",
                    json=payload
                ) as response:
                    if response.status == 201:
                        data = await response.json()
                        session_id = data.get("session_id")
                        print(f"✅ Session created: {session_id}")
                        return session_id
                    else:
                        error_text = await response.text()
                        print(f"❌ Session creation failed: {response.status} - {error_text}")
                        return None

        except Exception as e:
            print(f"❌ Session creation error: {e}")
            return None

    async def test_session_list(self):
        """Test listing sessions."""
        print("\n🔍 Testing session listing...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8080/sessions") as response:
                    if response.status == 200:
                        data = await response.json()
                        sessions = data.get("sessions", [])
                        print(f"✅ Found {len(sessions)} sessions")
                        for s in sessions:
                            print(f"   - {s.get('session_id')}: {s.get('status')}")
                        return sessions
                    else:
                        print(f"❌ Session listing failed: {response.status}")
                        return []

        except Exception as e:
            print(f"❌ Session listing error: {e}")
            return []

    async def test_send_message(self, session_id: str):
        """Test sending a message to a session."""
        print(f"\n🔍 Testing message sending to {session_id}...")

        try:
            async with aiohttp.ClientSession() as session:
                payload = {"message": "help"}

                async with session.post(
                    f"http://localhost:8080/sessions/{session_id}/message",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Message sent successfully")
                        print(f"   Response: {data.get('immediate_response', 'No immediate response')[:100]}...")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ Message sending failed: {response.status} - {error_text}")
                        return False

        except Exception as e:
            print(f"❌ Message sending error: {e}")
            return False

    async def test_get_logs(self, session_id: str):
        """Test getting logs from a session."""
        print(f"\n🔍 Testing log retrieval from {session_id}...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://localhost:8080/sessions/{session_id}/logs?lines=10"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logs = data.get("logs", [])
                        print(f"✅ Retrieved {len(logs)} log lines")
                        for log in logs[-3:]:  # Show last 3 lines
                            print(f"   {log}")
                        return True
                    else:
                        print(f"❌ Log retrieval failed: {response.status}")
                        return False

        except Exception as e:
            print(f"❌ Log retrieval error: {e}")
            return False

    async def test_mcp_server_connection(self):
        """Test MCP server connectivity to supervisor."""
        print("\n🔍 Testing MCP server connection...")

        try:
            # Set environment variable for supervisor URL
            # Use default config values

            # Import and test MCP server functions
            from server import supervisor_request

            # Test health endpoint
            health_data = await supervisor_request("GET", "/health")
            print(f"✅ MCP server can connect to supervisor")
            print(f"   Supervisor status: {health_data.get('status')}")
            return True

        except Exception as e:
            print(f"❌ MCP server connection error: {e}")
            return False

    async def cleanup_sessions(self):
        """Clean up test sessions."""
        print("\n🧹 Cleaning up test sessions...")

        sessions = await self.test_session_list()
        for session_data in sessions:
            session_id = session_data.get("session_id")
            if session_id and "test" in session_id:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.delete(
                            f"http://localhost:8080/sessions/{session_id}"
                        ) as response:
                            if response.status == 200:
                                print(f"✅ Cleaned up session: {session_id}")
                            else:
                                print(f"⚠️ Failed to clean up session: {session_id}")
                except Exception as e:
                    print(f"⚠️ Error cleaning up session {session_id}: {e}")

    async def run_tests(self):
        """Run all tests."""
        print("🧪 Starting Claude-Code MCP Controller Local Tests\n")

        tests_passed = 0
        total_tests = 0

        try:
            # Start supervisor
            await self.start_supervisor()

            # Wait a moment for startup
            await asyncio.sleep(2)

            # Test supervisor health
            total_tests += 1
            if await self.test_supervisor_health():
                tests_passed += 1

            # Test session creation
            total_tests += 1
            session_id = await self.test_session_creation()
            if session_id:
                tests_passed += 1

                # Test message sending
                total_tests += 1
                if await self.test_send_message(session_id):
                    tests_passed += 1

                # Wait for response
                await asyncio.sleep(2)

                # Test log retrieval
                total_tests += 1
                if await self.test_get_logs(session_id):
                    tests_passed += 1

            # Test session listing
            total_tests += 1
            if await self.test_session_list():
                tests_passed += 1

            # Test MCP server connection
            total_tests += 1
            if await self.test_mcp_server_connection():
                tests_passed += 1

            # Cleanup
            await self.cleanup_sessions()

        except KeyboardInterrupt:
            print("\n⏹️  Tests interrupted by user")
        except Exception as e:
            print(f"\n❌ Test suite error: {e}")
        finally:
            if self.supervisor_server:
                await self.supervisor_server.shutdown()

        # Results
        print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")

        if tests_passed == total_tests:
            print("🎉 All tests passed! The system is ready for deployment.")
            return True
        else:
            print("⚠️ Some tests failed. Please check the issues above.")
            return False


async def main():
    """Main function."""
    tester = LocalTester()
    success = await tester.run_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())