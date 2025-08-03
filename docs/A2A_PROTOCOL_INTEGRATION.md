# Agent2Agent (A2A) Protocol Integration Guide

## 🤖 Overview

Our multi-agent system is built with native **Agent2Agent (A2A) protocol** support through the Google ADK framework. All three agent tiers communicate seamlessly using A2A protocol for distributed, scalable agent interactions.

## 🏗️ A2A Architecture

### **Three-Tier A2A Communication**

```
┌─────────────────┐    A2A     ┌─────────────────┐    A2A     ┌─────────────────┐
│   Domain Agent  │ ◄─────────► │  Context Agent  │ ◄─────────► │   Core Agents   │
│                 │             │                 │             │                 │
│ • Real Estate   │             │ • User Profiles │             │ • LLM Agent     │
│ • CRM Integration│             │ • Personalization│             │ • Memory Agent  │
│ • Lead Management│             │ • Session Mgmt  │             │ • Notifications │
│                 │             │                 │             │ • Coordinator   │
└─────────────────┘             └─────────────────┘             └─────────────────┘
```

## 🔗 A2A Implementation in Our Agents

### **1. Domain Agent (Real Estate)**
```python
# agents/domain_realestate/agent.py
agent = Agent(
    name="domain_realestate",
    tools=[
        # Domain-specific tools
        FunctionTool(create_lead),
        FunctionTool(search_properties),
        
        # A2A Communication Tools
        AgentTool("llm_agent"),      # A2A → Core LLM processing
        AgentTool("memory_agent"),   # A2A → Conversation memory
        AgentTool("context_agent"),  # A2A → User personalization
        AgentTool("notifications")   # A2A → Alert system
    ]
)
```

### **2. Context Agent**
```python
# agents/context_agent/agent.py
agent = Agent(
    name="context_agent",
    tools=[
        FunctionTool(fetch_user_profile),
        FunctionTool(personalize_response),
        # Can communicate back to domain agents via A2A
    ]
)
```

### **3. Core Agents**
```python
# agents/core_agent/coordinator/agent.py
agent = Agent(
    name="coordinator",
    tools=[
        FunctionTool(orchestrate_workflow),
        AgentTool("llm_agent"),     # A2A → LLM processing
        AgentTool("memory_agent"),  # A2A → Memory management
        AgentTool("notifications")  # A2A → Notification system
    ]
)
```

## 🚀 A2A Communication Patterns

### **Pattern 1: Request-Response**
```python
# Domain Agent requests user profile from Context Agent
user_profile = await AgentTool("context_agent").call(
    "fetch_user_profile", 
    {"user_id": "user_123"}
)
```

### **Pattern 2: Workflow Orchestration**
```python
# Coordinator orchestrates multi-agent workflow
workflow_result = await AgentTool("coordinator").call(
    "orchestrate_workflow",
    {
        "task": "process_lead",
        "agents": ["context_agent", "memory_agent", "notifications"]
    }
)
```

### **Pattern 3: Event Broadcasting**
```python
# Domain Agent broadcasts lead creation to multiple agents
await AgentTool("memory_agent").call("store_memory", lead_data)
await AgentTool("notifications").call("send_alert", alert_data)
await AgentTool("context_agent").call("update_user_context", context_data)
```

## 📋 A2A Message Flow Examples

### **Customer Inquiry Processing**

1. **Domain Agent** receives customer inquiry
2. **A2A Call**: Domain → Context Agent (get user profile)
3. **A2A Call**: Domain → Memory Agent (store conversation)
4. **A2A Call**: Domain → LLM Agent (generate response)
5. **A2A Call**: Domain → Notifications (send follow-up)

