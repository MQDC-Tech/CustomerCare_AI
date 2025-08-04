"""Lead Router for intelligent lead routing and qualification."""

from datetime import datetime
from typing import Any, Dict, List, Optional


def qualify_lead(lead_data: Dict[str, Any], qualification_criteria: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Qualify a lead based on predefined criteria.

    Args:
        lead_data: Lead information dictionary
        qualification_criteria: Custom qualification criteria

    Returns:
        Lead qualification result
    """
    default_criteria = {
        "budget_minimum": 200000,
        "required_fields": ["name", "email", "phone"],
        "property_types": ["house", "condo", "apartment", "townhouse"],
    }

    criteria = qualification_criteria or default_criteria
    score = 0
    max_score = 100

    # Check required fields
    required_fields = criteria.get("required_fields", [])
    fields_present = sum(1 for field in required_fields if lead_data.get(field))
    if required_fields:
        score += (fields_present / len(required_fields)) * 30

    # Check budget qualification
    budget_range = lead_data.get("budget_range", "")
    if budget_range and "k" in budget_range.lower():
        try:
            budget_num = float(budget_range.lower().replace("k", "").replace("$", "").strip()) * 1000
            if budget_num >= criteria.get("budget_minimum", 0):
                score += 40
        except:
            pass

    # Check property interest
    property_interest = lead_data.get("property_interest", "").lower()
    if property_interest in criteria.get("property_types", []):
        score += 30

    qualification_level = "high" if score >= 80 else "medium" if score >= 50 else "low"

    return {
        "lead_id": lead_data.get("lead_id", "unknown"),
        "qualification_score": score,
        "qualification_level": qualification_level,
        "criteria_met": {
            "required_fields": fields_present == len(required_fields),
            "budget_qualified": score >= 40,
            "property_match": property_interest in criteria.get("property_types", []),
        },
        "message": f"Lead qualified as {qualification_level} priority (score: {score}/100)",
    }


def route_lead_to_agent(lead_data: Dict[str, Any], available_agents: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Route a qualified lead to the most appropriate agent.

    Args:
        lead_data: Lead information
        available_agents: List of available agents with their specialties

    Returns:
        Lead routing decision
    """
    default_agents = [
        {
            "agent_id": "agent_001",
            "name": "Sarah Johnson",
            "specialties": ["luxury", "house"],
            "locations": ["downtown", "suburbs"],
            "current_leads": 5,
            "max_leads": 10,
        },
        {
            "agent_id": "agent_002",
            "name": "Mike Chen",
            "specialties": ["first-time", "condo"],
            "locations": ["city", "urban"],
            "current_leads": 3,
            "max_leads": 8,
        },
    ]

    agents = available_agents or default_agents
    property_interest = lead_data.get("property_interest", "").lower()
    budget_range = lead_data.get("budget_range", "")

    # Simple routing logic - in production this would be more sophisticated
    best_agent = None
    best_score = 0

    for agent in agents:
        if agent["current_leads"] >= agent["max_leads"]:
            continue

        score = 0

        # Match property type specialty
        if property_interest in agent["specialties"]:
            score += 50

        # Prefer agents with lower current load
        load_factor = 1 - (agent["current_leads"] / agent["max_leads"])
        score += load_factor * 30

        # Budget consideration
        if "luxury" in agent["specialties"] and "500k" in budget_range:
            score += 20
        elif "first-time" in agent["specialties"] and any(x in budget_range for x in ["200k", "300k"]):
            score += 20

        if score > best_score:
            best_score = score
            best_agent = agent

    if best_agent:
        return {
            "lead_id": lead_data.get("lead_id"),
            "assigned_agent": best_agent,
            "routing_score": best_score,
            "routing_reason": f"Best match based on specialty and availability",
            "status": "routed",
            "message": f"Lead routed to {best_agent['name']} (Agent ID: {best_agent['agent_id']})",
        }
    else:
        return {
            "lead_id": lead_data.get("lead_id"),
            "assigned_agent": None,
            "status": "unrouted",
            "message": "No available agents found for this lead",
        }


def prioritize_leads(leads: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Prioritize a list of leads based on qualification and urgency.

    Args:
        leads: List of lead dictionaries

    Returns:
        Prioritized lead list
    """
    prioritized = []

    for lead in leads:
        qualification = qualify_lead(lead)
        priority_score = qualification["qualification_score"]

        # Add urgency factors
        created_at = lead.get("created_at", "")
        if created_at:
            # Recent leads get higher priority
            priority_score += 10

        lead_with_priority = {
            **lead,
            "priority_score": priority_score,
            "qualification_level": qualification["qualification_level"],
        }
        prioritized.append(lead_with_priority)

    # Sort by priority score (highest first)
    prioritized.sort(key=lambda x: x["priority_score"], reverse=True)

    return {
        "prioritized_leads": prioritized,
        "total_leads": len(prioritized),
        "high_priority": len([l for l in prioritized if l["qualification_level"] == "high"]),
        "message": f"Prioritized {len(prioritized)} leads",
    }
