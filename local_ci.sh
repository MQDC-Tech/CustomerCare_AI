#!/bin/bash

# 🔍 Local CI Script for Google ADK Multi-Agent System
# Engineering best practices: Unit tests, code quality, and core functionality validation
# Excludes documentation checks, file structure validation, and E2E tests

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}🚀 Local CI Pipeline - Engineering Best Practices${NC}"
echo "============================================="

# Check if virtual environment exists and activate it
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run: python -m venv venv${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Verify core dependencies only
echo -e "${YELLOW}🔍 Checking core dependencies...${NC}"
if ! python -c "import google.adk" 2>/dev/null; then
    echo -e "${RED}❌ Google ADK not installed. Please run: pip install -r requirements.txt${NC}"
    exit 1
fi

# 1. Code Quality Checks
echo -e "${BLUE}1️⃣ Code Quality & Linting${NC}"
echo "=========================="

# Check Python syntax
echo -e "${YELLOW}🐍 Checking Python syntax...${NC}"
find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" | xargs python -m py_compile
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Python syntax check passed${NC}"
else
    echo -e "${RED}❌ Python syntax errors found${NC}"
    exit 1
fi

# Install code quality tools if needed
echo -e "${YELLOW}📦 Ensuring code quality tools...${NC}"
for tool in flake8 black isort pytest; do
    if ! python -c "import $tool" 2>/dev/null; then
        echo -e "${YELLOW}  Installing $tool...${NC}"
        pip install $tool > /dev/null 2>&1
    fi
done

# Run flake8 linting
echo -e "${YELLOW}🔧 Running flake8 linting...${NC}"
FLAKE8_OUTPUT=$(flake8 . --exclude=venv,.git,__pycache__ --max-line-length=88 --ignore=E203,W503 --count 2>/dev/null || echo "")
if [ -n "$FLAKE8_OUTPUT" ]; then
    FLAKE8_COUNT=$(echo "$FLAKE8_OUTPUT" | tail -1)
    if [ "$FLAKE8_COUNT" != "0" ] && [ -n "$FLAKE8_COUNT" ]; then
        echo -e "${RED}❌ Flake8 found $FLAKE8_COUNT issues${NC}"
        echo "$FLAKE8_OUTPUT" | head -10
        exit 1
    else
        echo -e "${GREEN}✅ Flake8 checks passed${NC}"
    fi
else
    echo -e "${GREEN}✅ Flake8 checks passed${NC}"
fi

# Check code formatting with black
echo -e "${YELLOW}🎨 Checking code formatting...${NC}"
if ! black --check --exclude='venv|.git' . > /dev/null 2>&1; then
    echo -e "${RED}❌ Code formatting issues found${NC}"
    echo -e "${YELLOW}💡 Run 'black .' to auto-format${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Code formatting is consistent${NC}"
fi

# Check import sorting
echo -e "${YELLOW}📋 Checking import sorting...${NC}"
if ! isort --check-only --skip=venv --skip=.git . > /dev/null 2>&1; then
    echo -e "${RED}❌ Import sorting issues found${NC}"
    echo -e "${YELLOW}💡 Run 'isort .' to auto-sort imports${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Import sorting is correct${NC}"
fi

# 2. Unit Tests
echo -e "${BLUE}2️⃣ Unit Tests${NC}"
echo "=============="

# Run unit tests with pytest
echo -e "${YELLOW}🧪 Running unit tests...${NC}"
if [ -d "tests" ]; then
    if ! pytest tests/ -v --tb=short > /dev/null 2>&1; then
        echo -e "${RED}❌ Unit tests failed${NC}"
        pytest tests/ -v --tb=short
        exit 1
    else
        echo -e "${GREEN}✅ All unit tests passed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No tests directory found, skipping unit tests${NC}"
fi

# 3. Core Module Import Validation
echo -e "${BLUE}3️⃣ Core Module Validation${NC}"
echo "=========================="

# Basic import validation for core modules
echo -e "${YELLOW}🔍 Validating core imports...${NC}"
python -c "
import sys
sys.path.append('.')

# Test core agent imports
try:
    from agents.core_agent.agent import root_agent
    from agents.context_agent.agent import root_agent
    from agents.domain_realestate.agent import root_agent
    print('✅ All agent modules import successfully')
except Exception as e:
    print(f'❌ Agent import failed: {e}')
    sys.exit(1)

# Test ADK imports
try:
    from google.adk.a2a.utils.agent_to_a2a import to_a2a
    from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
    print('✅ ADK imports successful')
except Exception as e:
    print(f'❌ ADK import failed: {e}')
    sys.exit(1)
"

# Final Summary
echo ""
echo -e "${BLUE}🎉 CI Pipeline Complete${NC}"
echo "====================="
echo -e "${GREEN}✅ All checks passed! Code is ready for commit.${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Commit: git add . && git commit -m 'Your message'"
echo "2. Test: ./local_playground/start_a2a_agents.sh"
echo "3. Deploy: ./deploy.sh"
