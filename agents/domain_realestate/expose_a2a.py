#!/usr/bin/env python3
"""
Domain Real Estate Agent A2A Exposure Script
Exposes the Domain Real Estate Agent via A2A protocol using Google ADK's to_a2a() method.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from agents.domain_realestate.agent import root_agent

# Create A2A app using Google's recommended to_a2a() method
a2a_app = to_a2a(root_agent, port=8001)

if __name__ == "__main__":
    import uvicorn

    print("🏠 Starting Domain Real Estate Agent A2A Server on port 8001...")
    print("📋 Agent Card URL: http://localhost:8001/.well-known/agent.json")
    uvicorn.run("agents.domain_realestate.expose_a2a:a2a_app", host="localhost", port=8001, reload=False)
