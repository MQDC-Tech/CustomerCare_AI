"""Tests for core agents functionality."""

import os
import sys

import pytest

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from agents.core_agent.memory_agent.agent import root_agent as memory_agent
from agents.core_agent.notifications.agent import root_agent as notifications_agent
from utils.llm import generate_reply, rewrite_text, summarize_text


class TestLLMUtilities:
    """Test LLM utility functions."""

    def test_generate_reply(self):
        """Test basic reply generation."""
        result = generate_reply("Hello, how are you?")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_summarize_text(self):
        """Test text summarization."""
        long_text = "This is a very long text that needs to be summarized. " * 10
        result = summarize_text(long_text, max_length=100)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_rewrite_text(self):
        """Test text rewriting."""
        original = "Hello there, how are you doing today?"
        result = rewrite_text(original, style="formal")
        assert isinstance(result, str)
        assert len(result) > 0


class TestMemoryAgent:
    """Test memory agent functionality."""

    def test_memory_agent_exists(self):
        """Test that memory agent is properly initialized."""
        assert memory_agent is not None
        assert memory_agent.name == "memory_agent"
        assert len(memory_agent.tools) > 0


class TestNotificationsAgent:
    """Test notifications agent functionality."""

    def test_notifications_agent_exists(self):
        """Test that notifications agent is properly initialized."""
        assert notifications_agent is not None
        assert notifications_agent.name == "notifications"
        assert len(notifications_agent.tools) > 0


def test_agent_integration():
    """Test basic agent integration."""
    # This would test actual agent communication in a real environment
    assert True  # Placeholder for integration tests


if __name__ == "__main__":
    pytest.main([__file__])
