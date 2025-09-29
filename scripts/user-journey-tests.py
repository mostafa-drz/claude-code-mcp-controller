#!/usr/bin/env python3
"""
Comprehensive User Journey Testing for Claude-Code MCP Controller

Tests the top 10 user journey branches to identify UX gaps and improvement opportunities.
This simulates real-world usage patterns and edge cases.
"""

import asyncio
import json
import sys
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import aiohttp

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from supervisor.main import SupervisorServer


class UserJourneyTester:
    """Test comprehensive user journeys to identify UX gaps."""

    def __init__(self):
        self.supervisor_server = None
        self.test_results = {}
        self.ux_issues = []
        self.session_ids = []

    async def start_supervisor(self):
        """Start the supervisor server."""
        print("🚀 Starting supervisor for user journey testing...")
        self.supervisor_server = SupervisorServer(host="localhost", port=8080)
        await self.supervisor_server.start()
        await asyncio.sleep(2)  # Give server time to start

    async def cleanup_supervisor(self):
        """Clean up supervisor and sessions."""
        if self.supervisor_server:
            await self.supervisor_server.shutdown()

    async def api_call(self, method: str, endpoint: str, **kwargs) -> Tuple[bool, Dict, float]:
        """Make API call and measure response time."""
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, f"http://localhost:8080{endpoint}", **kwargs) as response:
                    response_time = time.time() - start_time
                    if response.status < 400:
                        data = await response.json()
                        return True, data, response_time
                    else:
                        error_text = await response.text()
                        return False, {"error": error_text, "status": response.status}, response_time
        except Exception as e:
            response_time = time.time() - start_time
            return False, {"error": str(e)}, response_time

    def log_ux_issue(self, journey: str, issue: str, severity: str = "medium"):
        """Log a UX issue found during testing."""
        self.ux_issues.append({
            "journey": journey,
            "issue": issue,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })

    async def journey_1_first_time_user(self) -> Dict:
        """Journey 1: First-time user discovering the system."""
        journey = "first_time_user"
        print(f"\n🧪 Testing Journey 1: First-time user experience")

        results = {"success": True, "steps": [], "issues": []}

        # Step 1: Health check (user wants to verify system is working)
        print("  📋 Step 1: User checks if system is healthy")
        success, data, response_time = await self.api_call("GET", "/health")
        results["steps"].append({"step": "health_check", "success": success, "response_time": response_time})

        if not success:
            self.log_ux_issue(journey, "Health check failed - bad first impression", "high")
            results["success"] = False
        elif response_time > 2.0:
            self.log_ux_issue(journey, f"Health check too slow ({response_time:.2f}s) - impatient users will leave", "medium")

        # Step 2: List sessions (user expects to see empty list with helpful message)
        print("  📋 Step 2: User checks what sessions exist (expects none)")
        success, data, response_time = await self.api_call("GET", "/sessions")
        results["steps"].append({"step": "empty_session_list", "success": success, "response_time": response_time})

        if success and len(data.get("sessions", [])) == 0:
            # Good! But is there a helpful message for empty state?
            if "sessions" in data and not data.get("message"):
                self.log_ux_issue(journey, "Empty session list lacks helpful guidance for new users", "low")

        # Step 3: Try to create first session
        print("  📋 Step 3: User creates their first session")
        success, data, response_time = await self.api_call("POST", "/sessions", json={"name": "my-first-session"})
        results["steps"].append({"step": "first_session_creation", "success": success, "response_time": response_time})

        if success:
            session_id = data.get("session_id")
            self.session_ids.append(session_id)
            print(f"    ✅ Created session: {session_id}")
        else:
            self.log_ux_issue(journey, "First session creation failed - major blocker", "critical")
            results["success"] = False

        return results

    async def journey_2_power_user_multiple_sessions(self) -> Dict:
        """Journey 2: Power user managing multiple sessions simultaneously."""
        journey = "power_user_multiple"
        print(f"\n🧪 Testing Journey 2: Power user with multiple sessions")

        results = {"success": True, "steps": [], "issues": []}

        # Create multiple sessions quickly
        session_names = ["web-frontend", "api-backend", "mobile-app", "data-pipeline", "docs-site"]
        created_sessions = []

        print("  📋 Step 1: Rapidly creating 5 sessions")
        start_time = time.time()
        for name in session_names:
            success, data, response_time = await self.api_call("POST", "/sessions", json={"name": name})
            if success:
                created_sessions.append(data.get("session_id"))
                self.session_ids.append(data.get("session_id"))
            else:
                self.log_ux_issue(journey, f"Failed to create session '{name}' - system doesn't handle rapid creation well", "high")

        total_creation_time = time.time() - start_time
        results["steps"].append({"step": "rapid_session_creation", "success": len(created_sessions) == 5, "total_time": total_creation_time})

        if total_creation_time > 30:
            self.log_ux_issue(journey, f"Creating 5 sessions took {total_creation_time:.1f}s - too slow for power users", "medium")

        # Step 2: List all sessions and check response format
        print("  📋 Step 2: Viewing all sessions at once")
        success, data, response_time = await self.api_call("GET", "/sessions")
        results["steps"].append({"step": "view_multiple_sessions", "success": success, "response_time": response_time})

        if success:
            sessions = data.get("sessions", [])
            if len(sessions) != len(created_sessions):
                self.log_ux_issue(journey, "Session list doesn't match created sessions - data consistency issue", "high")

            # Check if sessions have useful information for power users
            for session in sessions:
                if not session.get("last_activity"):
                    self.log_ux_issue(journey, "Sessions missing last_activity timestamp - hard to manage multiple sessions", "medium")
                if not session.get("working_dir"):
                    self.log_ux_issue(journey, "Sessions missing working directory - confusing for project management", "low")

        # Step 3: Send messages to multiple sessions simultaneously
        print("  📋 Step 3: Sending commands to multiple sessions")
        commands = ["help", "status", "echo test", "wait", "status"]

        for i, session_id in enumerate(created_sessions[:3]):  # Test first 3 sessions
            command = commands[i % len(commands)]
            success, data, response_time = await self.api_call("POST", f"/sessions/{session_id}/message", json={"message": command})
            if not success:
                self.log_ux_issue(journey, f"Failed to send message to session {session_id} - unreliable for power users", "high")

        return results

    async def journey_3_mobile_user_checking_progress(self) -> Dict:
        """Journey 3: Mobile user checking progress while away from computer."""
        journey = "mobile_progress_check"
        print(f"\n🧪 Testing Journey 3: Mobile user checking progress")

        results = {"success": True, "steps": [], "issues": []}

        # Simulate mobile constraints: slower network, limited bandwidth
        slow_timeout = 10  # Mobile users are more patient but connection is slower

        # Step 1: Quick status check
        print("  📋 Step 1: Quick status overview (mobile user wants fast info)")
        success, data, response_time = await self.api_call("GET", "/sessions")
        results["steps"].append({"step": "mobile_status_check", "success": success, "response_time": response_time})

        if response_time > 5.0:
            self.log_ux_issue(journey, f"Session list too slow for mobile ({response_time:.2f}s)", "high")

        # Step 2: Get logs from active session
        if self.session_ids:
            session_id = self.session_ids[0]
            print("  📋 Step 2: Getting recent logs (mobile user wants quick context)")
            success, data, response_time = await self.api_call("GET", f"/sessions/{session_id}/logs?lines=10")
            results["steps"].append({"step": "mobile_log_check", "success": success, "response_time": response_time})

            if success:
                logs = data.get("logs", [])
                if len(logs) == 0:
                    self.log_ux_issue(journey, "No logs available - mobile user can't understand what happened", "medium")
                else:
                    # Check if logs are mobile-friendly (not too long)
                    for log in logs:
                        if len(log) > 200:
                            self.log_ux_issue(journey, "Log lines too long for mobile viewing", "low")
                            break

        # Step 3: Send simple command and wait for result
        if self.session_ids:
            session_id = self.session_ids[0]
            print("  📋 Step 3: Sending simple status command from mobile")
            success, data, response_time = await self.api_call("POST", f"/sessions/{session_id}/message", json={"message": "status"})
            results["steps"].append({"step": "mobile_command", "success": success, "response_time": response_time})

            if success:
                # Wait a bit and check logs again
                await asyncio.sleep(3)
                success2, data2, _ = await self.api_call("GET", f"/sessions/{session_id}/logs?lines=5")
                if success2:
                    logs = data2.get("logs", [])
                    # Check if the status command result is visible
                    status_found = any("status" in log.lower() or "active" in log.lower() for log in logs)
                    if not status_found:
                        self.log_ux_issue(journey, "Command result not immediately visible in logs - poor mobile feedback", "medium")

        return results

    async def journey_4_stuck_session_recovery(self) -> Dict:
        """Journey 4: User dealing with a stuck session that needs prompt response."""
        journey = "stuck_session_recovery"
        print(f"\n🧪 Testing Journey 4: Stuck session recovery")

        results = {"success": True, "steps": [], "issues": []}

        # Create a session and simulate a stuck state
        print("  📋 Step 1: Creating session and simulating stuck state")
        success, data, response_time = await self.api_call("POST", "/sessions", json={"name": "test-stuck"})
        if not success:
            results["success"] = False
            return results

        session_id = data.get("session_id")
        self.session_ids.append(session_id)

        # Step 2: Check for prompts (should find none initially)
        print("  📋 Step 2: Checking for interactive prompts")
        success, data, response_time = await self.api_call("GET", "/prompts")
        results["steps"].append({"step": "check_prompts_empty", "success": success, "response_time": response_time})

        if success:
            prompts = data.get("prompts", [])
            if len(prompts) > 0:
                self.log_ux_issue(journey, "Found unexpected prompts in clean state", "medium")

        # Step 3: Send a command that might trigger a prompt (simulate)
        print("  📋 Step 3: Sending command that could trigger prompt")
        success, data, response_time = await self.api_call("POST", f"/sessions/{session_id}/message", json={"message": "help"})
        results["steps"].append({"step": "send_prompt_triggering_command", "success": success, "response_time": response_time})

        # Step 4: Try prompt detection multiple times (simulate polling behavior)
        print("  📋 Step 4: Polling for prompts (real user behavior)")
        prompt_checks = []
        for i in range(3):
            await asyncio.sleep(1)
            success, data, response_time = await self.api_call("GET", "/prompts")
            prompt_checks.append({"success": success, "response_time": response_time})

            if response_time > 2.0:
                self.log_ux_issue(journey, f"Prompt checking too slow ({response_time:.2f}s) - users will poll frequently", "medium")

        results["steps"].append({"step": "prompt_polling", "checks": prompt_checks})

        # Step 5: Test prompt response mechanism
        print("  📋 Step 5: Testing prompt response (even without real prompt)")
        success, data, response_time = await self.api_call("POST", f"/sessions/{session_id}/respond", json={"response": "y"})
        results["steps"].append({"step": "prompt_response", "success": success, "response_time": response_time})

        if not success:
            error_msg = data.get("error", "")
            if "not found" in error_msg.lower():
                # This is expected if no prompt exists, but error message should be clear
                if "no prompt" not in error_msg.lower() and "waiting" not in error_msg.lower():
                    self.log_ux_issue(journey, "Prompt response error message unclear - users won't understand what went wrong", "medium")

        return results

    async def journey_5_session_lifecycle_management(self) -> Dict:
        """Journey 5: Complete session lifecycle from creation to termination."""
        journey = "session_lifecycle"
        print(f"\n🧪 Testing Journey 5: Complete session lifecycle")

        results = {"success": True, "steps": [], "issues": []}

        # Step 1: Create session with custom directory
        print("  📋 Step 1: Creating session with custom working directory")
        custom_dir = "/tmp/test-project"
        success, data, response_time = await self.api_call("POST", "/sessions", json={
            "name": "lifecycle-test",
            "working_dir": custom_dir
        })
        results["steps"].append({"step": "create_with_custom_dir", "success": success, "response_time": response_time})

        if not success:
            self.log_ux_issue(journey, "Cannot create session with custom directory - limits usefulness", "high")
            results["success"] = False
            return results

        session_id = data.get("session_id")
        self.session_ids.append(session_id)

        # Step 2: Get detailed session status
        print("  📋 Step 2: Getting detailed session information")
        success, data, response_time = await self.api_call("GET", f"/sessions/{session_id}/status")
        results["steps"].append({"step": "get_detailed_status", "success": success, "response_time": response_time})

        if success:
            # Check if status contains useful information
            required_fields = ["session_id", "status", "working_dir", "created_at"]
            for field in required_fields:
                if field not in data:
                    self.log_ux_issue(journey, f"Session status missing {field} - incomplete information", "medium")

            # Check working directory is correct
            if data.get("working_dir") != custom_dir:
                self.log_ux_issue(journey, "Custom working directory not preserved - data consistency issue", "high")

        # Step 3: Send multiple commands in sequence
        print("  📋 Step 3: Sending sequence of commands")
        commands = ["help", "status", "echo 'testing sequence'"]
        for i, cmd in enumerate(commands):
            success, data, response_time = await self.api_call("POST", f"/sessions/{session_id}/message", json={"message": cmd})
            if not success:
                self.log_ux_issue(journey, f"Command {i+1} failed in sequence - unreliable workflow", "high")
            await asyncio.sleep(0.5)  # Small delay between commands

        # Step 4: Monitor logs over time
        print("  📋 Step 4: Monitoring log accumulation")
        initial_success, initial_data, _ = await self.api_call("GET", f"/sessions/{session_id}/logs?lines=50")
        await asyncio.sleep(2)
        final_success, final_data, _ = await self.api_call("GET", f"/sessions/{session_id}/logs?lines=50")

        if initial_success and final_success:
            initial_logs = len(initial_data.get("logs", []))
            final_logs = len(final_data.get("logs", []))
            if final_logs <= initial_logs:
                self.log_ux_issue(journey, "Logs not accumulating properly - users can't track progress", "medium")

        # Step 5: Graceful termination
        print("  📋 Step 5: Gracefully terminating session")
        success, data, response_time = await self.api_call("DELETE", f"/sessions/{session_id}")
        results["steps"].append({"step": "graceful_termination", "success": success, "response_time": response_time})

        if success:
            # Verify session is really gone
            await asyncio.sleep(1)
            success2, data2, _ = await self.api_call("GET", f"/sessions/{session_id}/status")
            if success2:
                self.log_ux_issue(journey, "Session still exists after termination - cleanup issue", "high")
        else:
            self.log_ux_issue(journey, "Cannot terminate session - users stuck with zombie sessions", "critical")

        return results

    async def journey_6_error_handling_resilience(self) -> Dict:
        """Journey 6: Testing error handling and system resilience."""
        journey = "error_handling"
        print(f"\n🧪 Testing Journey 6: Error handling and resilience")

        results = {"success": True, "steps": [], "issues": []}

        # Step 1: Try to access non-existent session
        print("  📋 Step 1: Accessing non-existent session")
        fake_id = "nonexistent_session_12345"
        success, data, response_time = await self.api_call("GET", f"/sessions/{fake_id}/status")
        results["steps"].append({"step": "nonexistent_session", "success": success, "response_time": response_time})

        if success:
            self.log_ux_issue(journey, "Non-existent session returned success - should return 404", "high")
        else:
            # Check error message quality
            error_msg = data.get("error", "")
            if not error_msg or "not found" not in error_msg.lower():
                self.log_ux_issue(journey, "Poor error message for non-existent session", "medium")

        # Step 2: Send invalid data
        print("  📋 Step 2: Sending invalid data formats")
        test_cases = [
            ("POST", "/sessions", {"name": None}),  # Invalid name
            ("POST", "/sessions", {"working_dir": "/invalid/path/that/does/not/exist"}),  # Invalid directory
            ("POST", "/sessions", "invalid json"),  # Invalid JSON
        ]

        for method, endpoint, payload in test_cases:
            if isinstance(payload, str):
                # Raw string data
                success, data, response_time = await self.api_call(method, endpoint, data=payload)
            else:
                success, data, response_time = await self.api_call(method, endpoint, json=payload)

            if success:
                self.log_ux_issue(journey, f"Invalid data accepted: {payload} - should validate input", "medium")

        # Step 3: Test rate limiting behavior
        print("  📋 Step 3: Testing rapid requests (rate limiting)")
        rapid_requests = []
        start_time = time.time()

        for i in range(10):
            success, data, response_time = await self.api_call("GET", "/health")
            rapid_requests.append({"success": success, "response_time": response_time})

        total_time = time.time() - start_time
        avg_response_time = sum(r["response_time"] for r in rapid_requests) / len(rapid_requests)

        if avg_response_time > 1.0:
            self.log_ux_issue(journey, f"System slows down under rapid requests ({avg_response_time:.2f}s avg)", "medium")

        results["steps"].append({"step": "rapid_requests", "total_time": total_time, "avg_response_time": avg_response_time})

        return results

    async def journey_7_concurrent_user_simulation(self) -> Dict:
        """Journey 7: Simulate multiple users accessing the system simultaneously."""
        journey = "concurrent_users"
        print(f"\n🧪 Testing Journey 7: Concurrent user simulation")

        results = {"success": True, "steps": [], "issues": []}

        # Simulate 3 concurrent users doing different things
        async def user_1_workflow():
            """User 1: Creates sessions and sends commands"""
            user_results = []
            for i in range(3):
                success, data, response_time = await self.api_call("POST", "/sessions", json={"name": f"user1-session-{i}"})
                user_results.append({"action": "create_session", "success": success, "response_time": response_time})
                if success:
                    self.session_ids.append(data.get("session_id"))
                await asyncio.sleep(0.1)
            return user_results

        async def user_2_workflow():
            """User 2: Monitors sessions and gets logs"""
            user_results = []
            for i in range(5):
                success, data, response_time = await self.api_call("GET", "/sessions")
                user_results.append({"action": "list_sessions", "success": success, "response_time": response_time})
                await asyncio.sleep(0.2)
            return user_results

        async def user_3_workflow():
            """User 3: Sends messages to existing sessions"""
            user_results = []
            if self.session_ids:
                session_id = self.session_ids[0]
                for i in range(4):
                    success, data, response_time = await self.api_call("POST", f"/sessions/{session_id}/message", json={"message": f"test-{i}"})
                    user_results.append({"action": "send_message", "success": success, "response_time": response_time})
                    await asyncio.sleep(0.3)
            return user_results

        print("  📋 Running concurrent user workflows...")
        start_time = time.time()

        user1_results, user2_results, user3_results = await asyncio.gather(
            user_1_workflow(),
            user_2_workflow(),
            user_3_workflow(),
            return_exceptions=True
        )

        total_time = time.time() - start_time
        results["steps"].append({"step": "concurrent_execution", "total_time": total_time})

        # Analyze results for concurrency issues
        all_results = []
        if isinstance(user1_results, list):
            all_results.extend(user1_results)
        if isinstance(user2_results, list):
            all_results.extend(user2_results)
        if isinstance(user3_results, list):
            all_results.extend(user3_results)

        failed_operations = [r for r in all_results if not r.get("success", True)]
        if len(failed_operations) > 0:
            self.log_ux_issue(journey, f"{len(failed_operations)} operations failed under concurrent load", "high")

        slow_operations = [r for r in all_results if r.get("response_time", 0) > 3.0]
        if len(slow_operations) > 0:
            self.log_ux_issue(journey, f"{len(slow_operations)} operations were slow under concurrent load", "medium")

        return results

    async def journey_8_data_consistency_validation(self) -> Dict:
        """Journey 8: Validate data consistency across operations."""
        journey = "data_consistency"
        print(f"\n🧪 Testing Journey 8: Data consistency validation")

        results = {"success": True, "steps": [], "issues": []}

        # Step 1: Create session and immediately check if it appears in lists
        print("  📋 Step 1: Create session and verify immediate visibility")
        success, data, response_time = await self.api_call("POST", "/sessions", json={"name": "consistency-test"})
        if not success:
            results["success"] = False
            return results

        session_id = data.get("session_id")
        self.session_ids.append(session_id)

        # Immediately list sessions
        success2, data2, _ = await self.api_call("GET", "/sessions")
        if success2:
            sessions = data2.get("sessions", [])
            session_found = any(s.get("session_id") == session_id for s in sessions)
            if not session_found:
                self.log_ux_issue(journey, "Newly created session not immediately visible in list", "high")

        # Step 2: Send message and verify it appears in logs
        print("  📋 Step 2: Send message and verify log consistency")
        test_message = f"consistency-test-{int(time.time())}"
        success, data, response_time = await self.api_call("POST", f"/sessions/{session_id}/message", json={"message": test_message})

        if success:
            # Wait a moment and check logs
            await asyncio.sleep(2)
            success2, data2, _ = await self.api_call("GET", f"/sessions/{session_id}/logs?lines=10")
            if success2:
                logs = data2.get("logs", [])
                message_found = any(test_message in log for log in logs)
                if not message_found:
                    self.log_ux_issue(journey, "Sent message not visible in logs - data consistency issue", "high")

        # Step 3: Rapid operations and consistency check
        print("  📋 Step 3: Rapid operations consistency test")
        operations = []
        for i in range(5):
            success, data, response_time = await self.api_call("POST", f"/sessions/{session_id}/message", json={"message": f"rapid-{i}"})
            operations.append({"success": success, "message": f"rapid-{i}"})

        # Check if all messages appear in logs
        await asyncio.sleep(3)
        success, data, _ = await self.api_call("GET", f"/sessions/{session_id}/logs?lines=20")
        if success:
            logs = " ".join(data.get("logs", []))
            missing_messages = []
            for op in operations:
                if op["success"] and op["message"] not in logs:
                    missing_messages.append(op["message"])

            if missing_messages:
                self.log_ux_issue(journey, f"Messages missing from logs: {missing_messages}", "medium")

        return results

    async def journey_9_performance_under_load(self) -> Dict:
        """Journey 9: Test performance characteristics under various loads."""
        journey = "performance_load"
        print(f"\n🧪 Testing Journey 9: Performance under load")

        results = {"success": True, "steps": [], "issues": []}

        # Step 1: Baseline performance
        print("  📋 Step 1: Measuring baseline performance")
        baseline_times = []
        for i in range(10):
            success, data, response_time = await self.api_call("GET", "/health")
            if success:
                baseline_times.append(response_time)

        avg_baseline = sum(baseline_times) / len(baseline_times) if baseline_times else 0
        results["steps"].append({"step": "baseline_performance", "avg_response_time": avg_baseline})

        # Step 2: Create many sessions
        print("  📋 Step 2: Creating multiple sessions for load testing")
        session_creation_times = []
        load_test_sessions = []

        for i in range(8):
            start_time = time.time()
            success, data, response_time = await self.api_call("POST", "/sessions", json={"name": f"load-test-{i}"})
            session_creation_times.append(response_time)

            if success:
                load_test_sessions.append(data.get("session_id"))
                self.session_ids.append(data.get("session_id"))

        if session_creation_times:
            avg_creation_time = sum(session_creation_times) / len(session_creation_times)
            max_creation_time = max(session_creation_times)

            if avg_creation_time > 5.0:
                self.log_ux_issue(journey, f"Session creation too slow under load ({avg_creation_time:.2f}s avg)", "medium")

            if max_creation_time > 10.0:
                self.log_ux_issue(journey, f"Worst session creation very slow ({max_creation_time:.2f}s)", "high")

        # Step 3: Concurrent operations on multiple sessions
        print("  📋 Step 3: Concurrent operations across sessions")

        async def send_messages_to_session(session_id, count=5):
            times = []
            for i in range(count):
                success, data, response_time = await self.api_call("POST", f"/sessions/{session_id}/message", json={"message": f"load-test-{i}"})
                times.append(response_time)
                await asyncio.sleep(0.1)
            return times

        if len(load_test_sessions) >= 3:
            concurrent_tasks = [
                send_messages_to_session(load_test_sessions[0]),
                send_messages_to_session(load_test_sessions[1]),
                send_messages_to_session(load_test_sessions[2])
            ]

            start_time = time.time()
            task_results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
            total_concurrent_time = time.time() - start_time

            # Analyze concurrent performance
            all_times = []
            for task_result in task_results:
                if isinstance(task_result, list):
                    all_times.extend(task_result)

            if all_times:
                avg_concurrent_time = sum(all_times) / len(all_times)
                if avg_concurrent_time > avg_baseline * 3:
                    self.log_ux_issue(journey, f"Performance degrades significantly under concurrent load", "medium")

        # Step 4: Memory usage implications (simulate)
        print("  📋 Step 4: Testing with many log retrievals")
        log_retrieval_times = []
        for session_id in load_test_sessions[:3]:
            success, data, response_time = await self.api_call("GET", f"/sessions/{session_id}/logs?lines=100")
            log_retrieval_times.append(response_time)

        if log_retrieval_times:
            avg_log_time = sum(log_retrieval_times) / len(log_retrieval_times)
            if avg_log_time > 2.0:
                self.log_ux_issue(journey, f"Log retrieval slow with multiple sessions ({avg_log_time:.2f}s)", "medium")

        return results

    async def journey_10_edge_cases_and_boundaries(self) -> Dict:
        """Journey 10: Test edge cases and boundary conditions."""
        journey = "edge_cases"
        print(f"\n🧪 Testing Journey 10: Edge cases and boundaries")

        results = {"success": True, "steps": [], "issues": []}

        # Step 1: Very long session names
        print("  📋 Step 1: Testing boundary conditions")
        long_name = "a" * 255  # Very long name
        success, data, response_time = await self.api_call("POST", "/sessions", json={"name": long_name})
        results["steps"].append({"step": "long_session_name", "success": success})

        if success:
            session_id = data.get("session_id")
            self.session_ids.append(session_id)
            # Check if long name is handled properly
            success2, data2, _ = await self.api_call("GET", f"/sessions/{session_id}/status")
            if success2 and len(data2.get("session_id", "")) > 100:
                self.log_ux_issue(journey, "Very long session names create unwieldy IDs", "low")

        # Step 2: Empty messages
        if self.session_ids:
            print("  📋 Step 2: Testing empty and whitespace messages")
            session_id = self.session_ids[0]

            edge_messages = ["", "   ", "\n\n", "\t"]
            for msg in edge_messages:
                success, data, response_time = await self.api_call("POST", f"/sessions/{session_id}/message", json={"message": msg})
                if success:
                    # Empty messages accepted - is this intentional?
                    if not msg.strip():
                        self.log_ux_issue(journey, "Empty/whitespace messages accepted - may cause confusion", "low")

        # Step 3: Very large log requests
        print("  📋 Step 3: Testing large log requests")
        if self.session_ids:
            session_id = self.session_ids[0]
            success, data, response_time = await self.api_call("GET", f"/sessions/{session_id}/logs?lines=10000")
            results["steps"].append({"step": "large_log_request", "success": success, "response_time": response_time})

            if success and response_time > 5.0:
                self.log_ux_issue(journey, f"Large log requests very slow ({response_time:.2f}s)", "medium")

            if success:
                logs = data.get("logs", [])
                total_size = sum(len(log) for log in logs)
                if total_size > 1000000:  # 1MB
                    self.log_ux_issue(journey, f"Large log responses ({total_size} bytes) may cause memory issues", "medium")

        # Step 4: Special characters in inputs
        print("  📋 Step 4: Testing special characters")
        special_chars_name = "test-émojis-🚀-unicode-中文"
        success, data, response_time = await self.api_call("POST", "/sessions", json={"name": special_chars_name})
        if success:
            self.session_ids.append(data.get("session_id"))
        else:
            self.log_ux_issue(journey, "System doesn't handle unicode characters in session names", "medium")

        # Step 5: Rapid session creation and deletion
        print("  📋 Step 5: Testing rapid create/delete cycles")
        rapid_sessions = []
        for i in range(5):
            success, data, _ = await self.api_call("POST", "/sessions", json={"name": f"rapid-{i}"})
            if success:
                session_id = data.get("session_id")
                rapid_sessions.append(session_id)

                # Immediately try to delete
                success2, _, _ = await self.api_call("DELETE", f"/sessions/{session_id}")
                if not success2:
                    self.log_ux_issue(journey, "Cannot immediately delete newly created session", "medium")

        return results

    async def run_all_journeys(self):
        """Run all user journey tests and compile results."""
        print("🧪 Starting Comprehensive User Journey Testing")
        print("=" * 60)

        journeys = [
            ("First-time User Experience", self.journey_1_first_time_user),
            ("Power User Multiple Sessions", self.journey_2_power_user_multiple_sessions),
            ("Mobile Progress Check", self.journey_3_mobile_user_checking_progress),
            ("Stuck Session Recovery", self.journey_4_stuck_session_recovery),
            ("Session Lifecycle Management", self.journey_5_session_lifecycle_management),
            ("Error Handling & Resilience", self.journey_6_error_handling_resilience),
            ("Concurrent Users", self.journey_7_concurrent_user_simulation),
            ("Data Consistency", self.journey_8_data_consistency_validation),
            ("Performance Under Load", self.journey_9_performance_under_load),
            ("Edge Cases & Boundaries", self.journey_10_edge_cases_and_boundaries),
        ]

        try:
            await self.start_supervisor()

            for journey_name, journey_func in journeys:
                print(f"\n{'='*20} {journey_name} {'='*20}")
                try:
                    result = await journey_func()
                    self.test_results[journey_name] = result
                    status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
                    print(f"Result: {status}")
                except Exception as e:
                    print(f"❌ CRASHED: {e}")
                    self.test_results[journey_name] = {"success": False, "error": str(e)}
                    self.log_ux_issue(journey_name, f"Journey crashed: {e}", "critical")

        finally:
            await self.cleanup_supervisor()

        # Generate comprehensive report
        await self.generate_final_report()

    async def generate_final_report(self):
        """Generate comprehensive UX analysis report."""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE UX ANALYSIS REPORT")
        print("="*80)

        # Summary statistics
        total_journeys = len(self.test_results)
        successful_journeys = len([r for r in self.test_results.values() if r.get("success", False)])
        total_issues = len(self.ux_issues)

        print(f"\n📈 SUMMARY STATISTICS")
        print(f"Total Journeys Tested: {total_journeys}")
        print(f"Successful Journeys: {successful_journeys}/{total_journeys} ({successful_journeys/total_journeys*100:.1f}%)")
        print(f"Total UX Issues Found: {total_issues}")

        # Issue severity breakdown
        severity_counts = {}
        for issue in self.ux_issues:
            severity = issue["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        print(f"\n🚨 ISSUE SEVERITY BREAKDOWN")
        for severity in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(severity, 0)
            print(f"{severity.upper()}: {count} issues")

        # Top UX issues
        print(f"\n🔍 TOP UX ISSUES TO ADDRESS")
        critical_high_issues = [i for i in self.ux_issues if i["severity"] in ["critical", "high"]]

        if critical_high_issues:
            for i, issue in enumerate(critical_high_issues[:10], 1):
                print(f"{i}. [{issue['severity'].upper()}] {issue['journey']}: {issue['issue']}")
        else:
            print("✅ No critical or high severity issues found!")

        # Journey-specific insights
        print(f"\n📱 JOURNEY-SPECIFIC INSIGHTS")
        for journey_name, result in self.test_results.items():
            status = "✅" if result.get("success", False) else "❌"
            journey_issues = [i for i in self.ux_issues if i["journey"] == journey_name]
            print(f"{status} {journey_name}: {len(journey_issues)} issues")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS FOR MVP IMPROVEMENT")
        recommendations = []

        # High-priority recommendations based on issues found
        if severity_counts.get("critical", 0) > 0:
            recommendations.append("🔥 CRITICAL: Fix critical issues before any deployment")

        if severity_counts.get("high", 0) > 0:
            recommendations.append("⚡ HIGH PRIORITY: Address high-severity issues for better user retention")

        mobile_issues = [i for i in self.ux_issues if "mobile" in i["issue"].lower() or i["journey"] == "mobile_progress_check"]
        if mobile_issues:
            recommendations.append("📱 MOBILE: Optimize for mobile users (key use case)")

        performance_issues = [i for i in self.ux_issues if "slow" in i["issue"].lower() or "performance" in i["issue"].lower()]
        if performance_issues:
            recommendations.append("🚀 PERFORMANCE: Improve response times for better UX")

        error_issues = [i for i in self.ux_issues if "error" in i["issue"].lower() or i["journey"] == "error_handling"]
        if error_issues:
            recommendations.append("🛡️ ERROR HANDLING: Better error messages and recovery")

        consistency_issues = [i for i in self.ux_issues if "consistency" in i["issue"].lower()]
        if consistency_issues:
            recommendations.append("🔄 DATA CONSISTENCY: Fix data synchronization issues")

        if not recommendations:
            recommendations.append("🎉 EXCELLENT: System shows good UX maturity for MVP!")

        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")

        # Next steps
        print(f"\n🎯 RECOMMENDED NEXT STEPS")
        print("1. Fix all critical and high-severity issues")
        print("2. Implement better error messages and user feedback")
        print("3. Optimize for mobile user workflows")
        print("4. Add user onboarding for first-time users")
        print("5. Implement proper rate limiting and performance monitoring")
        print("6. Add data validation and boundary condition handling")
        print("7. Consider A/B testing for critical user flows")

        # Save detailed report
        report_data = {
            "summary": {
                "total_journeys": total_journeys,
                "successful_journeys": successful_journeys,
                "total_issues": total_issues,
                "severity_breakdown": severity_counts
            },
            "issues": self.ux_issues,
            "test_results": self.test_results,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }

        with open("user_journey_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📄 Detailed report saved to: user_journey_test_report.json")
        print("="*80)


async def main():
    """Main function to run user journey tests."""
    tester = UserJourneyTester()
    await tester.run_all_journeys()


if __name__ == "__main__":
    asyncio.run(main())