"""Tests for context agent functionality."""

import os
import sys

import pytest

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from agents.context_agent.agent import root_agent as context_agent
from agents.context_agent.profile_manager import (
    fetch_user_profile,
    get_personalization_data,
    get_user_preferences,
    update_user_context,
    update_user_profile,
)


class TestProfileManager:
    """Test profile manager functionality."""

    def test_fetch_user_profile(self):
        """Test user profile fetching."""
        result = fetch_user_profile("test_user_123")

        assert result["status"] == "success"
        assert "profile" in result
        assert result["profile"]["user_id"] == "test_user_123"
        assert "preferences" in result["profile"]
        assert "context" in result["profile"]

    def test_update_user_profile(self):
        """Test user profile updating."""
        updates = {"name": "John Doe", "preferences": {"communication_style": "casual"}}

        result = update_user_profile("test_user_123", updates)

        assert result["status"] == "updated"
        assert result["user_id"] == "test_user_123"
        assert "updated_fields" in result
        assert len(result["updated_fields"]) == 2

    def test_get_user_preferences(self):
        """Test user preferences retrieval."""
        result = get_user_preferences("test_user_123")

        assert "preferences" in result
        assert result["user_id"] == "test_user_123"
        assert isinstance(result["preferences"], dict)

    def test_update_user_context(self):
        """Test user context updating."""
        context_data = {"industry": "real_estate", "role": "buyer", "interests": ["houses", "condos"]}

        result = update_user_context("test_user_123", context_data)

        assert result["status"] == "context_updated"
        assert result["user_id"] == "test_user_123"
        assert result["context"] == context_data

    def test_get_personalization_data(self):
        """Test personalization data retrieval."""
        result = get_personalization_data("test_user_123")

        assert "personalization" in result
        assert result["user_id"] == "test_user_123"
        personalization = result["personalization"]
        assert "communication_style" in personalization
        assert "industry_context" in personalization
        assert "language" in personalization
        assert "timezone" in personalization


class TestContextAgent:
    """Test context agent functionality."""

    def test_context_agent_exists(self):
        """Test that context agent is properly initialized."""
        assert context_agent is not None
        assert context_agent.name == "context_agent"
        assert len(context_agent.tools) > 0


def test_session_management():
    """Test session management functionality."""
    # Import the session management function
    from agents.context_agent.agent import manage_session

    # Test session start
    result = manage_session("test_user_123", action="start")
    assert result["status"] == "started"
    assert result["user_id"] == "test_user_123"
    assert "session_id" in result

    # Test session update
    session_data = {"page_views": 5, "last_action": "property_search"}
    result = manage_session("test_user_123", action="update", session_data=session_data)
    assert result["status"] == "updated"
    assert result["data"] == session_data

    # Test session end
    result = manage_session("test_user_123", action="end")
    assert result["status"] == "ended"


def test_response_personalization():
    """Test response personalization functionality."""
    from agents.context_agent.agent import personalize_response

    base_response = "Here are the properties that match your criteria."

    # Test personalization
    result = personalize_response("test_user_123", base_response)

    assert "personalized_response" in result
    assert "style_applied" in result
    assert result["original_response"] == base_response
    assert len(result["personalized_response"]) > len(base_response)


def test_context_integration():
    """Test context agent integration."""
    # Test full workflow
    user_id = "integration_test_user"

    # Fetch profile
    profile = fetch_user_profile(user_id)
    assert profile["status"] == "success"

    # Update context
    context_update = update_user_context(user_id, {"industry": "real_estate"})
    assert context_update["status"] == "context_updated"

    # Get personalization data
    personalization = get_personalization_data(user_id)
    assert "personalization" in personalization


if __name__ == "__main__":
    pytest.main([__file__])
