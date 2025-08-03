"""
Local ADK Playground Setup for Testing Multi-Agent System
Run and test all agents locally with ADK's built-in development UI
"""

import os
import subprocess
import json
from typing import Dict, Any, List
import asyncio


def setup_local_adk_playground():
    """
    Set up local ADK playground for testing all agents.
    """
    
    playground_config = {
        "playground": {
            "name": "CustomerCare Multi-Agent Playground",
            "description": "Local testing environment for B2B Customer Care agents",
            "version": "1.0.0"
        },
        
        "agents": {
            "core_agents": {
                "manifest": "manifests/core_agent.manifest.yaml",
                "agents": ["coordinator", "llm_agent", "memory_agent", "notifications"],
                "local_port": 8080,
                "ui_enabled": True
            },
            "context_agent": {
                "manifest": "manifests/context_agent.manifest.yaml", 
                "agents": ["context_agent"],
                "local_port": 8081,
                "ui_enabled": True
            },
            "domain_agent": {
                "manifest": "manifests/domain_realestate.manifest.yaml",
                "agents": ["domain_realestate"], 
                "local_port": 8082,
                "ui_enabled": True
            }
        },
        
        "playground_features": {
            "agent_chat_ui": True,
            "tool_testing": True,
            "a2a_communication_viewer": True,
            "conversation_history": True,
            "agent_metrics": True,
            "debug_mode": True
        },
        
        "local_discovery": {
            "enabled": True,
            "registry_port": 8090,
            "health_check_interval": 10
        }
    }
    
    return playground_config


def create_playground_startup_script():
    """
    Create script to start all agents in ADK playground mode.
    """
    
    startup_script = """#!/bin/bash
set -e

echo "🎮 Starting ADK Playground for Multi-Agent System"
echo "=================================================="

# Activate virtual environment
source venv/bin/activate

# Set environment variables for local development
export ADK_PLAYGROUND_MODE=true
export ADK_DEBUG=true
export A2A_LOCAL_DISCOVERY=true
export PYTHONPATH=$(pwd)

# Create logs directory
mkdir -p logs/playground

echo "🚀 Starting agents in playground mode..."

# Start Core Agents (in background)
echo "📡 Starting Core Agents..."
adk run --manifest manifests/core_agent.manifest.yaml \\
    --port 8080 \\
    --ui \\
    --debug \\
    --log-file logs/playground/core_agents.log &
CORE_PID=$!

# Wait a moment for core agents to start
sleep 3

# Start Context Agent (in background)  
echo "👤 Starting Context Agent..."
adk run --manifest manifests/context_agent.manifest.yaml \\
    --port 8081 \\
    --ui \\
    --debug \\
    --log-file logs/playground/context_agent.log &
CONTEXT_PID=$!

# Wait a moment for context agent to start
sleep 3

# Start Domain Agent (in background)
echo "🏠 Starting Domain Agent..."
adk run --manifest manifests/domain_realestate.manifest.yaml \\
    --port 8082 \\
    --ui \\
    --debug \\
    --log-file logs/playground/domain_agent.log &
DOMAIN_PID=$!

# Wait for all agents to start
sleep 5

echo ""
echo "✅ ADK Playground Started Successfully!"
echo "======================================"
echo ""
echo "🌐 Agent UIs Available:"
echo "   • Core Agents:    http://localhost:8080"
echo "   • Context Agent:  http://localhost:8081" 
echo "   • Domain Agent:   http://localhost:8082"
echo ""
echo "🔧 Playground Features:"
echo "   • Interactive chat with each agent"
echo "   • Tool testing and debugging"
echo "   • A2A communication visualization"
echo "   • Real-time agent metrics"
echo "   • Conversation history"
echo ""
echo "🧪 Test Commands:"
echo "   • Test A2A communication: python local_playground/test_a2a_local.py"
echo "   • Run agent workflows: python local_playground/test_workflows.py"
echo "   • Load test agents: python local_playground/load_test.py"
echo ""
echo "⏹️  To stop all agents: ./local_playground/stop_playground.sh"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping ADK Playground..."
    kill $CORE_PID $CONTEXT_PID $DOMAIN_PID 2>/dev/null || true
    echo "✅ Playground stopped."
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Keep script running and show logs
echo "📊 Monitoring agent logs (Ctrl+C to stop):"
echo "==========================================="
tail -f logs/playground/*.log
"""
    
    return startup_script


