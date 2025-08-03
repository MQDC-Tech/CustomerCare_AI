#!/bin/bash
set -e

echo "🎮 Starting ADK Playground for Multi-Agent System"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Load environment variables from .env file
if [ -f ".env" ]; then
    echo "📋 Loading environment variables from .env..."
    set -a  # automatically export all variables
    source .env
    set +a  # stop automatically exporting
else
    echo "⚠️  No .env file found, using default settings"
fi

# Set environment variables for local development
export ADK_PLAYGROUND_MODE=true
export ADK_DEBUG=true
export A2A_LOCAL_DISCOVERY=true
export PYTHONPATH=$(pwd)

# Create logs directory
mkdir -p logs/playground

echo "🚀 Starting ADK Web UI with all agents..."

# Start ADK Web UI with all agents (in background)
echo "🌐 Starting ADK Web Server..."
nohup adk web agents/ \
    --host 127.0.0.1 \
    --port 8080 \
    --reload \
    --reload_agents \
    --verbose \
    --session_service_uri sqlite:///playground_sessions.db \
    > logs/playground/adk_server.log 2>&1 &

WEB_PID=$!
echo $WEB_PID > logs/playground/adk_server.pid

# Wait for web server to start
echo "⏳ Waiting for ADK server to start..."
sleep 8

# Check if server is running
if lsof -i :8080 > /dev/null 2>&1; then
    echo ""
    echo "✅ ADK Playground Started Successfully!"
    echo "======================================"
    echo ""
    echo "🌐 ADK Web UI Available:"
    echo "   • All Agents: http://localhost:8080"
    echo "   • Interactive chat with all agents"
    echo "   • Live agent reload enabled"
    echo ""
    echo "🤖 Available Agents:"
    echo "   • Core Agents: coordinator, llm_agent, memory_agent, notifications"
    echo "   • Context Agent: User personalization and session management"
    echo "   • Domain Agent: Real estate CRM and lead management"
    echo ""
    echo "🧪 Test Commands:"
    echo "   • Test A2A communication: python local_playground/test_a2a_local.py"
    echo "   • Run agent workflows: python local_playground/test_workflows.py"
    echo ""
    echo "⏹️  To stop playground: ./local_playground/stop_playground.sh"
    echo ""
    echo "📊 Server running in background (PID: $WEB_PID)"
    echo "📝 Logs available at: logs/playground/adk_server.log"
    echo ""
    echo "💡 To monitor logs: tail -f logs/playground/adk_server.log"
else
    echo "❌ Failed to start ADK server. Check logs/playground/adk_server.log for details."
    exit 1
fi
