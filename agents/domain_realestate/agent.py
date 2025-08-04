"""Domain Real Estate Agent with Coordinator for multi-agent orchestration."""

import os
import sys
from typing import Optional, Any, Dict, List

from google.adk import Agent
from google.adk.tools import FunctionTool
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH, RemoteA2aAgent
from google.genai import types

# Import utils with absolute path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from agents.domain_realestate.tools import crm_connector, lead_router
from utils.memory import MemoryManager

# Initialize local components
memory_manager = MemoryManager()

# Define remote A2A agents following official ADK pattern
core_agent = RemoteA2aAgent(
    name="core_agent",
    description="Core Agent for notifications, logging, analytics, and shared services",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
)

context_agent = RemoteA2aAgent(
    name="context_agent",
    description="Context Agent for user personalization, profiles, and session management",
    agent_card=f"http://localhost:8002{AGENT_CARD_WELL_KNOWN_PATH}",
)


def search_properties(query: str, max_price: float = 0.0, bedrooms: int = 0, location: str = "") -> str:
    """
    Search for properties based on criteria.

    Args:
        query: Search query for properties
        max_price: Maximum price filter
        bedrooms: Number of bedrooms
        location: Location filter

    Returns:
        Formatted property search results
    """

    # Mock property search - replace with actual MLS/property API
    properties = [
        {
            "id": "PROP001",
            "address": "123 Main St, Downtown",
            "price": 450000,
            "bedrooms": 3,
            "bathrooms": 2,
            "sqft": 1800,
            "description": "Beautiful downtown condo with city views",
        },
        {
            "id": "PROP002",
            "address": "456 Oak Ave, Suburbs",
            "price": 520000,
            "bedrooms": 4,
            "bathrooms": 3,
            "sqft": 2200,
            "description": "Spacious family home with large backyard",
        },
    ]

    # Filter properties based on criteria
    filtered_properties = []
    for prop in properties:
        if max_price > 0 and prop["price"] > max_price:
            continue
        if bedrooms > 0 and prop["bedrooms"] != bedrooms:
            continue
        if location and location.lower() not in prop["address"].lower():
            continue
        filtered_properties.append(prop)

    if not filtered_properties:
        return "No properties found matching your criteria."

    # Format results
    result = f"Found {len(filtered_properties)} properties:\n\n"
    for prop in filtered_properties:
        result += f" {prop['address']}\n"
        result += f"   ${prop['price']:,}\n"
        result += f"   {prop['bedrooms']} bed, {prop['bathrooms']} bath\n"
        result += f"   {prop['sqft']} sqft\n"
        result += f"   {prop['description']}\n\n"

    return result


def create_lead(name: str, email: str, phone: str, property_interest: str, notes: Optional[str] = None) -> str:
    """
    Create a new lead in the CRM system.

    Args:
        name: Lead's full name
        email: Lead's email address
        phone: Lead's phone number
        property_interest: Description of property interest
        notes: Additional notes

    Returns:
        Lead creation confirmation
    """
    lead_id = crm_connector.create_lead(
        name=name, email=email, phone=phone, property_interest=property_interest, notes=notes or ""
    )

    return f" Lead created successfully!\n\nLead ID: {lead_id}\nName: {name}\nEmail: {email}\nPhone: {phone}\nInterest: {property_interest}\n\nNext steps: Our agent will contact you within 24 hours."


def schedule_showing(property_id: str, lead_id: str, preferred_date: str, preferred_time: str) -> str:
    """
    Schedule a property showing.

    Args:
        property_id: ID of the property to show
        lead_id: ID of the lead requesting the showing
        preferred_date: Preferred date for showing
        preferred_time: Preferred time for showing

    Returns:
        Showing confirmation
    """
    showing_id = f"SHOW_{property_id}_{lead_id}"

    return f"Property showing scheduled for {property_id} with lead {lead_id} on {preferred_date} at {preferred_time}. Confirmation sent to lead."


