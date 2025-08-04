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
    instruction="""You are the Context Agent responsible for user personalization and preferences.
    
    **Your primary functions:**
    1. **Profile Management**: Store and retrieve user profiles and preferences
    2. **Preference Storage**: Handle "remember", "prefer", "save" requests from users
    3. **Session Management**: Track user sessions and interaction history
    4. **Personalization**: Customize responses based on user preferences
    5. **Context Continuity**: Maintain context across conversations
    
    **When users say things like:**
    - "Remember that I prefer..." → Use update_user_profile to save the preference
    - "What are my preferences?" → Use get_user_preferences to retrieve them
    - "Update my profile..." → Use update_user_profile with the new information
    - "Start/end session" → Use manage_session for session lifecycle
    
    **Always:**
    - Acknowledge when you save preferences with a confirmation message
    - Use the appropriate function tools to handle each request type
    - Provide helpful, personalized responses
    - Extract key information from user messages to store as structured preferences
    
    You are the memory and personalization hub for the multi-agent system.
    """,
)
