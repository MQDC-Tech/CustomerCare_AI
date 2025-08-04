#!/usr/bin/env python3
"""
Domain Real Estate Agent A2A Server
Implements proper A2A Protocol specification with /v1/messages:send endpoint
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.domain_realestate.agent import root_agent

app = FastAPI(title="Domain Real Estate Agent A2A Server")


# A2A Protocol Models
class MessageContent(BaseModel):
    type: str = "text"
    text: str


class Message(BaseModel):
    content: List[MessageContent]


class MessageSendRequest(BaseModel):
    message: Message
    configuration: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class TaskStatus(BaseModel):
    state: str
    message: str
    timestamp: str


class Task(BaseModel):
    id: str
    contextId: str
    status: TaskStatus
    history: List[Dict[str, Any]] = []
    artifacts: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    kind: str = "task"


# Agent Card endpoint
@app.get("/.well-known/agent.json")
async def get_agent_card():
    """Return agent card for A2A discovery"""
    return {
        "name": "domain_realestate",
        "version": "1.0.0",
        "description": "Domain Real Estate Agent with property search, lead management, and scheduling capabilities",
        "protocolVersion": "0.2.6",
        "url": "http://localhost:8001",
        "capabilities": {"textGeneration": True, "functionCalling": True},
        "skills": [
            {
                "id": "property_search",
                "name": "Property Search",
                "description": "Search for real estate properties based on criteria like price, bedrooms, and location",
                "tags": ["real_estate", "search"],
            },
            {
                "id": "lead_management",
                "name": "Lead Management",
                "description": "Create and manage real estate leads in CRM system",
                "tags": ["crm", "leads"],
            },
            {
                "id": "showing_scheduling",
                "name": "Property Showing Scheduling",
                "description": "Schedule property showings and appointments",
                "tags": ["scheduling", "appointments"],
            },
        ],
    }


# A2A Protocol message endpoint
@app.post("/v1/messages:send")
async def send_message(request: MessageSendRequest):
    """Handle A2A protocol message sending"""
    try:
        # Extract text from message content
        text_content = ""
        for content in request.message.content:
            if content.type == "text":
                text_content += content.text + " "

        text_content = text_content.strip()

        if not text_content:
            raise HTTPException(status_code=400, detail="No text content found in message")

        print(f"🏠 Domain Agent received A2A request: {text_content}")

        # Process the request using the ADK agent
        response = await root_agent.send_message(text_content)

        print(f"🏠 Domain Agent response: {response}")

        # Return response in A2A protocol format
        import time

        task_id = f"task_{int(time.time())}"
        context_id = f"context_{int(time.time())}"

        return Task(
            id=task_id,
            contextId=context_id,
            status=TaskStatus(state="completed", message=response, timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ")),
            metadata=request.metadata,
        )

    except Exception as e:
        print(f"❌ Domain Agent error: {str(e)}")
        import time

        task_id = f"task_{int(time.time())}"
        context_id = f"context_{int(time.time())}"

        return Task(
            id=task_id,
            contextId=context_id,
            status=TaskStatus(
                state="failed", message=f"Error processing request: {str(e)}", timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ")
            ),
            metadata=request.metadata,
        )


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "domain_realestate"}


if __name__ == "__main__":
    print("🏠 Starting Domain Real Estate Agent A2A Server on port 8001...")
    print("📋 Agent Card URL: http://localhost:8001/.well-known/agent.json")
    print("🔗 A2A Endpoint: http://localhost:8001/v1/messages:send")
    uvicorn.run("agents.domain_realestate.a2a_server:app", host="localhost", port=8001, reload=False)
