"""
A2A Server Entry Point for Core Agent (Orchestrator)
Implements AgentCard, AgentSkill, and A2A server setup for multi-agent orchestration
"""

import logging
import click
import uvicorn

from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore

from .task_manager import CoreAgentTaskManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", default="localhost", help="Host address to bind the server to")
@click.option("--port", default=10000, type=int, help="Port number for the server")
def main(host: str, port: int):
    """
    Initialize and start the A2A server for the Core Agent (Orchestrator).
    
    Example usage:
    python -m agents.core_agent --host 0.0.0.0 --port 10000
    """
    logger.info(f"Starting Core Agent (Orchestrator) A2A Server on http://{host}:{port}")

    # Define the skill that this agent provides
    skill = AgentSkill(
        id="CoreAgentOrchestrator",
        name="Core_Agent_Orchestrator",
        description="Central orchestrator agent that coordinates multi-agent workflows, provides core platform services (LLM, memory, notifications), and manages complex task delegation across specialized agents.",
        tags=["orchestrator", "coordination", "llm", "memory", "notifications", "workflow", "multi-agent"],
        examples=[
            "Coordinate a real estate lead qualification workflow",
            "Process a complex request involving user context and property search",
            "Manage memory storage and retrieval across agents",
            "Send notifications and alerts to users",
            "Generate responses using LLM capabilities",
            "Orchestrate multi-step workflows across specialized agents"
        ]
    )

    # Create Agent Card for discovery and metadata
    agent_card = AgentCard(
        name="CoreAgentOrchestrator",
        description="Central orchestrator and coordinator for the multi-agent B2B Customer Care Platform. Provides core services including LLM processing, memory management, notifications, and intelligent task delegation to specialized agents (Context, Domain Real Estate). Capable of handling both simple requests and complex multi-agent workflows.",
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
        agent_executor=CoreAgentTaskManager(),
        task_store=InMemoryTaskStore(),
    )

    # Create A2A Starlette application
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    # Start the server
    logger.info("Core Agent (Orchestrator) A2A server starting...")
    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main()