def create_playground_stop_script():
    """
    Create script to stop playground.
    """
    
    stop_script = """#!/bin/bash
echo "🛑 Stopping ADK Playground..."

# Kill all ADK processes
pkill -f "adk run" || true

# Kill processes on playground ports
lsof -ti:8080,8081,8082,8090 | xargs kill -9 2>/dev/null || true

echo "✅ ADK Playground stopped."
"""
    
    return stop_script


def create_local_a2a_test():
    """
    Create test script for local A2A communication.
    """
    
    test_script = """
import asyncio
import aiohttp
import json
from typing import Dict, Any


async def test_local_a2a_communication():
    \"\"\"Test A2A communication between locally running agents.\"\"\"
    
    print("🧪 Testing Local A2A Communication")
    print("==================================")
    
    # Local agent endpoints
    agents = {
        "core_agents": "http://localhost:8080",
        "context_agent": "http://localhost:8081", 
        "domain_agent": "http://localhost:8082"
    }
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Check all agents are running
        print("\\n1️⃣ Checking Agent Health:")
        for name, url in agents.items():
            try:
                async with session.get(f"{url}/health") as response:
                    if response.status == 200:
                        print(f"   ✅ {name}: Running on {url}")
                    else:
                        print(f"   ❌ {name}: Health check failed")
            except Exception as e:
                print(f"   ❌ {name}: Not reachable - {e}")
        
        # Test 2: Test A2A communication flow
        print("\\n2️⃣ Testing A2A Communication Flow:")
        
        # Send request to domain agent that triggers A2A calls
        test_request = {
            "action": "process_customer_inquiry",
            "data": {
                "user_id": "playground_user_123",
                "inquiry": "I need help finding a 3-bedroom house",
                "test_mode": True
            }
        }
        
        try:
            async with session.post(
                f"{agents['domain_agent']}/chat",
                json=test_request
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ Domain Agent Response: {result.get('status', 'success')}")
                    
                    # Check if A2A calls were made
                    a2a_calls = result.get('a2a_calls', [])
                    if a2a_calls:
                        print(f"   🔗 A2A Calls Made: {len(a2a_calls)}")
                        for call in a2a_calls:
                            print(f"      - {call.get('from_agent')} → {call.get('to_agent')}")
                    else:
                        print(f"   ℹ️  No A2A calls recorded (may be internal)")
                        
                else:
                    print(f"   ❌ Domain Agent Request Failed: {response.status}")
                    
        except Exception as e:
            print(f"   ❌ A2A Communication Test Failed: {e}")
        
        # Test 3: Test individual agent capabilities
        print("\\n3️⃣ Testing Individual Agent Capabilities:")
        
        # Test Context Agent
        try:
            context_request = {
                "action": "fetch_user_profile",
                "user_id": "playground_user_123"
            }
            
            async with session.post(
                f"{agents['context_agent']}/chat",
                json=context_request
            ) as response:
                
                if response.status == 200:
                    print(f"   ✅ Context Agent: Profile retrieval working")
                else:
                    print(f"   ❌ Context Agent: Request failed")
                    
        except Exception as e:
            print(f"   ❌ Context Agent Test Failed: {e}")
        
        # Test Core Agents
        try:
            llm_request = {
                "action": "generate_reply",
                "prompt": "Hello, this is a test message"
            }
            
            async with session.post(
                f"{agents['core_agents']}/chat",
                json=llm_request
            ) as response:
                
                if response.status == 200:
                    print(f"   ✅ Core Agents: LLM processing working")
                else:
                    print(f"   ❌ Core Agents: Request failed")
                    
        except Exception as e:
            print(f"   ❌ Core Agents Test Failed: {e}")
    
    print("\\n🎯 Local A2A Testing Complete!")
    print("\\n💡 Next Steps:")
    print("   • Open agent UIs in browser to interact manually")
    print("   • Check logs in logs/playground/ for detailed information")
    print("   • Use ADK playground UI for visual debugging")


if __name__ == "__main__":
    asyncio.run(test_local_a2a_communication())
"""
    
    return test_script


