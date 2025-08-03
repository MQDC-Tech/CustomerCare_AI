"""
A2A Task Manager for Context Agent
Implements AgentExecutor interface for A2A communication
"""

import logging
from typing import AsyncGenerator, Dict, Any

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import Task, TaskState
from a2a.utils import new_agent_text_message, new_task

# Import the actual agent implementation
from .agent import root_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextAgentTaskManager(AgentExecutor):
    """
    Implements the AgentExecutor interface to integrate the Context Agent
    into the A2A server framework. This class is responsible for:
    - Managing user context and personalization requests
    - Handling profile management and session data
    - Managing task state updates and streaming responses
    """

    def __init__(self):
        """Initialize the ContextAgentTaskManager with the Context Agent."""
        self.agent = root_agent
        logger.info("ContextAgentTaskManager initialized with Context Agent.")

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        Execute a new task for the Context Agent based on user input.
        
        Args:
            context: Contains information about the current request
            event_queue: Queue to send task updates back to A2A server
        """
        # Extract user input from request context
        query = context.get_user_input()
        logger.info(f"Context Agent executing task for query: {query[:100]}...")

        # Get or create task
        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
            logger.info(f"Created new task with ID: {task.id}")
        else:
            logger.info(f"Continuing existing task with ID: {task.id}")

        # Initialize task updater
        # Handle contextId robustly - A2A SDK implementation may differ from spec
        context_id = getattr(task, 'contextId', None) or getattr(task, 'context_id', None) or task.id
        updater = TaskUpdater(event_queue, task.id, context_id)

        try:
            # Send working status
            await updater.update_status(
                TaskState.working,
                new_agent_text_message(
                    "Context Agent is processing your request...", 
                    context_id, 
                    task.id
                ),
            )

            # Process the request using the Context Agent
            # Since our agent doesn't have an async invoke method, we'll simulate it
            response = await self._process_context_request(query, context_id)

            # Send completion status with response
            logger.info(f"Context Agent task {task.id} completed.")
            message = new_agent_text_message(response, context_id, task.id)
            await updater.update_status(TaskState.completed, message)

        except Exception as e:
            # Handle errors
            logger.exception(f"Error during Context Agent execution for task {task.id}: {e}")
            error_message = f"Context Agent error: {str(e)}"
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(error_message, context_id, task.id),
            )

    async def _process_context_request(self, query: str, context_id: str) -> str:
        """
        Process a context request using the Context Agent.
        
        Args:
            query: User query to process
            context_id: Context ID for the request
            
        Returns:
            Response from the Context Agent
        """
        try:
            # For now, we'll create a simple response
            # In a full implementation, this would integrate with the agent's tools
            response = f"Context Agent processed: {query}\n"
            response += "Available context management capabilities:\n"
            response += "• User profile management\n"
            response += "• Session data handling\n"
            response += "• Personalization services\n"
            response += "• Context-aware recommendations"
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing context request: {e}")
            return f"Error processing context request: {str(e)}"

    async def cancel(self, task_id: str) -> None:
        """Cancel a running task (required by AgentExecutor interface)."""
        logger.info(f"Context Agent task {task_id} cancellation requested.")
        # Implementation for task cancellation if needed
        pass
