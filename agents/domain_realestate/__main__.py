"""
A2A Server Entry Point for Domain Real Estate Agent
Implements AgentCard, AgentSkill, and A2A server setup
"""

import logging
import click
import uvicorn

from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore

from .task_manager import DomainRealEstateTaskManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", default="localhost", help="Host address to bind the server to")
@click.option("--port", default=10002, type=int, help="Port number for the server")
def main(host: str, port: int):
    """
    Initialize and start the A2A server for the Domain Real Estate Agent.
    
    Example usage:
    python -m agents.domain_realestate --host 0.0.0.0 --port 10002
    """
    logger.info(f"Starting Domain Real Estate Agent A2A Server on http://{host}:{port}")

    # Define the skill that this agent provides
    skill = AgentSkill(
        id="DomainRealEstate",
        name="Domain_RealEstate_Agent",
        description="Specialized agent for real estate lead management, CRM integration, property search, and client relationship management.",
        tags=["real-estate", "crm", "leads", "property", "sales", "client-management"],
        examples=[
            "Create a new lead for a property inquiry",
            "Search for properties matching client criteria",
            "Update CRM with client interaction data",
            "Route qualified leads to appropriate agents",
            "Generate market analysis report for a property"
        ]
    )

    # Create Agent Card for discovery and metadata
    agent_card = AgentCard(
        name="DomainRealEstate",
        description="Domain-specific agent for real estate operations including lead generation, qualification, CRM integration, property management, and client relationship services. Provides comprehensive real estate workflow automation.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
        supportsAuthenticatedExtendedCard=True,
    )

    # Initialize request handler
    request_handler = DefaultRequestHandler(
        agent_executor=DomainRealEstateTaskManager(),
        task_store=InMemoryTaskStore(),
    )

    # Create A2A Starlette application
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    # Start the server
    logger.info("Domain Real Estate Agent A2A server starting...")
    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main()
