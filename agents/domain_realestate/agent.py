"""Real Estate Domain Agent for handling real estate specific tasks."""

from google.adk import Agent
from google.adk.tools import FunctionTool, AgentTool
import sys
import os

from .tools.crm_connector import (
    create_lead,
    update_lead,
    get_lead,
    assign_lead_to_agent,
    search_properties,
    schedule_showing
)
from .tools.lead_router import (
    qualify_lead,
    route_lead_to_agent,
    prioritize_leads
)


# Create the real estate domain agent
root_agent = Agent(
    name="domain_realestate",
    model="gemini-1.5-flash",
    tools=[
        # CRM and Lead Management Tools
        FunctionTool(create_lead),
        FunctionTool(update_lead),
        FunctionTool(get_lead),
        FunctionTool(assign_lead_to_agent),
        FunctionTool(qualify_lead),
        FunctionTool(route_lead_to_agent),
        FunctionTool(prioritize_leads),
        
        # Property Management Tools
        FunctionTool(search_properties),
        FunctionTool(schedule_showing),
        
        # Core Agent Tools (A2A communication)
        # Note: AgentTool requires actual agent instances, not strings
        # These will be configured during deployment for A2A communication
    ],
    instruction="""
    You are the Real Estate Domain Agent responsible for:
    1. Managing real estate leads and CRM integration
    2. Qualifying and routing leads to appropriate agents
    3. Searching and managing property listings
    4. Scheduling property showings and appointments
    5. Coordinating with core agents for LLM, memory, and notifications
    
    Key capabilities:
    - Lead creation, qualification, and routing
    - Property search and matching
    - CRM integration and data management
    - Agent assignment and workload balancing
    - Customer communication and follow-up
    
    Always prioritize lead qualification and proper routing to maximize conversion rates.
    Use the context agent for personalization and the memory agent for maintaining conversation history.
    """
)
