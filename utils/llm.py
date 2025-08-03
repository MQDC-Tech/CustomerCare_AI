"""LLM utility functions for the ADK multi-agent system."""

import os
from typing import Dict, Any, Optional
import google.generativeai as genai
from google.cloud import aiplatform


def initialize_llm():
    """Initialize the LLM with proper configuration."""
    # Configure Gemini API
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
    
    # Initialize Vertex AI
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
    
    if project_id:
        aiplatform.init(project=project_id, location=location)


def generate_reply(prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate a reply using the configured LLM.
    
    Args:
        prompt: The input prompt
        context: Optional context dictionary
        
    Returns:
        Generated response string
    """
    try:
        # Use Gemini for text generation
        model = genai.GenerativeModel('gemini-pro')
        
        # Add context to prompt if provided
        if context:
            context_str = f"Context: {context}\n\n"
            full_prompt = context_str + prompt
        else:
            full_prompt = prompt
            
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        return f"Error generating response: {str(e)}"


def summarize_text(text: str, max_length: int = 200) -> str:
    """
    Summarize the given text.
    
    Args:
        text: Text to summarize
        max_length: Maximum length of summary
        
    Returns:
        Summarized text
    """
    prompt = f"Summarize the following text in {max_length} characters or less:\n\n{text}"
    return generate_reply(prompt)


def rewrite_text(text: str, style: str = "professional") -> str:
    """
    Rewrite text in a specific style.
    
    Args:
        text: Text to rewrite
        style: Writing style (professional, casual, formal, etc.)
        
    Returns:
        Rewritten text
    """
    prompt = f"Rewrite the following text in a {style} style:\n\n{text}"
    return generate_reply(prompt)
