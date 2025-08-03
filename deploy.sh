#!/bin/bash

# 🚀 ADK Multi-Agent System Deployment Script
# Automates deployment to Google Vertex Agent Engine

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-""}
REGION=${GOOGLE_CLOUD_LOCATION:-"us-central1"}
SERVICE_ACCOUNT_NAME="adk-multi-agent-sa"

echo -e "${BLUE}🚀 ADK Multi-Agent System Deployment${NC}"
echo "======================================"

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}📋 Checking prerequisites...${NC}"
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ Google Cloud CLI not found. Please install it first.${NC}"
        exit 1
    fi
    
    # Check if project ID is set
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}❌ GOOGLE_CLOUD_PROJECT not set. Please set it in .env or export it.${NC}"
        exit 1
    fi
    
    # Check if authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 &> /dev/null; then
        echo -e "${RED}❌ Not authenticated with Google Cloud. Run 'gcloud auth login' first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Enable required APIs
enable_apis() {
    echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
    
    gcloud services enable aiplatform.googleapis.com --project=$PROJECT_ID
    gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
    gcloud services enable run.googleapis.com --project=$PROJECT_ID
    gcloud services enable artifactregistry.googleapis.com --project=$PROJECT_ID
    
    echo -e "${GREEN}✅ APIs enabled${NC}"
}

# Create service account if it doesn't exist
setup_service_account() {
    echo -e "${YELLOW}👤 Setting up service account...${NC}"
    
    # Check if service account exists
    if gcloud iam service-accounts describe ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com --project=$PROJECT_ID &> /dev/null; then
        echo -e "${GREEN}✅ Service account already exists${NC}"
    else
        # Create service account
        gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
            --description="Service account for ADK multi-agent system" \
            --display-name="ADK Multi-Agent Service Account" \
            --project=$PROJECT_ID
        
        # Grant permissions
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
            --role="roles/aiplatform.user"
        
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
            --role="roles/run.invoker"
        
        echo -e "${GREEN}✅ Service account created and configured${NC}"
    fi
}

# Deploy individual agent
deploy_agent() {
    local agent_name=$1
    local agent_path=$2
    local memory=${3:-"1Gi"}
    local cpu=${4:-"1"}
    
    echo -e "${YELLOW}🚀 Deploying $agent_name...${NC}"
    
    # Navigate to agent directory
    cd $agent_path
    
    # Create Dockerfile if it doesn't exist
    if [ ! -f "Dockerfile" ]; then
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
    fi
    
    # Build and submit to Cloud Build
    gcloud builds submit --tag gcr.io/$PROJECT_ID/$agent_name --project=$PROJECT_ID .
    
    # Deploy to Cloud Run
    gcloud run deploy $agent_name \
        --image gcr.io/$PROJECT_ID/$agent_name \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory $memory \
        --cpu $cpu \
        --service-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com \
        --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$REGION" \
        --project=$PROJECT_ID
    
    # Get service URL
    local service_url=$(gcloud run services describe $agent_name --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
    echo -e "${GREEN}✅ $agent_name deployed: $service_url${NC}"
    
    # Return to root directory
    cd - > /dev/null
    
    echo $service_url
}

# Test deployment
test_deployment() {
    echo -e "${YELLOW}🧪 Testing deployment...${NC}"
    
    # Get service URLs
    local core_url=$(gcloud run services describe core-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID 2>/dev/null || echo "")
    local context_url=$(gcloud run services describe context-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID 2>/dev/null || echo "")
    local domain_url=$(gcloud run services describe domain-realestate-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID 2>/dev/null || echo "")
    
    # Test health endpoints
    if [ ! -z "$core_url" ]; then
        echo "Testing Core Agent: $core_url"
        curl -s -o /dev/null -w "%{http_code}" "$core_url/.well-known/agent-card.json" | grep -q "200" && echo -e "${GREEN}✅ Core Agent healthy${NC}" || echo -e "${RED}❌ Core Agent unhealthy${NC}"
    fi
    
    if [ ! -z "$context_url" ]; then
        echo "Testing Context Agent: $context_url"
        curl -s -o /dev/null -w "%{http_code}" "$context_url/.well-known/agent-card.json" | grep -q "200" && echo -e "${GREEN}✅ Context Agent healthy${NC}" || echo -e "${RED}❌ Context Agent unhealthy${NC}"
    fi
    
    if [ ! -z "$domain_url" ]; then
        echo "Testing Domain Agent: $domain_url"
        curl -s -o /dev/null -w "%{http_code}" "$domain_url/.well-known/agent-card.json" | grep -q "200" && echo -e "${GREEN}✅ Domain Agent healthy${NC}" || echo -e "${RED}❌ Domain Agent unhealthy${NC}"
    fi
}

# Main deployment flow
main() {
    echo -e "${BLUE}Starting deployment to Google Cloud Project: $PROJECT_ID${NC}"
    
    check_prerequisites
    enable_apis
    setup_service_account
    
    # Deploy agents
    echo -e "${YELLOW}🚀 Deploying agents...${NC}"
    
    # Deploy Core Agent (Coordinator)
    CORE_URL=$(deploy_agent "core-agent" "agents/core_agent/coordinator" "2Gi" "2")
    
    # Deploy Context Agent
    CONTEXT_URL=$(deploy_agent "context-agent" "agents/context_agent" "1Gi" "1")
    
    # Deploy Domain Real Estate Agent
    DOMAIN_URL=$(deploy_agent "domain-realestate-agent" "agents/domain_realestate" "1Gi" "1")
    
    # Test deployment
    test_deployment
    
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo ""
    echo "📋 Service URLs:"
    echo "  Core Agent:              $CORE_URL"
    echo "  Context Agent:           $CONTEXT_URL"
    echo "  Domain Real Estate:      $DOMAIN_URL"
    echo ""
    echo -e "${YELLOW}📖 Next steps:${NC}"
    echo "1. Update agent registry in Core Agent with production URLs"
    echo "2. Test A2A communication between agents"
    echo "3. Set up monitoring and alerts"
    echo "4. Configure custom domain (optional)"
    echo ""
    echo -e "${BLUE}📚 For detailed instructions, see DEPLOYMENT.md${NC}"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "test")
        test_deployment
        ;;
    "clean")
        echo -e "${YELLOW}🧹 Cleaning up deployment...${NC}"
        gcloud run services delete core-agent --region=$REGION --quiet --project=$PROJECT_ID || true
        gcloud run services delete context-agent --region=$REGION --quiet --project=$PROJECT_ID || true
        gcloud run services delete domain-realestate-agent --region=$REGION --quiet --project=$PROJECT_ID || true
        echo -e "${GREEN}✅ Cleanup completed${NC}"
        ;;
    *)
        echo "Usage: $0 [deploy|test|clean]"
        echo "  deploy: Deploy all agents (default)"
        echo "  test:   Test existing deployment"
        echo "  clean:  Remove all deployed services"
        exit 1
        ;;
esac
