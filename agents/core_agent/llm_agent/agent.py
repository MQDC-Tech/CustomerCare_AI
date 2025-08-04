"""LLM Agent for handling generic language model tasks."""

import os

# Import utils with absolute path
import sys

from google.adk import Agent
from google.adk.tools import FunctionTool

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from utils.llm import generate_reply, rewrite_text, summarize_text

# Create the LLM agent
root_agent = Agent(
    name="llm_agent",
    model="gemini-1.5-flash",
    tools=[FunctionTool(generate_reply), FunctionTool(summarize_text), FunctionTool(rewrite_text)],
    instruction="""
    You are the LLM Agent responsible for:
    1. Generating replies and responses using language models
    2. Summarizing text content
    3. Rewriting text in different styles
    4. Handling generic language processing tasks
    
    Provide accurate, helpful, and contextually appropriate responses.
    """,
)
