# 🚀 Google Vertex Agent Engine Deployment Guide

> **Complete deployment workflow for the ADK Multi-Agent B2B Customer Care Platform**

## 📋 Prerequisites

### 1. Google Cloud Setup

```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate with Google Cloud
gcloud auth login
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### 2. Enable Required APIs

```bash
# Enable necessary Google Cloud APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable agent-engine.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### 3. Create Service Account

```bash
# Create service account for deployment
gcloud iam service-accounts create adk-multi-agent-sa \
    --description="Service account for ADK multi-agent system" \
    --display-name="ADK Multi-Agent Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:adk-multi-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:adk-multi-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.invoker"

# Create and download service account key
gcloud iam service-accounts keys create ./service-account-key.json \
    --iam-account=adk-multi-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

## 🏗️ Deployment Architecture

### Agent Deployment Strategy

```
┌─────────────────────────────────────────────────────────┐
│                Google Cloud Platform                    │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────┐ │
│  │   Core Agent    │  │ Context Agent   │  │  Domain   │ │
│  │  (Coordinator)  │  │ (Personalization│  │ Real Estate│ │
│  │                 │  │ & Sessions)     │  │   Agent   │ │
│  │ Cloud Run       │  │ Cloud Run       │  │ Cloud Run │ │
│  │ + Vertex AI     │  │ + Vertex AI     │  │ + Vertex AI│ │
│  └─────────────────┘  └─────────────────┘  └───────────┘ │
│           │                     │                  │     │
│           └─────────────────────┼──────────────────┘     │
│                                 │                        │
│  ┌─────────────────────────────────────────────────────┐ │
│  │            A2A Protocol Communication               │ │
│  │         (JSON-RPC 2.0 over HTTPS)                  │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Load Balancer                          │ │
│  │         (Google Cloud Load Balancing)              │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 🎯 Step-by-Step Deployment

### Step 1: Prepare Environment

```bash
# Clone and setup project
git clone <your-repo-url>
cd CustomerCare_AI

# Create production environment file
cp .env.example .env.production

# Edit production environment variables
nano .env.production
```

**Production Environment Variables:**
```bash
# Google AI API Key (Required)
GEMINI_API_KEY=your_production_gemini_api_key

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# Production Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Optional: Production Integrations
FIREBASE_PROJECT_ID=your_firebase_project_id
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/customercare
NEWRELIC_LICENSE_KEY=your_newrelic_license_key
```

### Step 2: Build and Deploy Core Agent

```bash
# Navigate to Core Agent directory
cd agents/core_agent/coordinator

# Create Dockerfile for Core Agent
cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY ../../../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY . .
COPY ../../../.env.production .env

# Expose port
EXPOSE 8080

# Run agent
CMD ["python", "-m", "adk", "run", ".", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/core-agent .

gcloud run deploy core-agent \
    --image gcr.io/YOUR_PROJECT_ID/core-agent \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --env-vars-file ../../../.env.production
```

### Step 3: Deploy Context Agent

```bash
# Navigate to Context Agent directory
cd ../../context_agent

# Create Dockerfile for Context Agent
cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY ../../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY . .
COPY ../../.env.production .env

# Expose port
EXPOSE 8080

# Run agent
CMD ["python", "-m", "adk", "run", ".", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/context-agent .

gcloud run deploy context-agent \
    --image gcr.io/YOUR_PROJECT_ID/context-agent \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --env-vars-file ../../.env.production
```

### Step 4: Deploy Domain Real Estate Agent

```bash
# Navigate to Domain Real Estate Agent directory
cd ../domain_realestate

# Create Dockerfile for Domain Agent
cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY ../../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY . .
COPY ../../.env.production .env

# Expose port
EXPOSE 8080

# Run agent
CMD ["python", "-m", "adk", "run", ".", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/domain-realestate-agent .

gcloud run deploy domain-realestate-agent \
    --image gcr.io/YOUR_PROJECT_ID/domain-realestate-agent \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --env-vars-file ../../.env.production
```

### Step 5: Configure A2A Communication

```bash
# Get deployed service URLs
CORE_AGENT_URL=$(gcloud run services describe core-agent --region=us-central1 --format='value(status.url)')
CONTEXT_AGENT_URL=$(gcloud run services describe context-agent --region=us-central1 --format='value(status.url)')
DOMAIN_AGENT_URL=$(gcloud run services describe domain-realestate-agent --region=us-central1 --format='value(status.url)')

echo "Core Agent URL: $CORE_AGENT_URL"
echo "Context Agent URL: $CONTEXT_AGENT_URL"
echo "Domain Agent URL: $DOMAIN_AGENT_URL"
```

Update the agent registry in your Core Agent coordinator to use production URLs:

```python
# In agents/core_agent/coordinator/agent.py
agent_registry = {
    "domain_realestate": "https://domain-realestate-agent-xxx-uc.a.run.app",
    "context_agent": "https://context-agent-xxx-uc.a.run.app",
    "llm_agent": "https://core-agent-xxx-uc.a.run.app"
}
```

### Step 6: Set Up Load Balancer (Optional)