```json
{
  "a2a_workflow": [
    {
      "step": 1,
      "from": "domain_realestate",
      "to": "context_agent",
      "method": "fetch_user_profile",
      "params": {"user_id": "user_123"}
    },
    {
      "step": 2,
      "from": "context_agent",
      "to": "domain_realestate", 
      "method": "profile_response",
      "result": {"preferences": {"style": "professional"}}
    },
    {
      "step": 3,
      "from": "domain_realestate",
      "to": "memory_agent",
      "method": "store_memory",
      "params": {"session_id": "session_123", "content": "inquiry"}
    }
  ]
}
```

## 🛠️ A2A Configuration

### **Manifest Configuration**
```yaml
# manifests/domain_realestate.manifest.yaml
agents:
  - name: domain_realestate
    entrypoint: agents/domain_realestate/agent.py
    a2a_enabled: true
    communication_targets:
      - context_agent
      - llm_agent
      - memory_agent
      - notifications
```

### **Environment Variables**
```bash
# .env
A2A_PROTOCOL_ENABLED=true
A2A_DISCOVERY_MODE=auto
A2A_TIMEOUT_SECONDS=30
```

## 🔍 A2A Monitoring & Debugging

### **A2A Communication Logs**
```python
# Enable A2A logging
import logging
logging.getLogger('adk.a2a').setLevel(logging.DEBUG)

# A2A call tracing
@trace_a2a_calls
def process_customer_request(request):
    # All AgentTool calls will be traced
    profile = AgentTool("context_agent").call("fetch_profile", user_id)
    memory = AgentTool("memory_agent").call("get_history", session_id)
```

### **A2A Metrics**
- **Communication Latency**: Time for A2A request-response
- **Success Rate**: Percentage of successful A2A calls
- **Agent Availability**: Real-time agent status
- **Message Throughput**: A2A messages per second

## 🚀 Deployment with A2A

### **Local Development**
```bash
# Run with A2A protocol enabled
adk run --manifest manifests/domain_realestate.manifest.yaml --a2a-enabled
```

### **Google Cloud Vertex Agent Engine**
```bash
# Deploy with A2A support
gcloud vertex-ai agents deploy \
  --agent-bundle=agent_bundle.zip \
  --enable-a2a-protocol \
  --region=us-central1
```

## 🔧 A2A Best Practices

### **1. Async Communication**
```python
# Use async for non-blocking A2A calls
async def process_lead_async(lead_data):
    profile_task = AgentTool("context_agent").call_async("fetch_profile")
    memory_task = AgentTool("memory_agent").call_async("store_lead")
    
    profile, memory_result = await asyncio.gather(profile_task, memory_task)
```

### **2. Error Handling**
```python
# Handle A2A communication failures
try:
    result = await AgentTool("context_agent").call("fetch_profile", user_id)
except A2ATimeoutError:
    # Fallback to default profile
    result = get_default_profile(user_id)
except A2AAgentUnavailableError:
    # Queue request for later processing
    queue_a2a_request("context_agent", "fetch_profile", user_id)
```

### **3. Circuit Breaker Pattern**
```python
# Prevent cascade failures in A2A communication
@circuit_breaker(failure_threshold=5, recovery_timeout=60)
def call_agent_with_circuit_breaker(agent_name, method, params):
    return AgentTool(agent_name).call(method, params)
```

## ✅ A2A Protocol Benefits

1. **Scalability**: Agents can be distributed across multiple instances
2. **Resilience**: Fault-tolerant communication with retry mechanisms
3. **Modularity**: Loose coupling between agent components
4. **Observability**: Built-in tracing and monitoring
5. **Security**: Encrypted agent-to-agent communication
6. **Load Balancing**: Automatic routing to available agent instances

## 🎯 Testing A2A Communication

```bash
# Run A2A communication tests
pytest tests/test_a2a_communication.py -v

# Test specific A2A workflow
python examples/a2a_communication_demo.py

# Load test A2A protocol
python tests/load_test_a2a.py --agents=10 --requests=1000
```

---

**Our multi-agent system is fully A2A-enabled and ready for production deployment with distributed agent communication!** 🚀
