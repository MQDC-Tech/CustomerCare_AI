"""Tests for domain agent functionality."""

import os
import sys

import pytest

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from agents.domain_realestate.tools.crm_connector import (
    create_lead,
    get_lead,
    schedule_showing,
    search_properties_crm,
    update_lead,
)
from agents.domain_realestate.tools.lead_router import prioritize_leads, qualify_lead, route_lead_to_agent


class TestCRMConnector:
    """Test CRM connector functionality."""

    def test_create_lead(self):
        """Test lead creation."""
        result = create_lead(
            name="John Doe",
            email="john@example.com",
            phone="555-1234",
            property_interest="house",
            budget_range="400k",
            notes="First time buyer",
        )

        assert result["status"] == "created"
        assert "lead_id" in result
        assert result["data"]["name"] == "John Doe"
        assert result["data"]["email"] == "john@example.com"

    def test_search_properties(self):
        """Test property search functionality."""
        result = search_properties_crm(
            property_type="house", location="downtown", min_price=300000, max_price=500000, bedrooms=3
        )

        assert "results" in result
        assert "count" in result
        assert isinstance(result["results"], list)
        assert result["count"] >= 0

    def test_schedule_showing(self):
        """Test property showing scheduling."""
        result = schedule_showing(property_id="prop_001", lead_id="lead_123", preferred_time="2024-01-15 14:00")

        assert result["status"] == "scheduled"
        assert "showing_id" in result
        assert result["property_id"] == "prop_001"


class TestLeadRouter:
    """Test lead routing functionality."""

    def test_qualify_lead(self):
        """Test lead qualification."""
        lead_data = {
            "lead_id": "test_lead",
            "name": "Jane Smith",
            "email": "jane@example.com",
            "phone": "555-5678",
            "property_interest": "house",
            "budget_range": "500k",
        }

        result = qualify_lead(lead_data)

        assert "qualification_score" in result
        assert "qualification_level" in result
        assert result["qualification_score"] >= 0
        assert result["qualification_level"] in ["low", "medium", "high"]

    def test_route_lead_to_agent(self):
        """Test lead routing to agents."""
        lead_data = {"lead_id": "test_lead", "property_interest": "house", "budget_range": "400k"}

        result = route_lead_to_agent(lead_data)

        assert "status" in result
        assert result["status"] in ["routed", "unrouted"]

    def test_prioritize_leads(self):
        """Test lead prioritization."""
        leads = [
            {
                "lead_id": "lead_1",
                "name": "Lead 1",
                "email": "lead1@example.com",
                "phone": "555-0001",
                "property_interest": "house",
                "budget_range": "300k",
                "created_at": "2024-01-01",
            },
            {
                "lead_id": "lead_2",
                "name": "Lead 2",
                "email": "lead2@example.com",
                "phone": "555-0002",
                "property_interest": "condo",
                "budget_range": "500k",
                "created_at": "2024-01-02",
            },
        ]

        result = prioritize_leads(leads)

        assert "prioritized_leads" in result
        assert "total_leads" in result
        assert len(result["prioritized_leads"]) == 2
        assert result["total_leads"] == 2


def test_domain_agent_integration():
    """Test domain agent integration."""
    # Test that all components work together
    # Create a lead
    lead_result = create_lead(
        name="Test User", email="test@example.com", phone="555-TEST", property_interest="house", budget_range="450k"
    )

    # Qualify the lead
    qualification = qualify_lead(lead_result["data"])

    # Route the lead
    routing = route_lead_to_agent(lead_result["data"])

    assert lead_result["status"] == "created"
    assert qualification["qualification_score"] > 0
    assert routing["status"] in ["routed", "unrouted"]


if __name__ == "__main__":
    pytest.main([__file__])
