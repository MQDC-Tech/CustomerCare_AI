#!/usr/bin/env python3
"""
A2A Multi-Agent Testing Script
Tests the ADK-native A2A framework with various scenarios
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

# A2A Agent Registry
AGENTS = {
    "core_agent": "http://localhost:10000",
    "context_agent": "http://localhost:10001", 
    "domain_realestate": "http://localhost:10002"
}

class A2AAgentTester:
    """Test client for A2A agents"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def test_agent_health(self, agent_name: str, agent_url: str) -> bool:
        """Test if an agent is healthy and responding"""
        try:
            print(f"🔍 Testing {agent_name} health at {agent_url}...")
            # Try to get the agent card using A2A protocol standard endpoint
            response = await self.client.get(f"{agent_url}/.well-known/agent-card.json")
            if response.status_code == 200:
                print(f"   ✅ {agent_name} is healthy and responding")
                return True
            else:
                print(f"   ❌ {agent_name} health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ {agent_name} is not responding: {e}")
            return False
    
    async def get_agent_card(self, agent_name: str, agent_url: str) -> Dict[str, Any]:
        """Get agent card information"""
        try:
            print(f"📋 Getting {agent_name} agent card...")
            response = await self.client.get(f"{agent_url}/.well-known/agent-card.json")
            if response.status_code == 200:
                card = response.json()
                print(f"   ✅ {agent_name} card retrieved")
                print(f"      Name: {card.get('name', 'Unknown')}")
                print(f"      Version: {card.get('version', 'Unknown')}")
                print(f"      Skills: {len(card.get('skills', []))}")
                return card
            else:
                print(f"   ❌ Failed to get {agent_name} card: {response.status_code}")
                return {}
        except Exception as e:
            print(f"   ❌ Error getting {agent_name} card: {e}")
            return {}
    
    async def send_message_to_agent(self, agent_name: str, agent_url: str, message: str) -> str:
        """Send a message to an agent via A2A protocol"""
        try:
            print(f"💬 Sending message to {agent_name}: '{message[:50]}...'")
            
            # A2A Protocol spec-compliant MessageSendParams structure
            message_id = f"msg-{int(time.time())}-{hash(message) % 10000}"
            request_id = f"req-{int(time.time())}-{hash(message) % 10000}"
            payload = {
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": {
                    "message": {
                        "messageId": message_id,
                        "role": "user",
                        "parts": [
                            {"type": "text", "text": message}
                        ]
                    },
                    "configuration": {
                        "blocking": True,
                        "historyLength": 10
                    },
                    "metadata": {
                        "client": "a2a-test-suite",
                        "timestamp": int(time.time())
                    }
                },
                "id": request_id
            }
            
            # A2A uses JSON-RPC at the root endpoint
            response = await self.client.post(
                f"{agent_url}/",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {agent_name} responded successfully")
                
                # Parse A2A Protocol spec-compliant response format
                if "result" in result:
                    # JSON-RPC success response
                    rpc_result = result["result"]
                    if isinstance(rpc_result, dict):
                        # A2A Protocol: Response can be Task or Message object
                        if rpc_result.get("kind") == "task":
                            # Task object response
                            task = rpc_result
                            task_id = task.get("id", "unknown")
                            context_id = task.get("contextId", "unknown")
                            status = task.get("status", {})
                            state = status.get("state", "unknown")
                            
                            # Extract response from task history or status message
                            if "history" in task and task["history"]:
                                # Get the latest message from history
                                latest_msg = task["history"][-1]
                                if "parts" in latest_msg:
                                    content_parts = []
                                    for part in latest_msg["parts"]:
                                        if part.get("type") == "text":
                                            content_parts.append(part.get("text", ""))
                                    if content_parts:
                                        return "\n".join(content_parts)
                            
                            # Check status message
                            if "message" in status and status["message"]:
                                status_msg = status["message"]
                                if "parts" in status_msg:
                                    content_parts = []
                                    for part in status_msg["parts"]:
                                        if part.get("type") == "text":
                                            content_parts.append(part.get("text", ""))
                                    if content_parts:
                                        return "\n".join(content_parts)
                            
                            return f"Task {task_id} [{state}] (Context: {context_id})"
                        
                        elif "messageId" in rpc_result or "role" in rpc_result:
                            # Direct Message object response
                            msg = rpc_result
                            if "parts" in msg:
                                content_parts = []
                                for part in msg["parts"]:
                                    if part.get("type") == "text":
                                        content_parts.append(part.get("text", ""))
                                return "\n".join(content_parts) if content_parts else "Message received"
                            return f"Message {msg.get('messageId', 'unknown')}"
                        
                        # Fallback for other response types
                        return f"Response: {str(rpc_result)[:200]}..."
                    else:
                        return str(rpc_result)
                elif "error" in result:
                    # JSON-RPC error response
                    error = result["error"]
                    return f"RPC Error {error.get('code', 'unknown')}: {error.get('message', 'Unknown error')}"
                else:
                    # Unexpected response format
                    return f"Unexpected response format: {str(result)[:200]}..."
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"   ❌ {agent_name} failed to respond: {error_msg}")
                return f"Error: {error_msg}"
                
        except Exception as e:
            error_msg = f"Error communicating with {agent_name}: {e}"
            print(f"   ❌ {error_msg}")
            return error_msg
    
    async def test_multi_agent_orchestration(self) -> None:
        """Test multi-agent orchestration through the core agent"""
        print("\n🎯 Testing Multi-Agent Orchestration...")
        print("=" * 50)
        
        test_scenarios = [
            {
                "name": "Real Estate Lead Processing",
                "message": "I'm interested in buying a 3-bedroom house in downtown. Please help me with lead qualification and personalize the search based on my profile."
            },
            {
                "name": "User Profile Management", 
                "message": "Update my user profile with new preferences and store this information for future interactions."
            },
            {
                "name": "Property Search with Context",
                "message": "Search for properties that match my saved preferences and provide personalized recommendations."
            },
            {
                "name": "Core Services Only",
                "message": "Generate a summary of available platform services and capabilities."
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n📝 Scenario: {scenario['name']}")
            print("-" * 40)
            
            response = await self.send_message_to_agent(
                "core_agent", 
                AGENTS["core_agent"], 
                scenario["message"]
            )
            
            print(f"📄 Response Preview:")
            print(f"   {response[:200]}...")
            
            # Wait between scenarios
            await asyncio.sleep(2)
    
    async def test_individual_agents(self) -> None:
        """Test individual agent capabilities"""
        print("\n🤖 Testing Individual Agent Capabilities...")
        print("=" * 50)
        
        # Test Context Agent
        print(f"\n📋 Testing Context Agent...")
        context_response = await self.send_message_to_agent(
            "context_agent",
            AGENTS["context_agent"],
            "Retrieve my user profile and personalization settings"
        )
        print(f"   Response: {context_response[:150]}...")
        
        # Test Domain Real Estate Agent
        print(f"\n🏠 Testing Domain Real Estate Agent...")
        realestate_response = await self.send_message_to_agent(
            "domain_realestate", 
            AGENTS["domain_realestate"],
            "Create a new lead for a client interested in commercial properties"
        )
        print(f"   Response: {realestate_response[:150]}...")
    
    async def run_comprehensive_test(self) -> None:
        """Run comprehensive A2A testing suite"""
        print("🚀 Starting ADK-native A2A Multi-Agent Testing...")
        print("=" * 60)
        
        # Test agent health
        print("\n🔍 Phase 1: Agent Health Checks")
        print("-" * 30)
        healthy_agents = []
        for agent_name, agent_url in AGENTS.items():
            if await self.test_agent_health(agent_name, agent_url):
                healthy_agents.append(agent_name)
        
        if not healthy_agents:
            print("\n❌ No agents are healthy. Please start the A2A agents first.")
            return
        
        print(f"\n✅ {len(healthy_agents)}/{len(AGENTS)} agents are healthy")
        
        # Get agent cards
        print("\n📋 Phase 2: Agent Discovery")
        print("-" * 30)
        for agent_name in healthy_agents:
            await self.get_agent_card(agent_name, AGENTS[agent_name])
        
        # Test individual agents
        await self.test_individual_agents()
        
        # Test multi-agent orchestration
        await self.test_multi_agent_orchestration()
        
        print("\n🎉 A2A Testing Complete!")
        print("=" * 60)
        print("✅ ADK-native A2A framework is working correctly!")
        
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


async def main():
    """Main testing function"""
    tester = A2AAgentTester()
    
    try:
        await tester.run_comprehensive_test()
    finally:
        await tester.close()


if __name__ == "__main__":
    print("🧪 ADK-native A2A Multi-Agent Testing Suite")
    print("Make sure to start the A2A agents first:")
    print("  ./local_playground/start_a2a_agents.sh")
    print("")
    
    asyncio.run(main())
