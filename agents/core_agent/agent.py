"""
Core Agent - Shared core functionality and services
This agent provides LLM, memory, and notification services for the multi-agent system
"""

from google.adk import Agent
from google.adk.tools import FunctionTool

# Import functions from sub-agents
from .llm_agent.agent import generate_reply, rewrite_text, summarize_text
from .memory_agent.agent import delete_memory, retrieve_memory, store_memory, update_memory
from .notifications.agent import get_notification_status, schedule_notification, send_alert, send_notification


def coordinate_core_services(request: str, service_type: str = "auto") -> str:
    """
    Coordinate between core services based on the request type.

    Args:
        request: The user request or task
        service_type: Type of service needed (auto, llm, memory, notification)

    Returns:
        Response from the appropriate core service
    """
    if service_type == "auto":
        # Auto-detect the best service based on request content
        if "remember" in request.lower() or "recall" in request.lower():
            service_type = "memory"
        elif "notify" in request.lower() or "alert" in request.lower():
            service_type = "notification"
        else:
            service_type = "llm"

    if service_type == "llm":
        return generate_reply(request)
    elif service_type == "memory":
        return retrieve_memory(request)
    elif service_type == "notification":
        return send_notification(request, "user", "info")
    else:
        return generate_reply(f"Processing request: {request}")


def get_core_status() -> str:
    """Get status of all core services."""
    return "Core Agent: All services (LLM, Memory, Notifications) are operational"


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
    ],
    instruction="""You are the Core Agent providing shared services for the multi-agent system.
    
    **Your role:** Provide core platform services including LLM, memory, and notifications.
    
    **Available services:**
    1. **LLM Services**: Text generation, summarization, rewriting
    2. **Memory Management**: Store, retrieve, update, delete conversation context
    3. **Notifications**: Send alerts, schedule notifications, check status
    4. **Service Coordination**: Route requests to appropriate core services
    
    **Your workflow:**
    1. Analyze the user's request
    2. Determine the appropriate core service (LLM, memory, or notifications)
    3. Use the relevant function tools to process the request
    4. Provide complete and helpful responses
    
    **Service Guidelines:**
    - Use LLM functions for text processing, generation, and analysis
    - Use memory functions for storing/retrieving conversation context
    - Use notification functions for alerts and scheduling
    - Use coordinate_core_services for complex multi-service requests
    
    You are a reliable backend service agent focused on core platform functionality.
    """,
)
