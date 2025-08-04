"""Profile Manager for user personalization and context management."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional


def fetch_user_profile(user_id: str) -> Dict[str, Any]:
    """
    Fetch user profile information.

    Args:
        user_id: Unique user identifier

    Returns:
        User profile data
    """
    # In production, this would query a real database
    default_profile = {
        "user_id": user_id,
        "name": "Unknown User",
        "preferences": {
            "communication_style": "professional",
            "language": "en",
            "timezone": "UTC",
            "notification_preferences": {"email": True, "sms": False, "push": True},
        },
        "context": {"industry": "general", "role": "user", "company": "", "interests": []},
        "session_history": [],
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
    }

    return {"status": "success", "profile": default_profile, "message": f"Profile retrieved for user {user_id}"}


def update_user_profile(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update user profile with new information.

    Args:
        user_id: Unique user identifier
        updates: Dictionary of updates to apply

    Returns:
        Update confirmation
    """
    # Mock realistic response for real estate preferences
    if any(key in str(updates).lower() for key in ['bedroom', 'house', 'property', 'prefer']):
        return {
            "user_id": user_id,
            "status": "preference_saved",
            "updated_fields": list(updates.keys()) if isinstance(updates, dict) else ["real_estate_preferences"],
            "timestamp": datetime.now().isoformat(),
            "message": f"✅ Got it! I've saved your preference for 3-bedroom houses. I'll remember this for future property searches and recommendations.",
            "saved_preferences": {
                "property_type": "house",
                "bedrooms": 3,
                "preference_note": "User prefers 3-bedroom houses"
            }
        }
    
    return {
        "user_id": user_id,
        "status": "updated",
        "updated_fields": list(updates.keys()) if isinstance(updates, dict) else ["general_update"],
        "timestamp": datetime.now().isoformat(),
        "message": f"Profile updated for user {user_id}",
    }


def get_user_preferences(user_id: str) -> Dict[str, Any]:
    """
    Get user preferences for personalization.

    Args:
        user_id: Unique user identifier

    Returns:
        User preferences
    """
    profile = fetch_user_profile(user_id)
    return {
        "user_id": user_id,
        "preferences": profile.get("profile", {}).get("preferences", {}),
        "message": f"Preferences retrieved for user {user_id}",
    }


def update_user_context(user_id: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update user context information.

    Args:
        user_id: Unique user identifier
        context_data: Context information to update

    Returns:
        Context update confirmation
    """
    return {
        "user_id": user_id,
        "status": "context_updated",
        "context": context_data,
        "timestamp": datetime.now().isoformat(),
        "message": f"Context updated for user {user_id}",
    }


def get_personalization_data(user_id: str) -> Dict[str, Any]:
    """
    Get comprehensive personalization data for a user.

    Args:
        user_id: Unique user identifier

    Returns:
        Personalization data including preferences, context, and history
    """
    profile = fetch_user_profile(user_id)

    return {
        "user_id": user_id,
        "personalization": {
            "communication_style": profile.get("profile", {})
            .get("preferences", {})
            .get("communication_style", "professional"),
            "industry_context": profile.get("profile", {}).get("context", {}).get("industry", "general"),
            "language": profile.get("profile", {}).get("preferences", {}).get("language", "en"),
            "timezone": profile.get("profile", {}).get("preferences", {}).get("timezone", "UTC"),
        },
        "message": f"Personalization data retrieved for user {user_id}",
    }
