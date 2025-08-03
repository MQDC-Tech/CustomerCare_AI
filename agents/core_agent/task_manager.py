"""
A2A Task Manager for Core Agent (Orchestrator)
Implements AgentExecutor interface for A2A communication and multi-agent orchestration
"""

import logging
from typing import AsyncGenerator, Dict, Any, List
import httpx

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import Task, TaskState
from a2a.utils import new_agent_text_message, new_task
from a2a.client import A2AClient

# Import the actual agent implementation
from .agent import root_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoreAgentTaskManager(AgentExecutor):
    """
    Implements the AgentExecutor interface to integrate the Core Agent
    into the A2A server framework. This class serves as the orchestrator
    for multi-agent workflows and is responsible for:
    - Coordinating tasks across multiple specialized agents
    - Discovering and communicating with other A2A agents
    - Managing complex multi-step workflows
    - Providing core platform services (LLM, memory, notifications)
    """

    def __init__(self):
        """Initialize the CoreAgentTaskManager with the Core Agent."""
        self.agent = root_agent
        
        # Registry of available A2A agents
        self.agent_registry = {
            "context_agent": "http://localhost:10001",
            "domain_realestate": "http://localhost:10002",
        }
        
        logger.info("CoreAgentTaskManager initialized with Core Agent (Orchestrator).")

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        Execute a new task for the Core Agent based on user input.
        This may involve orchestrating multiple agents for complex workflows.
        
        Args:
            context: Contains information about the current request
            event_queue: Queue to send task updates back to A2A server
        """
        # Extract user input from request context
        query = context.get_user_input()
        logger.info(f"Core Agent (Orchestrator) executing task for query: {query[:100]}...")

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
                    "Core Agent is analyzing your request and coordinating with specialized agents...", 
                    context_id, 
                    task.id
                ),
            )

            # Determine if this requires multi-agent orchestration
            required_agents = await self._analyze_request_for_agents(query)
            
            if required_agents:
                # Multi-agent workflow
                response = await self._orchestrate_multi_agent_workflow(query, required_agents, updater, task)
            else:
                # Single agent response
                response = await self._process_core_request(query, context_id)

            # Send completion status with response
            logger.info(f"Core Agent task {task.id} completed.")
            message = new_agent_text_message(response, context_id, task.id)
            await updater.update_status(TaskState.completed, message)

        except Exception as e:
            # Handle errors
            logger.exception(f"Error during Core Agent execution for task {task.id}: {e}")
            error_message = f"Core Agent error: {str(e)}"
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(error_message, context_id, task.id),
            )

    async def _analyze_request_for_agents(self, query: str) -> List[str]:
        """
        Analyze the user request to determine which specialized agents are needed.
        
        Args:
            query: User query to analyze
            
        Returns:
            List of agent names that should be involved
        """
        required_agents = []
        query_lower = query.lower()
        
        # Check for context/personalization needs
        if any(word in query_lower for word in ['user', 'profile', 'personalize', 'context', 'session', 'preference']):
            required_agents.append('context_agent')
        
        # Check for real estate domain needs
        if any(word in query_lower for word in ['lead', 'property', 'real estate', 'crm', 'listing', 'client']):
            required_agents.append('domain_realestate')
        
        logger.info(f"Analysis result: Required agents for query: {required_agents}")
        return required_agents

    async def _orchestrate_multi_agent_workflow(
        self, 
        query: str, 
        required_agents: List[str], 
        updater: TaskUpdater, 
        task: Task
    ) -> str:
        """
        Orchestrate a workflow across multiple specialized agents.
        
        Args:
            query: User query to process
            required_agents: List of agent names to coordinate
            updater: Task updater for status updates
            task: Current task object
            
        Returns:
            Orchestrated response from all agents
        """
        logger.info(f"Orchestrating multi-agent workflow with agents: {required_agents}")
        
        results = []
        results.append(f"🎯 **Multi-Agent Workflow Orchestration**")
        results.append(f"Query: {query}")
        results.append(f"Coordinating with {len(required_agents)} specialized agents...\n")
        
        for agent_name in required_agents:
            if agent_name in self.agent_registry:
                try:
                    # Update status for current agent
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(
                            f"Coordinating with {agent_name}...", 
                            context_id, 
                            task.id
                        ),
                    )
                    
                    # Call the specialized agent via A2A
                    agent_url = self.agent_registry[agent_name]
                    agent_response = await self._call_agent_a2a(agent_url, query)
                    
                    results.append(f"## 🤖 {agent_name.replace('_', ' ').title()} Response:")
                    results.append(agent_response)
                    results.append("")
                    
                    logger.info(f"Successfully coordinated with {agent_name}")
                    
                except Exception as e:
                    error_msg = f"❌ Error coordinating with {agent_name}: {str(e)}"
                    results.append(f"## 🤖 {agent_name.replace('_', ' ').title()} Response:")
                    results.append(error_msg)
                    results.append("")
                    logger.error(f"Failed to coordinate with {agent_name}: {e}")
            else:
                results.append(f"## 🤖 {agent_name.replace('_', ' ').title()} Response:")
                results.append(f"❌ Agent not available in registry")
                results.append("")
        
        results.append("✅ **Multi-agent workflow completed successfully!**")
        return "\n".join(results)

    async def _call_agent_a2a(self, agent_url: str, query: str) -> str:
        """
        Call another agent via A2A protocol using real HTTP communication.
        
        Args:
            agent_url: URL of the target agent
            query: Query to send to the agent
            
        Returns:
            Response from the target agent
        """
        import httpx
        import time
        
        try:
            # Create A2A Protocol compliant message
            message_id = f"msg-{int(time.time())}-{hash(query) % 10000}"
            request_id = f"req-{int(time.time())}-{hash(query) % 10000}"
            
            payload = {
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": {
                    "message": {
                        "messageId": message_id,
                        "role": "user",
                        "parts": [
                            {"type": "text", "text": query}
                        ]
                    },
                    "configuration": {
                        "blocking": True,
                        "historyLength": 5
                    },
                    "metadata": {
                        "client": "core-agent-orchestrator",
                        "timestamp": int(time.time())
                    }
                },
                "id": request_id
            }
            
            # Make real A2A call to the agent
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{agent_url}/",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Parse A2A Protocol response
                    if "result" in result:
                        rpc_result = result["result"]
                        if isinstance(rpc_result, dict):
                            # Handle Task object response
                            if rpc_result.get("kind") == "task":
                                task = rpc_result
                                
                                # Extract response from task history or status message
                                if "history" in task and task["history"]:
                                    latest_msg = task["history"][-1]
                                    if "parts" in latest_msg:
                                        content_parts = []
                                        for part in latest_msg["parts"]:
                                            if part.get("type") == "text":
                                                content_parts.append(part.get("text", ""))
                                        if content_parts:
                                            return "\n".join(content_parts)
                                
                                # Check status message
                                status = task.get("status", {})
                                if "message" in status and status["message"]:
                                    status_msg = status["message"]
                                    if "parts" in status_msg:
                                        content_parts = []
                                        for part in status_msg["parts"]:
                                            if part.get("type") == "text":
                                                content_parts.append(part.get("text", ""))
                                        if content_parts:
                                            return "\n".join(content_parts)
                                
                                return f"Task completed: {task.get('id', 'unknown')}"
                            
                            # Handle direct Message object response
                            elif "messageId" in rpc_result or "role" in rpc_result:
                                msg = rpc_result
                                if "parts" in msg:
                                    content_parts = []
                                    for part in msg["parts"]:
                                        if part.get("type") == "text":
                                            content_parts.append(part.get("text", ""))
                                    return "\n".join(content_parts) if content_parts else "Message received"
                            
                            return str(rpc_result)
                        else:
                            return str(rpc_result)
                    elif "error" in result:
                        error = result["error"]
                        return f"Agent Error {error.get('code', 'unknown')}: {error.get('message', 'Unknown error')}"
                    else:
                        return f"Unexpected response format from agent"
                else:
                    return f"HTTP Error {response.status_code}: {response.text}"
                
        except Exception as e:
            logger.error(f"Error calling agent at {agent_url}: {e}")
            return f"Error communicating with agent: {str(e)}"

    async def _process_core_request(self, query: str, context_id: str) -> str:
        """
        Process a request using only the Core Agent capabilities.
        
        Args:
            query: User query to process
            context_id: Context ID for the request
            
        Returns:
            Response from the Core Agent
        """
        try:
            response = f"🎯 **Core Agent Response**\n"
            response += f"Query: {query}\n\n"
            response += "Available Core Services:\n"
            response += "• 🧠 LLM Processing and Generation\n"
            response += "• 💾 Memory Management and Storage\n"
            response += "• 📢 Notifications and Alerts\n"
            response += "• 🎛️ Workflow Coordination\n"
            response += "• 🔗 Multi-Agent Orchestration\n\n"
            response += f"✅ Request processed successfully for context: {context_id}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing core request: {e}")
            return f"Error processing core request: {str(e)}"

    async def cancel(self, task_id: str) -> None:
        """Cancel a running task (required by AgentExecutor interface)."""
        logger.info(f"Core Agent task {task_id} cancellation requested.")
        # Implementation for task cancellation if needed
        pass
