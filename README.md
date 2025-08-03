# 🏢 Google ADK Multi-Agent B2B Customer Care Platform

> **A production-grade ADK-based multi-agent system with real Agent-to-Agent (A2A) Protocol communication for B2B customer care, featuring specialized real estate domain capabilities.**

## ✨ Key Features

- 🤖 **Real A2A Protocol Communication**: Native Agent-to-Agent messaging using Google's A2A SDK
- 🏗️ **Multi-Agent Architecture**: Core, Context, and Domain-specific agents working together
- 🏠 **Real Estate Specialization**: Property search, lead management, and CRM integration
- 🔄 **Live Testing Environment**: ADK playground and A2A test scripts
- 📊 **Detailed Response Handling**: Specific property listings, pricing, and agent contact information
- 🚀 **Production Ready**: Comprehensive deployment scripts and cloud integration

## 🏗️ Architecture Overview

### Three-Tier Agent System:

- **🧠 Core Agent**: Orchestration, memory management, notifications, and workflow coordination
- **👤 Context Agent**: User personalization, session management, and profile handling  
- **🏠 Domain Real Estate Agent**: Property search, lead generation, CRM integration, and client management

## 📂 Project Structure

```
├── agents/
│   ├── core_agent/
│   │   ├── coordinator/agent.py      # Workflow orchestration
│   │   ├── llm_agent/agent.py        # Language model tasks
│   │   ├── memory_agent/agent.py     # Conversation memory
│   │   └── notifications/agent.py    # Alerts & communication
│   │
│   ├── domain_realestate/
│   │   ├── agent.py                  # Real estate domain agent
│   │   └── tools/
│   │       ├── crm_connector.py      # CRM integration
│   │       └── lead_router.py        # Lead qualification & routing
│   │
│   └── context_agent/
│       ├── agent.py                  # Context management
│       └── profile_manager.py        # User profiles
│
├── manifests/
│   ├── core_agent.manifest.yaml     # Core agents manifest
│   ├── domain_realestate.manifest.yaml  # Domain agent manifest
│   └── context_agent.manifest.yaml  # Context agent manifest
│
├── tests/                            # Test suite
├── utils/                            # Shared utilities
├── requirements.txt                  # Dependencies
├── main.py                          # Entry point
└── README.md                        # This file
```

## 🚀 Quick Start & Testing Guide

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd CustomerCare_AI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Create environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required environment variables:**
```bash
# Google AI API Key (required for all agents)
GEMINI_API_KEY=your_google_ai_api_key_here

# Optional: Google Cloud credentials for production deployment
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
```

### 3. Testing Options

#### 🎮 Option A: ADK Playground (Interactive Web UI)

**Start the playground:**
```bash
./local_playground/start_playground.sh
```

**Access the web interface:**
- Open browser: `http://localhost:8080`
- Select `core_agent` from dropdown
- Test with sample queries:

```
I'm interested in buying a 3-bedroom house in downtown area under $500k. Please help me find properties and create a lead for this request.
```

**Stop the playground:**
```bash
./local_playground/stop_playground.sh
```

#### 🤖 Option B: A2A Agent Testing (Real Inter-Agent Communication)

**Start A2A agents:**
```bash
./local_playground/start_a2a_agents.sh
```

**Run comprehensive A2A tests:**
```bash
source venv/bin/activate
python local_playground/test_a2a_agents.py
```

**Monitor agent logs:**
```bash
# Core Agent logs
tail -f logs/core_agent_a2a.log

# Domain Real Estate Agent logs  
tail -f logs/domain_realestate_a2a.log

# Context Agent logs
tail -f logs/context_agent_a2a.log
```

**Stop A2A agents:**
```bash
./local_playground/stop_a2a_agents.sh
```

#### 🧪 Option C: Individual Agent Testing

**Test single agents:**
```bash
# Test Core Agent
adk run agents/core_agent/coordinator/ --reload

# Test Domain Real Estate Agent
adk run agents/domain_realestate/ --reload

# Test Context Agent
adk run agents/context_agent/ --reload
```

## 🔍 What to Expect When Testing

### ADK Playground Results

When you test in the ADK playground with a property query, you should see:

**Sample Query:**
```
I'm interested in buying a 3-bedroom house in downtown area under $500k. Please help me find properties and create a lead for this request.
```

