#!/bin/bash

# 🔄 GitHub Actions CI/CD Setup Script
# Automates the setup of CI/CD pipeline for ADK Multi-Agent System

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Setting up CI/CD Pipeline for ADK Multi-Agent System${NC}"
echo "============================================================="

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-""}
SERVICE_ACCOUNT_NAME="github-ci-cd"
KEY_FILE="github-sa-key.json"

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
    
    # Check if GitHub CLI is available (optional)
    if command -v gh &> /dev/null; then
        echo -e "${GREEN}✅ GitHub CLI found - can set secrets automatically${NC}"
        GH_CLI_AVAILABLE=true
    else
        echo -e "${YELLOW}⚠️ GitHub CLI not found - you'll need to set secrets manually${NC}"
        GH_CLI_AVAILABLE=false
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Create service account for GitHub Actions
create_service_account() {
    echo -e "${YELLOW}👤 Creating GitHub Actions service account...${NC}"
    
    # Check if service account exists
    if gcloud iam service-accounts describe ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com --project=$PROJECT_ID &> /dev/null; then
        echo -e "${YELLOW}⚠️ Service account already exists, skipping creation${NC}"
    else
        # Create service account
        gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
            --description="GitHub Actions CI/CD service account" \
            --display-name="GitHub CI/CD" \
            --project=$PROJECT_ID
        
        echo -e "${GREEN}✅ Service account created${NC}"
    fi
    
    # Grant necessary permissions
    echo -e "${YELLOW}🔐 Granting permissions...${NC}"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/run.admin" \
        --quiet
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/storage.admin" \
        --quiet
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/cloudbuild.builds.builder" \
        --quiet
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/artifactregistry.admin" \
        --quiet
    
    echo -e "${GREEN}✅ Permissions granted${NC}"
}

# Create and download service account key
create_service_account_key() {
    echo -e "${YELLOW}🔑 Creating service account key...${NC}"
    
    # Remove existing key file if it exists
    if [ -f "$KEY_FILE" ]; then
        rm "$KEY_FILE"
    fi
    
    # Create new key
    gcloud iam service-accounts keys create $KEY_FILE \
        --iam-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com \
        --project=$PROJECT_ID
    
    echo -e "${GREEN}✅ Service account key created: $KEY_FILE${NC}"
}

# Set up GitHub secrets (if GitHub CLI is available)
setup_github_secrets() {
    if [ "$GH_CLI_AVAILABLE" = true ]; then
        echo -e "${YELLOW}🔐 Setting up GitHub secrets...${NC}"
        
        # Check if we're in a git repository
        if ! git rev-parse --git-dir > /dev/null 2>&1; then
            echo -e "${RED}❌ Not in a git repository. Please run this from your project root.${NC}"
            return 1
        fi
        
        # Set required secrets
        echo -e "${BLUE}Setting GOOGLE_CLOUD_PROJECT...${NC}"
        echo "$PROJECT_ID" | gh secret set GOOGLE_CLOUD_PROJECT
        
        echo -e "${BLUE}Setting GOOGLE_CLOUD_SA_KEY...${NC}"
        cat "$KEY_FILE" | gh secret set GOOGLE_CLOUD_SA_KEY
        
        # Prompt for API keys
        echo -e "${YELLOW}📝 Please enter your Gemini API keys:${NC}"
        
        echo -n "Staging Gemini API Key: "
        read -s GEMINI_API_KEY_STAGING
        echo
        echo "$GEMINI_API_KEY_STAGING" | gh secret set GEMINI_API_KEY
        
        echo -n "Production Gemini API Key (or press Enter to use same as staging): "
        read -s GEMINI_API_KEY_PROD
        echo
        
        if [ -z "$GEMINI_API_KEY_PROD" ]; then
            GEMINI_API_KEY_PROD="$GEMINI_API_KEY_STAGING"
        fi
        echo "$GEMINI_API_KEY_PROD" | gh secret set GEMINI_API_KEY_PROD
        
        echo -e "${GREEN}✅ GitHub secrets configured${NC}"
    else
        echo -e "${YELLOW}⚠️ GitHub CLI not available. Please set secrets manually.${NC}"
        manual_secrets_instructions
    fi
}

