"""
Core Agent - Main coordinator for all core functionality
This agent orchestrates the coordinator, llm_agent, memory_agent, and notifications sub-agents
"""

from google.adk import Agent
from google.adk.tools import FunctionTool, AgentTool

# Import functions from sub-agents
from .coordinator.agent import orchestrate_workflow, route_request
from .llm_agent.agent import generate_reply, summarize_text, rewrite_text
from .memory_agent.agent import store_memory, retrieve_memory, update_memory, delete_memory
from .notifications.agent import send_notification, schedule_notification, get_notification_status, send_alert




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
        
        # Orchestration functions
        FunctionTool(orchestrate_workflow),
        FunctionTool(route_request),
    ],
    instruction="""
    You are the Core Agent responsible for coordinating all core platform services:
    
    1. **LLM Services**: Text generation, summarization, rewriting
    2. **Memory Management**: Store, retrieve, and search conversation context
    3. **Notifications**: Send alerts and manage notification workflows
    4. **Orchestration**: Coordinate multi-agent workflows and route requests
    
    Your role is to:
    - Automatically detect which core service is needed based on user requests
    - Coordinate between different core services when complex tasks require multiple services
    - Provide a unified interface for all core platform functionality
    - Maintain context and state across different service interactions
    
    When users interact with you, analyze their request and route it to the appropriate core service,
    or coordinate multiple services if needed. Always provide helpful, accurate responses while
    maintaining the context of the conversation through memory services.
    """
)