**Expected Response:**
- 🏡 **3 specific property listings** with addresses, prices, square footage
- 📋 **Lead creation confirmation** with unique lead ID (LEAD-2025-001)
- 📞 **Agent contact information** (Sarah Johnson, phone, email)
- ✅ **Request processing status** with context ID and timestamp

### A2A Communication Validation

The A2A test script validates:
- ✅ **Agent discovery** via `/.well-known/agent-card.json`
- ✅ **Message routing** using JSON-RPC 2.0 protocol
- ✅ **Task creation and completion** with proper status updates
- ✅ **Response parsing** from Task and Message objects
- ✅ **Multi-agent workflows** with real inter-agent communication

**Test Output Example:**
```
🎯 Testing A2A Communication...
✅ core_agent responded successfully
✅ context_agent responded successfully  
✅ domain_realestate responded successfully
🎉 A2A Testing Complete!
```

## 🤖 Agent Capabilities

### 🧠 Core Agent (Coordinator)
- **Workflow Orchestration**: Routes requests to appropriate domain agents
- **A2A Communication**: Real HTTP calls using A2A Protocol (not simulated)
- **Response Aggregation**: Combines responses from multiple agents
- **Memory Integration**: Stores conversation context and user preferences

### 👤 Context Agent
- **User Profiles**: Manages personalization data and preferences
- **Session Management**: Maintains context across conversations
- **Preference Learning**: Adapts responses based on user interaction history

### 🏠 Domain Real Estate Agent
- **Property Search**: Returns specific listings with addresses, prices, features
- **Lead Management**: Creates leads with unique IDs and assigns to agents
- **CRM Integration**: Manages client data and interaction tracking
- **Agent Assignment**: Routes qualified leads to appropriate real estate agents

## 🔧 A2A Protocol Implementation

### Technical Details

**Transport**: JSON-RPC 2.0 over HTTP(S)
**Discovery**: Agent Cards at `/.well-known/agent-card.json`
**Messaging**: `message/send` method with proper MessageSendParams
**Task Management**: Full lifecycle with states (working, completed, failed)

### Agent Endpoints

```
Core Agent:              http://localhost:10000
Context Agent:           http://localhost:10001
Domain Real Estate:      http://localhost:10002
```

### Message Flow

1. **User Query** → Core Agent (ADK Playground)
2. **Route Request** → Core Agent calls `route_request()` function
3. **A2A Call** → Core Agent makes HTTP POST to Domain Agent
4. **Processing** → Domain Agent processes and returns detailed response
5. **Response** → Core Agent receives and displays agent response

## 🚨 Troubleshooting

### Common Issues

**❌ "Module not found" errors:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**❌ "GEMINI_API_KEY not found":**
```bash
# Check .env file exists and has correct key
cat .env | grep GEMINI_API_KEY
```

**❌ A2A agents not responding:**
```bash
# Check if agents are running
curl http://localhost:10000/.well-known/agent-card.json
curl http://localhost:10001/.well-known/agent-card.json
curl http://localhost:10002/.well-known/agent-card.json
```

**❌ Generic responses instead of detailed property info:**
- This indicates the Core Agent's LLM is summarizing responses
- Check the Response panel in ADK playground for full details
- The A2A communication is working; it's a presentation layer issue

### Log Locations

```
logs/core_agent_a2a.log          # Core Agent A2A server logs
logs/domain_realestate_a2a.log   # Domain Agent processing logs
logs/context_agent_a2a.log       # Context Agent logs
logs/playground/adk_server.log   # ADK Playground logs
```

### Debug Commands

```bash
# Test direct A2A communication
curl -X POST http://localhost:10002/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "messageId": "test-123",
        "role": "user",
        "parts": [{"type": "text", "text": "Find 3-bedroom houses under $500k"}]
      },
      "configuration": {"blocking": true}
    },
    "id": "test-req"
  }'
```
- Smart routing to appropriate agents
- Priority-based lead management
- Performance analytics

## 🔧 Development

### Adding New Domain Agents

1. Create agent directory: `agents/domain_[name]/`
2. Implement `agent.py` with domain-specific tools
3. Create manifest: `manifests/domain_[name].manifest.yaml`
4. Add tests: `tests/test_[name].py`

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_domain.py -v

