#!/usr/bin/env python3
"""
Context Agent A2A Server
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

from agents.context_agent.agent import root_agent

app = FastAPI(title="Context Agent A2A Server")


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
        "name": "context_agent",
        "version": "1.0.0",
        "description": "Context Agent for user personalization, session management, and preference handling",
        "protocolVersion": "0.2.6",
        "url": "http://localhost:8002",
        "capabilities": {"textGeneration": True, "functionCalling": True},
        "skills": [
            {
                "id": "session_management",
                "name": "Session Management",
                "description": "Manage user session lifecycle and context",
                "tags": ["session", "context"],
            },
            {
                "id": "personalization",
                "name": "Response Personalization",
                "description": "Personalize responses based on user preferences and history",
                "tags": ["personalization", "preferences"],
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

        print(f"👤 Context Agent received A2A request: {text_content}")

        # Process the request using the ADK agent
        response = await root_agent.send_message(text_content)

        print(f"👤 Context Agent response: {response}")

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
        print(f"❌ Context Agent error: {str(e)}")
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
    return {"status": "healthy", "agent": "context_agent"}


if __name__ == "__main__":
    print("👤 Starting Context Agent A2A Server on port 8002...")
    print("📋 Agent Card URL: http://localhost:8002/.well-known/agent.json")
    print("🔗 A2A Endpoint: http://localhost:8002/v1/messages:send")
    uvicorn.run("agents.context_agent.a2a_server:app", host="localhost", port=8002, reload=False)
