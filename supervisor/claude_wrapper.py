"""
Claude-Code Process Wrapper

Handles PTY-based communication with Claude-Code processes.
Manages session lifecycle, input/output, and interactive prompts.
"""

import asyncio
import logging
import os
import signal
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pexpect
import psutil

logger = logging.getLogger(__name__)


class ClaudeWrapper:
    """Wrapper for a single Claude-Code process with PTY communication."""

    def __init__(self, session_id: str, working_dir: Optional[str] = None):
        self.session_id = session_id
        self.working_dir = working_dir or os.getcwd()
        self.process: Optional[pexpect.spawn] = None
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.log_buffer: List[str] = []
        self.max_log_lines = 1000

    async def start(self) -> bool:
        """Start a new Claude-Code process optimized for ChatGPT responsiveness."""
        try:
            logger.info(f"Starting Claude-Code session {self.session_id}")

            # Start claude-code in the specified directory
            # For testing, use mock if claude-code is not available
            try:
                # Try to find claude-code in PATH
                import shutil
                claude_cmd = shutil.which("claude-code")
                if claude_cmd:
                    cmd = "claude-code"
                else:
                    # Fall back to mock for testing
                    cmd = f"python3 {os.path.dirname(__file__)}/../scripts/mock-claude-code.py"
            except:
                cmd = f"python3 {os.path.dirname(__file__)}/../scripts/mock-claude-code.py"

            self.process = pexpect.spawn(
                cmd,
                cwd=self.working_dir,
                encoding='utf-8',
                timeout=10  # Reduced from 30s for faster failure detection
            )

            # OPTIMIZATION: Minimal wait for ChatGPT responsiveness
            # Just verify process started, don't wait for full initialization
            await asyncio.sleep(0.5)  # Quick check instead of full wait

            if self.process.isalive():
                # Mark as started, let initialization happen in background
                self._add_to_log("SESSION: Starting up...")
                logger.info(f"Claude-Code session {self.session_id} started successfully")

                # Schedule background initialization
                asyncio.create_task(self._background_initialization())
                return True
            else:
                raise RuntimeError("Process failed to start")

        except Exception as e:
            logger.error(f"Failed to start session {self.session_id}: {e}")
            return False

    async def _background_initialization(self):
        """Complete initialization in background without blocking creation."""
        try:
            # Wait for actual ready state
            await self._wait_for_ready()
            self._add_to_log("SESSION: Ready for commands")
        except Exception as e:
            logger.warning(f"Background initialization warning for {self.session_id}: {e}")
            self._add_to_log("SESSION: Initialization completed with warnings")

    async def send_message(self, message: str) -> Dict:
        """Send a message to the Claude-Code session."""
        if not self.process or not self.process.isalive():
            raise RuntimeError(f"Session {self.session_id} is not active")

        try:
            logger.info(f"Sending message to session {self.session_id}: {message[:100]}...")

            # Send the message
            self.process.sendline(message)
            self.last_activity = datetime.now()

            # Capture immediate response
            response_lines = []
            try:
                # Wait for some output (non-blocking)
                self.process.expect([pexpect.TIMEOUT], timeout=2)
                if self.process.before:
                    response_lines.append(self.process.before)
            except pexpect.TIMEOUT:
                pass

            # Add to log buffer
            self._add_to_log(f"USER: {message}")
            if response_lines:
                self._add_to_log("".join(response_lines))

            return {
                "status": "sent",
                "immediate_response": "".join(response_lines),
                "timestamp": self.last_activity.isoformat()
            }

        except Exception as e:
            logger.error(f"Error sending message to session {self.session_id}: {e}")
            raise

    async def get_logs(self, lines: int = 50, mobile_friendly: bool = False) -> List[str]:
        """Get recent log lines from the session, optimized for ChatGPT display."""
        logs = self.log_buffer[-lines:] if self.log_buffer else []

        if mobile_friendly:
            # MOBILE OPTIMIZATION: Format logs for ChatGPT mobile app
            mobile_logs = []
            for log in logs:
                # Truncate long lines that cause horizontal scrolling in ChatGPT mobile
                if len(log) > 80:
                    # Keep timestamp and truncate content intelligently
                    if ']' in log:
                        timestamp_part = log.split(']', 1)[0] + ']'
                        content_part = log.split(']', 1)[1] if len(log.split(']', 1)) > 1 else ""
                        if len(content_part) > 50:
                            content_part = content_part[:47] + "..."
                        mobile_logs.append(timestamp_part + content_part)
                    else:
                        mobile_logs.append(log[:77] + "...")
                else:
                    mobile_logs.append(log)
            return mobile_logs

        return logs

    def format_logs_for_chatgpt(self, logs: List[str], max_lines: int = 10) -> str:
        """Format logs as a readable string for ChatGPT responses."""
        if not logs:
            return "No recent activity in this session."

        # Take most recent logs and format for conversation
        recent_logs = logs[-max_lines:]

        formatted = "Recent session activity:\n```\n"
        for log in recent_logs:
            formatted += log + "\n"
        formatted += "```"

        return formatted

    async def get_status(self) -> Dict:
        """Get current session status."""
        is_alive = self.process and self.process.isalive()

        status = {
            "session_id": self.session_id,
            "status": "active" if is_alive else "terminated",
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "working_dir": self.working_dir,
            "log_lines": len(self.log_buffer)
        }

        if is_alive and self.process:
            status.update({
                "pid": self.process.pid,
                "memory_usage": self._get_memory_usage()
            })

        return status

    async def terminate(self) -> bool:
        """Terminate the Claude-Code session."""
        if not self.process:
            return True

        try:
            logger.info(f"Terminating session {self.session_id}")

            # Try graceful termination first
            self.process.sendcontrol('c')  # Send Ctrl+C
            await asyncio.sleep(1)

            if self.process.isalive():
                self.process.terminate()
                await asyncio.sleep(1)

            if self.process.isalive():
                self.process.kill(signal.SIGKILL)

            logger.info(f"Session {self.session_id} terminated")
            return True

        except Exception as e:
            logger.error(f"Error terminating session {self.session_id}: {e}")
            return False

    async def check_for_prompts(self) -> Optional[str]:
        """Check if Claude-Code is waiting for user input."""
        if not self.process or not self.process.isalive():
            return None

        try:
            # Non-blocking check for common prompt patterns
            patterns = [
                r".*\[y/n\].*",  # Yes/no prompts
                r".*\(y/N\).*",  # Yes/no with default
                r".*Continue\?.*",  # Continue prompts
                r".*Enter.*:",  # Input prompts
            ]

            index = self.process.expect(patterns + [pexpect.TIMEOUT], timeout=0.1)
            if index < len(patterns):
                prompt_text = self.process.before + self.process.after
                self._add_to_log(f"PROMPT: {prompt_text}")
                return prompt_text

        except pexpect.TIMEOUT:
            pass
        except Exception as e:
            logger.warning(f"Error checking for prompts in session {self.session_id}: {e}")

        return None

    async def respond_to_prompt(self, response: str) -> bool:
        """Respond to an interactive prompt."""
        if not self.process or not self.process.isalive():
            return False

        try:
            self.process.sendline(response)
            self._add_to_log(f"PROMPT_RESPONSE: {response}")
            self.last_activity = datetime.now()
            return True
        except Exception as e:
            logger.error(f"Error responding to prompt in session {self.session_id}: {e}")
            return False

    def _add_to_log(self, line: str):
        """Add a line to the log buffer with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_buffer.append(f"[{timestamp}] {line}")

        # Keep log buffer size manageable
        if len(self.log_buffer) > self.max_log_lines:
            self.log_buffer = self.log_buffer[-self.max_log_lines//2:]

    async def _wait_for_ready(self):
        """Wait for Claude-Code to be ready for input."""
        try:
            # Wait for the initial prompt or ready state
            self.process.expect([pexpect.TIMEOUT], timeout=5)
            if self.process.before:
                self._add_to_log(f"STARTUP: {self.process.before}")
        except pexpect.TIMEOUT:
            pass  # Timeout is expected for non-blocking wait

    def _get_memory_usage(self) -> Optional[float]:
        """Get memory usage of the process in MB."""
        try:
            if self.process and self.process.pid:
                proc = psutil.Process(self.process.pid)
                return proc.memory_info().rss / 1024 / 1024  # Convert to MB
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        return None