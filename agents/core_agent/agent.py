"""
Core Agent - Main coordinator for all core functionality
This agent orchestrates the coordinator, llm_agent, memory_agent, and notifications sub-agents
"""

from google.adk import Agent
from google.adk.tools import AgentTool, FunctionTool

# Import the coordinator root agent (A2A orchestrator)
from .coordinator.agent import root_agent as coordinator_agent

# Import functions from sub-agents
from .llm_agent.agent import generate_reply, rewrite_text, summarize_text
from .memory_agent.agent import delete_memory, retrieve_memory, store_memory, update_memory
from .notifications.agent import get_notification_status, schedule_notification, send_alert, send_notification


def coordinate_core_services(request: str, service_type: str = "auto") -> str:
    """
    Coordinate between core services based on the request type.

    Args:
        request: The user request or task
        service_type: Type of service needed (auto, llm, memory, notification, orchestration)

    Returns:
        Response from the appropriate core service
    """
    if service_type == "auto":
        # Auto-detect the best service based on request content
        if "remember" in request.lower() or "recall" in request.lower():
            service_type = "memory"
        elif "notify" in request.lower() or "alert" in request.lower():
            service_type = "notification"
        elif "orchestrate" in request.lower() or "workflow" in request.lower():
            service_type = "orchestration"
        else:
            service_type = "llm"

    if service_type == "llm":
        return generate_reply(request)
    elif service_type == "memory":
        return retrieve_memory(request)
    elif service_type == "notification":
        return send_notification(request, "user", "info")
    elif service_type == "orchestration":
        return orchestrate_workflow(request)
    else:
        return generate_reply(f"Processing request: {request}")


def get_core_status() -> str:
    """Get status of all core services."""
    return "Core Agent: All services (LLM, Memory, Notifications, Coordinator) are operational"


# Create the main core agent
root_agent = Agent(
    name="core_agent",
    model="gemini-1.5-flash",
    tools=[
        # Main coordination function
        FunctionTool(coordinate_core_services),
        FunctionTool(get_core_status),
        # LLM functions
        FunctionTool(generate_reply),
        FunctionTool(summarize_text),
        FunctionTool(rewrite_text),
        # Memory functions
        FunctionTool(store_memory),
        FunctionTool(retrieve_memory),
        FunctionTool(update_memory),
        FunctionTool(delete_memory),
        # Notification functions
        FunctionTool(send_notification),
        FunctionTool(schedule_notification),
        FunctionTool(get_notification_status),
        FunctionTool(send_alert),
        # Coordinator agent tool (for A2A orchestration)
        AgentTool(coordinator_agent),
    ],
    instruction="""    You are the Core Agent responsible for coordinating all core platform services.
    
    IMPORTANT: For real estate queries, user preferences, or multi-agent workflows, 
    you MUST use the coordinator agent tool to delegate to specialized agents.
    
    **When to use the coordinator agent tool:**
    - Real estate queries (property search, listings, CRM, market info)
    - User preferences and personalization (saving preferences, profiles)
    - Multi-agent workflows requiring coordination
    
    **Available services:**
    1. **LLM Services**: Text generation, summarization, rewriting (use direct functions)
    2. **Memory Management**: Store, retrieve conversation context (use direct functions)
    3. **Notifications**: Send alerts and notifications (use direct functions)
    4. **A2A Orchestration**: Real estate and user preference tasks (use coordinator agent tool)
    
    **Your workflow:**
    1. Analyze the user's request
    2. If it's about real estate or user preferences → use coordinator agent tool
    3. If it's about LLM, memory, or notifications → use direct function tools
    4. Always provide complete responses from the appropriate service
    
    Remember: The coordinator agent tool connects to specialized remote agents for 
    real estate and personalization tasks. Use it for any property-related or 
    user preference queries.
    """,
)