def create_playground_workflow_tests():
    """
    Create workflow tests for playground.
    """
    
    workflow_tests = """
import requests
import json
import time
from typing import Dict, Any


def test_real_estate_workflow():
    \"\"\"Test complete real estate workflow in playground.\"\"\"
    
    print("🏠 Testing Real Estate Workflow")
    print("==============================")
    
    # Domain agent endpoint
    domain_url = "http://localhost:8082"
    
    # Test scenarios
    scenarios = [
        {
            "name": "New Lead Creation",
            "request": {
                "action": "create_lead",
                "data": {
                    "name": "John Playground",
                    "email": "john@playground.com",
                    "phone": "555-PLAY",
                    "property_interest": "house",
                    "budget_range": "400k-500k",
                    "notes": "First time buyer, playground test"
                }
            }
        },
        {
            "name": "Property Search",
            "request": {
                "action": "search_properties", 
                "data": {
                    "property_type": "house",
                    "location": "downtown",
                    "min_price": 300000,
                    "max_price": 500000,
                    "bedrooms": 3
                }
            }
        },
        {
            "name": "Lead Qualification",
            "request": {
                "action": "qualify_lead",
                "data": {
                    "lead_id": "playground_lead_123",
                    "name": "Jane Playground",
                    "email": "jane@playground.com", 
                    "phone": "555-TEST",
                    "property_interest": "house",
                    "budget_range": "500k"
                }
            }
        }
    ]
    
    # Run test scenarios
    for i, scenario in enumerate(scenarios, 1):
        print(f"\\n{i}️⃣ {scenario['name']}:")
        
        try:
            response = requests.post(
                f"{domain_url}/chat",
                json=scenario['request'],
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {result.get('message', 'Completed')}")
                
                # Show A2A communication if available
                if 'a2a_calls' in result:
                    print(f"   🔗 A2A Calls: {len(result['a2a_calls'])}")
                    
            else:
                print(f"   ❌ Failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Small delay between tests
        time.sleep(1)
    
    print("\\n🎯 Real Estate Workflow Testing Complete!")


def test_user_personalization_workflow():
    \"\"\"Test user personalization workflow.\"\"\"
    
    print("\\n👤 Testing User Personalization Workflow")
    print("========================================")
    
    context_url = "http://localhost:8081"
    
    # Test user profile management
    test_user_id = "playground_user_456"
    
    # Create/update user profile
    profile_request = {
        "action": "update_user_profile",
        "data": {
            "user_id": test_user_id,
            "updates": {
                "name": "Playground User",
                "preferences": {
                    "communication_style": "casual",
                    "language": "en",
                    "timezone": "PST"
                },
                "context": {
                    "industry": "real_estate",
                    "role": "buyer",
                    "interests": ["houses", "condos"]
                }
            }
        }
    }
    
    try:
        response = requests.post(
            f"{context_url}/chat",
            json=profile_request,
            timeout=30
        )
        
        if response.status_code == 200:
            print("   ✅ User Profile Updated Successfully")
        else:
            print(f"   ❌ Profile Update Failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Profile Update Error: {e}")
    
    # Test personalized response
    personalization_request = {
        "action": "personalize_response",
        "data": {
            "user_id": test_user_id,
            "base_response": "Here are the properties that match your criteria."
        }
    }
    
    try:
        response = requests.post(
            f"{context_url}/chat", 
            json=personalization_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Response Personalization Working")
            print(f"   📝 Style Applied: {result.get('style_applied', 'N/A')}")
        else:
            print(f"   ❌ Personalization Failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Personalization Error: {e}")


if __name__ == "__main__":
    test_real_estate_workflow()
    test_user_personalization_workflow()
    
    print("\\n🎮 Playground Testing Complete!")
    print("\\n💡 Open these URLs in your browser:")
    print("   • http://localhost:8080 - Core Agents UI")
    print("   • http://localhost:8081 - Context Agent UI") 
    print("   • http://localhost:8082 - Domain Agent UI")
"""
    
    return workflow_tests


if __name__ == "__main__":
    print("🎮 Setting up ADK Playground for Local Testing")
    print("==============================================")
    
    config = setup_local_adk_playground()
    startup_script = create_playground_startup_script()
    stop_script = create_playground_stop_script()
    a2a_test = create_local_a2a_test()
    workflow_tests = create_playground_workflow_tests()
    
    print(f"✅ ADK Playground Configuration Created!")
    print(f"📊 Agents to run: {len(config['agents'])}")
    print(f"🔗 A2A Communication: Enabled locally")
    print(f"🎮 Playground UI: Available for all agents")
    
    print(f"\\n🚀 To start playground:")
    print(f"   ./local_playground/start_playground.sh")
    
    print(f"\\n🧪 To test A2A communication:")
    print(f"   python local_playground/test_a2a_local.py")
    
    print(f"\\n🌐 Agent UIs will be available at:")
    for agent_type, config_data in config['agents'].items():
        port = config_data['local_port']
        print(f"   • {agent_type}: http://localhost:{port}")
