"""Core Coordinator Agent for orchestrating multi-agent workflows."""

from google.adk import Agent
from google.adk.tools import FunctionTool, AgentTool
from typing import Dict, Any, List
import time
import asyncio
import httpx


def orchestrate_workflow(task: str, agents: List[str]) -> Dict[str, Any]:
    """
    Orchestrate a workflow across multiple agents.
    
    Args:
        task: The task description
        agents: List of agent names to coordinate
        
    Returns:
        Workflow execution results
    """
    return {
        "task": task,
        "agents": agents,
        "status": "coordinated",
        "message": f"Orchestrating task '{task}' across agents: {', '.join(agents)}"
    }


async def route_request(request: str, domain: str = "general") -> Dict[str, Any]:
    """
    Route requests to appropriate agents and get real responses via A2A protocol.
    
    Args:
        request: The incoming request
        domain: Domain classification (real_estate, general, etc.)
        
    Returns:
        Response from the target agent
    """
    # Agent registry for A2A communication
    agent_registry = {
        "domain_realestate": "http://localhost:10002",
        "context_agent": "http://localhost:10001",
        "llm_agent": "http://localhost:10000"
    }
    
    routing_map = {
        "real_estate": "domain_realestate",
        "general": "llm_agent",
        "profile": "context_agent"
    }
    
    # Determine target agent
    target_agent = routing_map.get(domain, "domain_realestate")  # Default to real estate for property requests
    
    # Auto-detect domain from request content
    request_lower = request.lower()
    if any(keyword in request_lower for keyword in ["house", "property", "real estate", "buy", "sell", "lead", "condo", "apartment"]):
        target_agent = "domain_realestate"
    elif any(keyword in request_lower for keyword in ["profile", "preference", "update", "personalization"]):
        target_agent = "context_agent"
    
    agent_url = agent_registry.get(target_agent)
    if not agent_url:
        return {
            "request": request,
            "domain": domain,
            "target_agent": target_agent,
            "error": f"Agent {target_agent} not available"
        }
    
    # Make real A2A call with improved error handling
    try:
        response = await _call_agent_a2a_sync(agent_url, request)
        return {
            "request": request,
            "domain": domain,
            "target_agent": target_agent,
            "response": response,
            "status": "success",
            "agent_url": agent_url  # For debugging
        }
    except asyncio.TimeoutError:
        return {
            "request": request,
            "domain": domain,
            "target_agent": target_agent,
            "error": f"Timeout communicating with {target_agent} at {agent_url}",
            "status": "timeout"
        }
    except Exception as e:
        return {
            "request": request,
            "domain": domain,
            "target_agent": target_agent,
            "error": f"Failed to communicate with {target_agent}: {str(e)}",
            "status": "error",
            "agent_url": agent_url  # For debugging
        }


async def _call_agent_a2a_sync(agent_url: str, query: str) -> str:
    """
    Make A2A Protocol call to another agent.
    """
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
                "client": "adk-coordinator",
                "timestamp": int(time.time())
            }
        },
        "id": request_id
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
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
                        
                        # Priority 1: Check status message (primary response location for completed tasks)
                        status = task.get("status", {})
                        if "message" in status and status["message"]:
                            status_msg = status["message"]
                            if "parts" in status_msg:
                                content_parts = []
                                for part in status_msg["parts"]:
                                    # Check both 'kind' and 'type' fields for text content
                                    if part.get("kind") == "text" or part.get("type") == "text":
                                        text_content = part.get("text", "")
                                        # Skip generic processing messages
                                        if text_content and "processing your request" not in text_content.lower():
                                            content_parts.append(text_content)
                                if content_parts:
                                    return "\n".join(content_parts)
                        
                        # Priority 2: Check task history for agent responses
                        if "history" in task and task["history"]:
                            # Look for the last agent response (not user message)
                            for msg in reversed(task["history"]):
                                if msg.get("role") == "agent" and "parts" in msg:
                                    content_parts = []
                                    for part in msg["parts"]:
                                        if part.get("kind") == "text" or part.get("type") == "text":
                                            text_content = part.get("text", "")
                                            if text_content and "processing your request" not in text_content.lower():
                                                content_parts.append(text_content)
                                    if content_parts:
                                        return "\n".join(content_parts)
                        
                        # Fallback: Return task completion message
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


# Create the coordinator agent
root_agent = Agent(
    name="coordinator",
    model="gemini-1.5-flash",
    tools=[
        FunctionTool(orchestrate_workflow),
        FunctionTool(route_request),
        # Core Agent Tools (A2A communication)
        # Note: AgentTool requires actual agent instances, not strings
        # These will be configured during deployment for A2A communication
    ],
    instruction="""
    You are the Core Coordinator Agent responsible for:
    1. Orchestrating workflows across multiple agents
    2. Routing requests to appropriate domain agents
    3. Managing inter-agent communication
    4. Ensuring proper task delegation and execution
    
    IMPORTANT: When you receive detailed responses from other agents via the route_request function:
    - ALWAYS display the complete, detailed response from the target agent
    - DO NOT summarize or paraphrase the agent's response
    - DO NOT generate generic messages like "I've sent your request..."
    - Present the agent's response exactly as received, including all details, formatting, and specific information
    - The user wants to see the actual agent responses, not conversational summaries
    
    Always consider the context and route requests to the most appropriate agent.
    """
)