# Run with coverage
pytest tests/ --cov=agents --cov-report=html
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 agents/ utils/ tests/
```

## ☁️ Deployment

### 🚀 Quick Deployment

**Automated Deployment Script:**
```bash
# One-command deployment to Google Vertex Agent Engine
./deploy.sh

# Test deployment
./deploy.sh test

# Clean up deployment
./deploy.sh clean
```

**Manual Deployment:**
```bash
# 1. Set up Google Cloud
export GOOGLE_CLOUD_PROJECT=your_project_id
gcloud auth login

# 2. Enable APIs
gcloud services enable aiplatform.googleapis.com cloudbuild.googleapis.com run.googleapis.com

# 3. Deploy agents
cd agents/core_agent/coordinator
gcloud run deploy core-agent --source . --region us-central1

cd ../../context_agent  
gcloud run deploy context-agent --source . --region us-central1

cd ../domain_realestate
gcloud run deploy domain-realestate-agent --source . --region us-central1
```

### 📚 Comprehensive Deployment Guide

**For detailed deployment instructions, architecture, security, monitoring, and troubleshooting:**

👉 **[See DEPLOYMENT.md](./DEPLOYMENT.md)** for the complete deployment guide

The deployment guide includes:
- 🏗️ **Architecture Overview** - Multi-agent Cloud Run deployment strategy
- 🔧 **Step-by-Step Instructions** - Detailed deployment workflow
- 🔒 **Security Configuration** - IAM, service accounts, VPC setup
- 📊 **Monitoring & Observability** - Logging, dashboards, alerts
- 🚨 **Troubleshooting** - Common issues and solutions
- 💰 **Cost Optimization** - Resource management and scaling

### 🧪 Deployment Validation

**Quick Health Check:**
```bash
# Test agent discovery endpoints
curl https://your-core-agent-url/.well-known/agent-card.json
curl https://your-context-agent-url/.well-known/agent-card.json
curl https://your-domain-agent-url/.well-known/agent-card.json

# Test A2A communication
curl -X POST https://your-domain-agent-url/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"message/send","params":{"message":{"messageId":"test","role":"user","parts":[{"type":"text","text":"Find properties under $500k"}]},"configuration":{"blocking":true}},"id":"test"}'
```

**Expected Production URLs:**
```
Core Agent:              https://core-agent-xxx-uc.a.run.app
Context Agent:           https://context-agent-xxx-uc.a.run.app
Domain Real Estate:      https://domain-realestate-agent-xxx-uc.a.run.app
```

### Local Development Server

```bash
# Run with hot reload
adk run --manifest manifests/domain_realestate.manifest.yaml --reload

# Run with debug logging
adk run --manifest manifests/domain_realestate.manifest.yaml --log-level debug
```

## 🔌 Integration Examples

### CRM Lead Creation

```python
from agents.domain_realestate.tools.crm_connector import create_lead

# Create new lead
lead = create_lead(
    name="John Doe",
    email="john@example.com",
    phone="555-1234",
    property_interest="house",
    budget_range="400k-500k",
    notes="First-time buyer, prequalified"
)
```

### User Personalization

```python
from agents.context_agent.profile_manager import fetch_user_profile

# Get user preferences
profile = fetch_user_profile("user_123")
preferences = profile["profile"]["preferences"]

# Personalize response
personalized = personalize_response("user_123", "Here are your property matches")
```

## 📊 Monitoring & Analytics

- **Agent Performance**: Response times, success rates
- **Lead Conversion**: Qualification rates, routing efficiency
- **User Engagement**: Session duration, interaction patterns
- **System Health**: Error rates, resource utilization

## 🛠️ Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure proper Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**API Key Issues**
```bash
# Verify environment variables
python -c "import os; print(os.getenv('GOOGLE_API_KEY'))"
```

**Agent Communication**
- Check manifest file syntax
- Verify agent names match exactly
- Ensure all dependencies are installed

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-agent`
3. Add tests for new functionality
4. Ensure all tests pass: `pytest tests/`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check the troubleshooting section
- Review agent logs and error messages
- Open an issue with detailed reproduction steps

---

**Built with Google Vertex AI ADK** 🚀