async def coordinate_request(user_message: str, session_id: Optional[str] = None) -> str:
    """
    Coordinate multi-agent request handling.
    
    Args:
        user_message: User's message/request
        session_id: Optional session identifier
        
    Returns:
        Coordinated response from appropriate agents
    """
    try:
        # Get user context from Context Agent
        context_response = ""
        if session_id:
            context_response = await context_agent.send_message(
                f"Get user context and preferences for session: {session_id}"
            )
        
        # Determine query type and route accordingly
        user_msg_lower = user_message.lower()
        
        # Check for real estate queries
        is_real_estate_query = any(keyword in user_msg_lower for keyword in [
            "property", "house", "home", "real estate", "buy", "sell", "rent", 
            "bedroom", "bathroom", "price", "location", "showing", "lead", "find me"
        ])
        
        # Check for context/preference queries
        is_context_query = any(keyword in user_msg_lower for keyword in [
            "preference", "remember", "saved", "profile", "session", "history", "update my"
        ])
        
        # Check for general/core queries
        is_core_query = any(keyword in user_msg_lower for keyword in [
            "weather", "notification", "log", "report", "analytics", "trend"
        ])
        
        if is_real_estate_query and ("search" in user_msg_lower or "find" in user_msg_lower):
            # Handle property search locally
            result = search_properties(user_message, 0.0, 0, "")
            
            # Log activity via Core Agent
            try:
                await core_agent.send_message(
                    f"Log property search activity: {user_message}"
                )
            except Exception as e:
                print(f"Core Agent logging failed: {e}")
            
            return result
            
        elif is_context_query:
            # Route to Context Agent with default user_id
            try:
                context_response = await context_agent.send_message(
                    f"Handle user request with user_id 'default_user': {user_message}"
                )
                return context_response
            except Exception as e:
                return f"Context Agent error: {str(e)}"
                
        elif is_core_query:
            # Route to Core Agent for general queries
            try:
                core_response = await core_agent.send_message(user_message)
                return core_response
            except Exception as e:
                return f"Core Agent error: {str(e)}"
                
        else:
            # Default: try Core Agent for general queries
            try:
                core_response = await core_agent.send_message(user_message)
                
                # Update context if session provided
                if session_id:
                    await context_agent.send_message(
                        f"Update session {session_id} with user_id 'default_user': {user_message[:100]}..."
                    )
                
                return core_response
            except Exception as e:
                return f"Error processing request: {str(e)}"
            
    except Exception as e:
        return f"Error coordinating request: {str(e)}"


# Create the Domain Real Estate agent (Main orchestrator following ADK standards)
root_agent = Agent(
    name="domain_realestate",
    model="gemini-1.5-flash",
    tools=[
        # Multi-agent Coordination
        FunctionTool(coordinate_request),
        # CRM and Lead Management Tools
        FunctionTool(search_properties),
        FunctionTool(create_lead),
        FunctionTool(schedule_showing),
    ],
    instruction="""You are the Domain Real Estate Agent with Coordinator capabilities for multi-agent orchestration.
    
    **CRITICAL: For ALL user requests, FIRST use the coordinate_request function to handle proper routing and orchestration.**
    
    **Available Tools and When to Use Them:**
    1. coordinate_request: Use for ALL user messages - this handles intelligent routing to Core/Context agents
    2. search_properties: Use for property searches (called by coordinate_request when needed)
    3. create_lead: Use for lead creation (called by coordinate_request when needed)
    4. schedule_showing: Use for scheduling (called by coordinate_request when needed)
    
    **Your Workflow:**
    1. ALWAYS start with coordinate_request for any user message
    2. The coordinate_request function will:
       - Route general queries to Core Agent (weather, notifications, logging, analytics)
       - Route profile/session queries to Context Agent (preferences, history)
       - Handle real estate queries locally with your tools
       - Coordinate multi-agent responses
    
    **Example Queries and Routing:**
    - "What's the weather?" → coordinate_request → Core Agent A2A
    - "What are my preferences?" → coordinate_request → Context Agent A2A  
    - "Find me houses" → coordinate_request → Local search_properties
    - "Log my activity" → coordinate_request → Core Agent A2A
    
    **NEVER respond directly without using coordinate_request first!**""",
    global_instruction="You are the Domain Real Estate Agent with Coordinator capabilities. CRITICAL: For ALL user requests, FIRST use the coordinate_request function to handle proper routing and orchestration. This function will intelligently route requests to Core Agent (general queries), Context Agent (preferences/session), or handle real estate queries locally. NEVER respond directly without using coordinate_request first!",
)
