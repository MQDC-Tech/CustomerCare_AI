"""Memory management utilities for the multi-agent system."""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class MemoryManager:
    """
    Manages conversation memory and context for agents.
    """

    def __init__(self, memory_file: str = "agent_memory.json"):
        """
        Initialize the memory manager.

        Args:
            memory_file: Path to the memory storage file
        """
        self.memory_file = memory_file
        self.memory = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from file."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {
            "conversations": {},
            "user_profiles": {},
            "context_history": [],
            "metadata": {"created": datetime.now().isoformat(), "last_updated": datetime.now().isoformat()},
        }

    def _save_memory(self) -> None:
        """Save memory to file."""
        self.memory["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=2)

    def store_conversation(self, session_id: str, message: str, response: str, agent: str = "system") -> None:
        """
        Store a conversation exchange.

        Args:
            session_id: Session identifier
            message: User message
            response: Agent response
            agent: Agent that provided the response
        """
        if session_id not in self.memory["conversations"]:
            self.memory["conversations"][session_id] = []

        exchange = {"timestamp": datetime.now().isoformat(), "message": message, "response": response, "agent": agent}

        self.memory["conversations"][session_id].append(exchange)
        self._save_memory()

    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of exchanges to return

        Returns:
            List of conversation exchanges
        """
        if session_id not in self.memory["conversations"]:
            return []

        return self.memory["conversations"][session_id][-limit:]

    def store_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> None:
        """
        Store user profile information.

        Args:
            user_id: User identifier
            profile_data: Profile information
        """
        if user_id not in self.memory["user_profiles"]:
            self.memory["user_profiles"][user_id] = {}

        self.memory["user_profiles"][user_id].update(profile_data)
        self.memory["user_profiles"][user_id]["last_updated"] = datetime.now().isoformat()
        self._save_memory()

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user profile information.

        Args:
            user_id: User identifier

        Returns:
            User profile data
        """
        return self.memory["user_profiles"].get(user_id, {})

    def add_context(self, context_type: str, data: Dict[str, Any]) -> None:
        """
        Add context information.

        Args:
            context_type: Type of context (e.g., 'property_search', 'lead_creation')
            data: Context data
        """
        context_entry = {"timestamp": datetime.now().isoformat(), "type": context_type, "data": data}

        self.memory["context_history"].append(context_entry)

        # Keep only last 100 context entries
        if len(self.memory["context_history"]) > 100:
            self.memory["context_history"] = self.memory["context_history"][-100:]

        self._save_memory()

    def get_context(self, context_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get context history.

        Args:
            context_type: Filter by context type (optional)
            limit: Maximum number of entries to return

        Returns:
            List of context entries
        """
        context_history = self.memory["context_history"]

        if context_type:
            context_history = [entry for entry in context_history if entry["type"] == context_type]

        return context_history[-limit:]

    def clear_session(self, session_id: str) -> None:
        """
        Clear conversation history for a session.

        Args:
            session_id: Session identifier
        """
        if session_id in self.memory["conversations"]:
            del self.memory["conversations"][session_id]
            self._save_memory()

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory usage statistics.

        Returns:
            Memory statistics
        """
        return {
            "total_conversations": len(self.memory["conversations"]),
            "total_users": len(self.memory["user_profiles"]),
            "total_context_entries": len(self.memory["context_history"]),
            "created": self.memory["metadata"]["created"],
            "last_updated": self.memory["metadata"]["last_updated"],
        }
