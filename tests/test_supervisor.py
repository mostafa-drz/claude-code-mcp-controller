"""
Tests for the supervisor module.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from supervisor.session_manager import SessionManager
from supervisor.claude_wrapper import ClaudeWrapper


class TestClaudeWrapper:
    """Test cases for ClaudeWrapper."""

    @pytest.fixture
    def wrapper(self):
        return ClaudeWrapper("test_session", "/tmp/test")

    def test_init(self, wrapper):
        assert wrapper.session_id == "test_session"
        assert wrapper.working_dir == "/tmp/test"
        assert wrapper.process is None
        assert len(wrapper.log_buffer) == 0

    @pytest.mark.asyncio
    async def test_start_success(self, wrapper):
        with patch('pexpect.spawn') as mock_spawn:
            mock_process = MagicMock()
            mock_process.expect = AsyncMock()
            mock_spawn.return_value = mock_process

            result = await wrapper.start()
            assert result is True
            assert wrapper.process == mock_process

    @pytest.mark.asyncio
    async def test_start_failure(self, wrapper):
        with patch('pexpect.spawn', side_effect=Exception("Failed to start")):
            result = await wrapper.start()
            assert result is False
            assert wrapper.process is None

    @pytest.mark.asyncio
    async def test_send_message_no_process(self, wrapper):
        with pytest.raises(RuntimeError, match="Session .* is not active"):
            await wrapper.send_message("test message")

    @pytest.mark.asyncio
    async def test_get_status_inactive(self, wrapper):
        status = await wrapper.get_status()
        assert status["session_id"] == "test_session"
        assert status["status"] == "terminated"
        assert status["working_dir"] == "/tmp/test"

    def test_add_to_log(self, wrapper):
        wrapper._add_to_log("test message")
        assert len(wrapper.log_buffer) == 1
        assert "test message" in wrapper.log_buffer[0]

    @pytest.mark.asyncio
    async def test_get_logs(self, wrapper):
        wrapper._add_to_log("line 1")
        wrapper._add_to_log("line 2")
        wrapper._add_to_log("line 3")

        logs = await wrapper.get_logs(2)
        assert len(logs) == 2
        assert "line 2" in logs[0]
        assert "line 3" in logs[1]


class TestSessionManager:
    """Test cases for SessionManager."""

    @pytest.fixture
    def manager(self):
        return SessionManager()

    @pytest.mark.asyncio
    async def test_create_session_success(self, manager):
        with patch.object(ClaudeWrapper, 'start', return_value=True):
            session_id = await manager.create_session("test")
            assert session_id.startswith("test_")
            assert session_id in manager.sessions

    @pytest.mark.asyncio
    async def test_create_session_failure(self, manager):
        with patch.object(ClaudeWrapper, 'start', return_value=False):
            with pytest.raises(RuntimeError, match="Failed to start session"):
                await manager.create_session("test")

    @pytest.mark.asyncio
    async def test_list_sessions_empty(self, manager):
        sessions = await manager.list_sessions()
        assert sessions == []

    @pytest.mark.asyncio
    async def test_get_session_exists(self, manager):
        with patch.object(ClaudeWrapper, 'start', return_value=True):
            session_id = await manager.create_session("test")
            wrapper = await manager.get_session(session_id)
            assert wrapper is not None
            assert wrapper.session_id == session_id

    @pytest.mark.asyncio
    async def test_get_session_not_exists(self, manager):
        wrapper = await manager.get_session("nonexistent")
        assert wrapper is None

    @pytest.mark.asyncio
    async def test_send_message_session_not_found(self, manager):
        with pytest.raises(ValueError, match="Session .* not found"):
            await manager.send_message("nonexistent", "test message")

    @pytest.mark.asyncio
    async def test_terminate_session_success(self, manager):
        with patch.object(ClaudeWrapper, 'start', return_value=True), \
             patch.object(ClaudeWrapper, 'terminate', return_value=True):

            session_id = await manager.create_session("test")
            result = await manager.terminate_session(session_id)

            assert result is True
            assert session_id not in manager.sessions

    @pytest.mark.asyncio
    async def test_terminate_session_not_found(self, manager):
        result = await manager.terminate_session("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_check_session_health(self, manager):
        with patch.object(ClaudeWrapper, 'start', return_value=True), \
             patch.object(ClaudeWrapper, 'get_status', return_value={"status": "active"}):

            # Create a session
            await manager.create_session("test")

            health = await manager.check_session_health()
            assert health["total_sessions"] == 1
            assert health["active_sessions"] == 1
            assert health["dead_sessions"] == 0

    @pytest.mark.asyncio
    async def test_shutdown_all(self, manager):
        with patch.object(ClaudeWrapper, 'start', return_value=True), \
             patch.object(ClaudeWrapper, 'terminate', return_value=True):

            # Create multiple sessions
            await manager.create_session("test1")
            await manager.create_session("test2")

            shutdown_report = await manager.shutdown_all()

            assert shutdown_report["total_sessions"] == 2
            assert shutdown_report["successful_shutdowns"] == 2
            assert shutdown_report["failed_shutdowns"] == 0
            assert len(manager.sessions) == 0