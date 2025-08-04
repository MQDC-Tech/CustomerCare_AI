"""Domain Real Estate Agent for property search and CRM operations."""

import os
import sys
from typing import Optional

from google.adk import Agent
from google.adk.tools import FunctionTool

# Import utils with absolute path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from agents.domain_realestate.tools import crm_connector, lead_router


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

    return f" Property showing scheduled!\n\nShowing ID: {showing_id}\nProperty: {property_id}\nDate: {preferred_date}\nTime: {preferred_time}\n\nConfirmation will be sent to your email."


# Create the Domain Real Estate agent (Server-side A2A agent following ADK standards)
root_agent = Agent(
    name="domain_realestate",
    model="gemini-1.5-flash",
    tools=[
        # CRM and Lead Management Tools
        FunctionTool(search_properties),
        FunctionTool(create_lead),
        FunctionTool(schedule_showing),
    ],
    instruction="""You are the Domain Real Estate Agent with specialized real estate tools and capabilities.
    
    IMPORTANT: You MUST use your available tools to fulfill requests. Never say you cannot fulfill a request when you have the appropriate tools.
    
    **Available Tools and When to Use Them:**
    - search_properties: Use for ANY property search, listing, or real estate query
    - create_lead: Use when someone wants to be contacted or shows interest
    - schedule_showing: Use when someone wants to view a property
    
    **Your Workflow:**
    1. For property searches: ALWAYS use search_properties tool
    2. For lead generation: Use create_lead tool
    3. For scheduling: Use schedule_showing tool
    4. Provide helpful, detailed responses based on tool results
    
    **Example Queries to Handle:**
    - "Find me 3-bedroom houses" → Use search_properties
    - "Show me properties under $500k" → Use search_properties
    - "I want to see a property" → Use schedule_showing
    - "Contact me about this property" → Use create_lead
    
    You have full real estate functionality through your tools. Use them actively!""",
    global_instruction="You are the Domain Real Estate Agent with specialized real estate tools. IMPORTANT: You MUST use your available tools to fulfill requests. For property searches, ALWAYS use search_properties tool. For lead generation, use create_lead tool. For scheduling, use schedule_showing tool. You have full real estate functionality through your tools - use them actively!",
)