```bash
# Create load balancer for high availability
gcloud compute url-maps create adk-multi-agent-lb \
    --default-service=core-agent-backend

# Create backend service
gcloud compute backend-services create core-agent-backend \
    --global \
    --load-balancing-scheme=EXTERNAL \
    --protocol=HTTP

# Add Cloud Run services as backends
gcloud compute backend-services add-backend core-agent-backend \
    --global \
    --neg=core-agent-neg \
    --neg-zone=us-central1-a
```

## 🧪 Deployment Validation

### 1. Health Checks

```bash
# Test Core Agent
curl -X GET "$CORE_AGENT_URL/health"

# Test Context Agent
curl -X GET "$CONTEXT_AGENT_URL/health"

# Test Domain Agent
curl -X GET "$DOMAIN_AGENT_URL/health"
```

### 2. A2A Communication Test

```bash
# Test A2A Protocol communication
curl -X POST "$DOMAIN_AGENT_URL/" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "messageId": "prod-test-123",
        "role": "user",
        "parts": [{"type": "text", "text": "Find 3-bedroom houses under $500k in downtown"}]
      },
      "configuration": {"blocking": true}
    },
    "id": "prod-test-req"
  }'
```

### 3. End-to-End Workflow Test

```bash
# Test complete workflow through Core Agent
curl -X POST "$CORE_AGENT_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need help finding a 3-bedroom house in downtown area under $500k",
    "session_id": "test-session-123"
  }'
```

## 📊 Monitoring & Observability

### 1. Set Up Logging

```bash
# Enable Cloud Logging
gcloud logging sinks create adk-multi-agent-sink \
    bigquery.googleapis.com/projects/YOUR_PROJECT_ID/datasets/adk_logs \
    --log-filter='resource.type="cloud_run_revision"'
```

### 2. Set Up Monitoring

```bash
# Create monitoring dashboard
gcloud alpha monitoring dashboards create \
    --config-from-file=monitoring/dashboard-config.yaml
```

### 3. Set Up Alerts

```bash
# Create alerting policy for high error rates
gcloud alpha monitoring policies create \
    --policy-from-file=monitoring/error-rate-alert.yaml
```

## 🔒 Security Configuration

### 1. Enable IAM Authentication

```bash
# Remove public access and enable IAM
gcloud run services update core-agent \
    --region=us-central1 \
    --no-allow-unauthenticated

# Create invoker role for inter-service communication
gcloud run services add-iam-policy-binding core-agent \
    --region=us-central1 \
    --member="serviceAccount:adk-multi-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.invoker"
```

### 2. Set Up VPC Connector (Optional)

```bash
# Create VPC connector for private communication
gcloud compute networks vpc-access connectors create adk-connector \
    --region=us-central1 \
    --subnet=default \
    --subnet-project=YOUR_PROJECT_ID \
    --min-instances=2 \
    --max-instances=10
```

## 🚀 Production Deployment Checklist

- [ ] **Environment Setup**
  - [ ] Google Cloud project configured
  - [ ] APIs enabled
  - [ ] Service account created
  - [ ] Production environment variables set

- [ ] **Agent Deployment**
  - [ ] Core Agent deployed to Cloud Run
  - [ ] Context Agent deployed to Cloud Run
  - [ ] Domain Real Estate Agent deployed to Cloud Run
  - [ ] All agents accessible via HTTPS

- [ ] **A2A Configuration**
  - [ ] Agent registry updated with production URLs
  - [ ] A2A Protocol endpoints tested
  - [ ] Inter-agent communication validated

- [ ] **Security**
  - [ ] IAM authentication configured
  - [ ] Service accounts properly configured
  - [ ] API keys secured in environment variables

- [ ] **Monitoring**
  - [ ] Cloud Logging enabled
  - [ ] Monitoring dashboard created
  - [ ] Alert policies configured

- [ ] **Testing**
  - [ ] Health checks passing
  - [ ] A2A communication working
  - [ ] End-to-end workflows validated

## 🔧 Troubleshooting

### Common Deployment Issues

**❌ "Permission denied" errors:**
```bash
# Check service account permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:adk-multi-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com"
```

**❌ "Service unavailable" errors:**
```bash
# Check Cloud Run logs
gcloud logs read "resource.type=cloud_run_revision" \
    --limit=50 \
    --format="table(timestamp,severity,textPayload)"
```

**❌ A2A communication failures:**
```bash
# Test agent discovery endpoints
curl -X GET "$DOMAIN_AGENT_URL/.well-known/agent-card.json"
```

### Performance Optimization

```bash
# Scale services based on traffic
gcloud run services update core-agent \
    --region=us-central1 \
    --min-instances=1 \
    --max-instances=100 \
    --concurrency=80 \
    --cpu=2 \
    --memory=2Gi
```

## 📈 Cost Optimization

- **Use minimum instances** for development/staging
- **Enable CPU allocation only during requests** for cost savings
- **Set appropriate concurrency limits** to optimize resource usage
- **Monitor usage** with Cloud Billing alerts

---

🎉 **Your ADK Multi-Agent System is now deployed to Google Vertex Agent Engine with full A2A Protocol communication!**
