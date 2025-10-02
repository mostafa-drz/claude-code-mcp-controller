"""
Claude-Code Session Wrapper

Handles tmux-based communication with existing Claude-Code sessions.
Manages session communication, input/output, and interactive prompts.
"""

import asyncio
import logging
import os
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ClaudeWrapper:
    """Wrapper for a single tmux session running Claude-Code."""

    def __init__(self, session_id: str, working_dir: Optional[str] = None):
        self.session_id = session_id  # Should match tmux session name (e.g., claude-web-app)
        self.working_dir = working_dir or os.getcwd()
        self.created_at = datetime.now()
        self.last_activity = datetime.now()


    async def send_message(self, message: str) -> Dict:
        """Send a message to the tmux session running Claude-Code."""
        try:
            logger.info(f"Sending message to session {self.session_id}: {message[:100]}...")

            # Send message to tmux session
            result = subprocess.run(
                ["tmux", "send-keys", "-t", self.session_id, message, "C-m"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                raise RuntimeError(f"Failed to send message to tmux session {self.session_id}: {result.stderr}")

            self.last_activity = datetime.now()

            # Capture current output after allowing time for processing
            await asyncio.sleep(2.0)  # Increased wait time for Claude to process
            current_output = await self._capture_output()

            return {
                "status": "sent",
                "immediate_response": current_output,
                "timestamp": self.last_activity.isoformat()
            }

        except Exception as e:
            logger.error(f"Error sending message to session {self.session_id}: {e}")
            raise

    async def get_logs(self, lines: int = 50, mobile_friendly: bool = False) -> List[str]:
        """Get recent log lines from tmux session."""
        try:
            # Capture current tmux pane content
            result = subprocess.run(
                ["tmux", "capture-pane", "-t", self.session_id, "-p"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                logger.warning(f"Failed to capture logs from tmux session {self.session_id}")
                return []

            output_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            recent_lines = output_lines[-lines:] if output_lines else []

            if mobile_friendly:
                # Mobile optimization: truncate long lines
                mobile_logs = []
                for line in recent_lines:
                    if len(line) > 80:
                        mobile_logs.append(line[:77] + "...")
                    else:
                        mobile_logs.append(line)
                return mobile_logs

            return recent_lines

        except Exception as e:
            logger.error(f"Error getting logs from session {self.session_id}: {e}")
            return []

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
        """Get current tmux session status."""
        # Check if tmux session exists
        try:
            result = subprocess.run(
                ["tmux", "has-session", "-t", self.session_id],
                capture_output=True,
                check=False
            )
            is_active = result.returncode == 0
        except Exception:
            is_active = False

        return {
            "session_id": self.session_id,
            "status": "active" if is_active else "terminated",
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "working_dir": self.working_dir
        }

    async def terminate(self) -> bool:
        """Terminate the tmux session."""
        try:
            logger.info(f"Terminating tmux session {self.session_id}")

            # Try graceful termination first - send Ctrl+C
            result = subprocess.run(
                ["tmux", "send-keys", "-t", self.session_id, "C-c"],
                capture_output=True,
                text=True,
                check=False
            )
            await asyncio.sleep(1)

            # Check if session still exists
            check_result = subprocess.run(
                ["tmux", "has-session", "-t", self.session_id],
                capture_output=True,
                check=False
            )

            if check_result.returncode == 0:
                # Session still exists, force kill it
                kill_result = subprocess.run(
                    ["tmux", "kill-session", "-t", self.session_id],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if kill_result.returncode != 0:
                    logger.warning(f"Failed to kill tmux session {self.session_id}: {kill_result.stderr}")
                    return False

            logger.info(f"Tmux session {self.session_id} terminated")
            return True

        except Exception as e:
            logger.error(f"Error terminating tmux session {self.session_id}: {e}")
            return False

    async def check_for_prompts(self) -> Optional[str]:
        """Check if Claude-Code is waiting for user input by examining recent output."""
        try:
            # Check if tmux session exists
            result = subprocess.run(
                ["tmux", "has-session", "-t", self.session_id],
                capture_output=True,
                check=False
            )
            if result.returncode != 0:
                return None

            # Get recent output from tmux session
            output = await self._capture_output()
            if not output:
                return None

            # Check for common prompt patterns in the output
            import re
            patterns = [
                r".*\[y/n\].*",  # Yes/no prompts
                r".*\(y/N\).*",  # Yes/no with default
                r".*Continue\?.*",  # Continue prompts
                r".*Enter.*:",  # Input prompts
            ]

            # Look at the last few lines for prompts
            lines = output.split('\n')[-3:]
            for line in lines:
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        return line

        except Exception as e:
            logger.warning(f"Error checking for prompts in session {self.session_id}: {e}")

        return None

    async def respond_to_prompt(self, response: str) -> bool:
        """Respond to an interactive prompt."""
        try:
            # Check if tmux session exists
            result = subprocess.run(
                ["tmux", "has-session", "-t", self.session_id],
                capture_output=True,
                check=False
            )
            if result.returncode != 0:
                return False

            # Send response to tmux session
            result = subprocess.run(
                ["tmux", "send-keys", "-t", self.session_id, response, "C-m"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                logger.error(f"Failed to send response to tmux session {self.session_id}: {result.stderr}")
                return False

            self.last_activity = datetime.now()
            return True

        except Exception as e:
            logger.error(f"Error responding to prompt in session {self.session_id}: {e}")
            return False

    async def _capture_output(self) -> str:
        """Capture current output from tmux session."""
        try:
            result = subprocess.run(
                ["tmux", "capture-pane", "-t", self.session_id, "-p"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                logger.warning(f"Failed to capture output from tmux session {self.session_id}")
                return ""

            return result.stdout.strip()

        except Exception as e:
            logger.error(f"Error capturing output from session {self.session_id}: {e}")
            return ""