# Display manual secrets setup instructions
manual_secrets_instructions() {
    echo -e "${BLUE}📝 Manual GitHub Secrets Setup Instructions:${NC}"
    echo ""
    echo "1. Go to your GitHub repository"
    echo "2. Navigate to Settings > Secrets and variables > Actions"
    echo "3. Add the following secrets:"
    echo ""
    echo -e "${YELLOW}Required Secrets:${NC}"
    echo "   GOOGLE_CLOUD_PROJECT: $PROJECT_ID"
    echo "   GOOGLE_CLOUD_SA_KEY: <paste contents of $KEY_FILE>"
    echo "   GEMINI_API_KEY: <your staging Gemini API key>"
    echo "   GEMINI_API_KEY_PROD: <your production Gemini API key>"
    echo ""
    echo -e "${BLUE}Service account key content:${NC}"
    echo "----------------------------------------"
    cat "$KEY_FILE"
    echo "----------------------------------------"
}

# Enable required APIs
enable_apis() {
    echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
    
    gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
    gcloud services enable run.googleapis.com --project=$PROJECT_ID
    gcloud services enable artifactregistry.googleapis.com --project=$PROJECT_ID
    gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID
    
    echo -e "${GREEN}✅ APIs enabled${NC}"
}

# Create environments in GitHub (if GitHub CLI is available)
create_github_environments() {
    if [ "$GH_CLI_AVAILABLE" = true ]; then
        echo -e "${YELLOW}🌍 Creating GitHub environments...${NC}"
        
        # Note: Environment creation via CLI requires GitHub Enterprise
        # For now, we'll just provide instructions
        echo -e "${BLUE}📝 GitHub Environments Setup:${NC}"
        echo "1. Go to your GitHub repository"
        echo "2. Navigate to Settings > Environments"
        echo "3. Create two environments:"
        echo "   - staging (no protection rules)"
        echo "   - production (require reviewers for deployment)"
    fi
}

# Test the setup
test_setup() {
    echo -e "${YELLOW}🧪 Testing CI/CD setup...${NC}"
    
    # Check if workflow file exists
    if [ -f ".github/workflows/ci-cd.yml" ]; then
        echo -e "${GREEN}✅ CI/CD workflow file exists${NC}"
    else
        echo -e "${RED}❌ CI/CD workflow file missing${NC}"
        return 1
    fi
    
    # Check if configuration files exist
    local config_files=("pytest.ini" ".flake8" "pyproject.toml")
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}✅ $file exists${NC}"
        else
            echo -e "${RED}❌ $file missing${NC}"
        fi
    done
    
    # Test service account permissions
    echo -e "${BLUE}Testing service account permissions...${NC}"
    gcloud projects get-iam-policy $PROJECT_ID \
        --flatten="bindings[].members" \
        --filter="bindings.members:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --format="table(bindings.role)" | grep -q "roles/run.admin" && \
        echo -e "${GREEN}✅ Cloud Run admin permissions verified${NC}" || \
        echo -e "${RED}❌ Cloud Run admin permissions missing${NC}"
}

# Cleanup function
cleanup() {
    echo -e "${YELLOW}🧹 Cleaning up temporary files...${NC}"
    
    # Optionally remove the service account key file
    read -p "Remove service account key file ($KEY_FILE)? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "$KEY_FILE"
        echo -e "${GREEN}✅ Key file removed${NC}"
    else
        echo -e "${YELLOW}⚠️ Key file kept: $KEY_FILE${NC}"
        echo -e "${RED}🔒 Remember to secure this file and never commit it to git!${NC}"
    fi
}

# Main setup flow
main() {
    echo -e "${BLUE}Starting CI/CD setup for Google Cloud Project: $PROJECT_ID${NC}"
    
    check_prerequisites
    enable_apis
    create_service_account
    create_service_account_key
    setup_github_secrets
    create_github_environments
    test_setup
    
    echo -e "${GREEN}🎉 CI/CD setup completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📋 Next steps:${NC}"
    echo "1. Push your code to trigger the first CI/CD run"
    echo "2. Check GitHub Actions tab for pipeline status"
    echo "3. Review deployment in Google Cloud Console"
    echo "4. Set up monitoring and alerts"
    echo ""
    echo -e "${YELLOW}📖 For detailed information, see docs/CI-CD.md${NC}"
    
    cleanup
}

# Handle script arguments
case "${1:-setup}" in
    "setup")
        main
        ;;
    "test")
        test_setup
        ;;
    "clean")
        echo -e "${YELLOW}🧹 Cleaning up CI/CD resources...${NC}"
        gcloud iam service-accounts delete ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com --project=$PROJECT_ID --quiet || true
        rm -f "$KEY_FILE"
        echo -e "${GREEN}✅ Cleanup completed${NC}"
        ;;
    *)
        echo "Usage: $0 [setup|test|clean]"
        echo "  setup: Set up CI/CD pipeline (default)"
        echo "  test:  Test existing setup"
        echo "  clean: Remove CI/CD resources"
        exit 1
        ;;
esac
