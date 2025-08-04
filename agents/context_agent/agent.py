"""Context Agent for user personalization and session management. This is a server-side A2A agent following ADK standards."""

import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from google.adk import Agent
from google.adk.tools import FunctionTool

from .profile_manager import (
    fetch_user_profile,
    get_personalization_data,
    get_user_preferences,
    update_user_context,
    update_user_profile,
)


def manage_session(
    user_id: str, action: Optional[str] = None, session_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Manage user session lifecycle.

    Args:
        user_id: Unique user identifier
        action: Session action (start, update, end)
        session_data: Optional session data

    Returns:
        Session management result
    """
    session_id = f"session_{user_id}_{datetime.now().timestamp()}"

    # Default action to "start" if None
    if action is None:
        action = "start"

    if action == "start":
        return {
            "session_id": session_id,
            "user_id": user_id,
            "status": "started",
            "timestamp": datetime.now().isoformat(),
            "message": f"Session started for user {user_id}",
        }
    elif action == "update":
        return {
            "session_id": session_id,
            "user_id": user_id,
            "status": "updated",
            "data": session_data or {},
            "timestamp": datetime.now().isoformat(),
            "message": f"Session updated for user {user_id}",
        }
    elif action == "end":
        return {
            "session_id": session_id,
            "user_id": user_id,
            "status": "ended",
            "timestamp": datetime.now().isoformat(),
            "message": f"Session ended for user {user_id}",
        }


def personalize_response(user_id: str, base_response: str) -> Dict[str, Any]:
    """
    Personalize a response based on user preferences.

    Args:
        user_id: Unique user identifier
        base_response: Base response to personalize

    Returns:
        Personalized response
    """
    personalization = get_personalization_data(user_id)
    style = personalization.get("personalization", {}).get("communication_style", "professional")

    # Simple personalization logic - in production this would be more sophisticated
    if style == "casual":
        personalized = f"Hey! {base_response} 😊"
    elif style == "formal":
        personalized = f"Dear User, {base_response}. Best regards."
    else:  # professional
        personalized = f"Hello, {base_response}"

    return {
        "user_id": user_id,
        "original_response": base_response,
        "personalized_response": personalized,
        "style_applied": style,
        "message": f"Response personalized for user {user_id}",
    }


# Create the context agent
root_agent = Agent(
    name="context_agent",
    model="gemini-1.5-flash",
    tools=[
        FunctionTool(fetch_user_profile),
        FunctionTool(update_user_profile),
        FunctionTool(get_user_preferences),
        FunctionTool(update_user_context),
        FunctionTool(get_personalization_data),
        FunctionTool(manage_session),
        FunctionTool(personalize_response),
    ],
    instruction="""
    You are the Context Agent responsible for:
    1. Managing user profiles and personalization data
    2. Handling session lifecycle and continuity
    3. Personalizing responses based on user preferences
    4. Maintaining user context across interactions
    5. Providing user-specific customization
    
    Always consider user preferences and context when processing requests.
    """,
)
