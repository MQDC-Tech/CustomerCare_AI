#!/usr/bin/env python3
"""
Core Agent A2A Exposure Script
Exposes the Core Agent via A2A protocol using Google ADK's to_a2a() method.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from agents.core_agent.agent import root_agent

# Create A2A app using Google's recommended to_a2a() method
a2a_app = to_a2a(root_agent, port=8001)

if __name__ == "__main__":
    import uvicorn

    print("🧠 Starting Core Agent A2A Server on port 8001...")
    print("📋 Agent Card URL: http://localhost:8001/.well-known/agent.json")
    uvicorn.run("agents.core_agent.expose_a2a:a2a_app", host="localhost", port=8001, reload=False)
