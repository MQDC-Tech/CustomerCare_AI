"""
A2A Server Entry Point for Context Agent
Implements AgentCard, AgentSkill, and A2A server setup
"""

import logging
import click
import uvicorn

from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore

from .task_manager import ContextAgentTaskManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", default="localhost", help="Host address to bind the server to")
@click.option("--port", default=10001, type=int, help="Port number for the server")
def main(host: str, port: int):
    """
    Initialize and start the A2A server for the Context Agent.
    
    Example usage:
    python -m agents.context_agent --host 0.0.0.0 --port 10001
    """
    logger.info(f"Starting Context Agent A2A Server on http://{host}:{port}")

    # Define the skill that this agent provides
    skill = AgentSkill(
        id="ContextAgent",
        name="Context_Agent",
        description="Agent responsible for user context management, personalization, and session handling.",
        tags=["context", "personalization", "session", "profile", "user-management"],
        examples=[
            "Update my user profile with new preferences",
            "Retrieve my session data from the last interaction",
            "Personalize recommendations based on my history",
            "Manage my user context and preferences"
        ]
    )

    # Create Agent Card for discovery and metadata
    agent_card = AgentCard(
        name="ContextAgent",
        description="Specialized agent for managing user context, personalization, session data, and profile management. Provides context-aware services and user-specific customization.",
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
        agent_executor=ContextAgentTaskManager(),
        task_store=InMemoryTaskStore(),
    )

    # Create A2A Starlette application
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    # Start the server
    logger.info("Context Agent A2A server starting...")
    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main()
