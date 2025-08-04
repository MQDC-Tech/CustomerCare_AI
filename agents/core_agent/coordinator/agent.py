"""Core Agent Coordinator for multi-agent orchestration using official ADK A2A pattern."""

# Core imports
import os
import sys
from typing import Any, Dict, List

# ADK imports following official pattern
from google.adk.agents.llm_agent import Agent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH, RemoteA2aAgent
from google.adk.tools.example_tool import ExampleTool
from google.genai import types

# Import utils with absolute path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from utils.memory import MemoryManager

# Initialize local components
memory_manager = MemoryManager()

# Define remote A2A agents following official ADK pattern
domain_realestate_agent = RemoteA2aAgent(
    name="domain_realestate",
    description="Domain Real Estate Agent for property search, lead management, and CRM integration",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
)

context_agent = RemoteA2aAgent(
    name="context_agent",
    description="Context Agent for user personalization, profiles, and session management",
    agent_card=f"http://localhost:8002{AGENT_CARD_WELL_KNOWN_PATH}",
)

# Create example tool for context
example_tool = ExampleTool(
    [
        {
            "input": {
                "role": "user",
                "parts": [{"text": "Find me a 3-bedroom house in downtown."}],
            },
            "output": [
                {
                    "role": "model",
                    "parts": [
                        {"text": "I'll help you find a 3-bedroom house in downtown. Let me search our real estate database."}
                    ],
                }
            ],
        },
        {
            "input": {
                "role": "user",
                "parts": [{"text": "What are my saved preferences?"}],
            },
            "output": [
                {
                    "role": "model",
                    "parts": [{"text": "Let me check your saved preferences and profile information."}],
                }
            ],
        },
    ]
)

# Create the coordinator agent following official ADK A2A pattern
root_agent = Agent(
    model="gemini-1.5-flash",
    name="coordinator",
    instruction="""
    You are the Core Coordinator Agent for a multi-agent customer care platform.
    You delegate tasks to specialized agents based on user requests:
    
    1. For real estate queries (property search, listings, CRM), delegate to domain_realestate agent
    2. For user preferences, profiles, and personalization, delegate to context_agent
    3. For general queries, handle them directly with your built-in capabilities
    
    Follow these steps:
    1. Analyze the user's request to determine the appropriate agent
    2. Delegate to the relevant sub-agent if needed
    3. Present the complete response from the sub-agent to the user
    
    Always provide helpful, accurate responses and ensure proper task delegation.
    """,
    global_instruction=("You are CustomerCareBot, a helpful assistant for real estate and customer service."),
    sub_agents=[domain_realestate_agent, context_agent],
    tools=[example_tool],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
