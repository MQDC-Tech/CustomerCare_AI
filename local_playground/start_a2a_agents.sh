#!/bin/bash

# A2A Multi-Agent Startup Script
# Starts all agents as separate A2A servers for inter-agent communication

set -e

echo "🚀 Starting ADK-native A2A Multi-Agent System..."

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Load environment variables
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env..."
    set -a
    source .env
    set +a
else
    echo "⚠️  Warning: .env file not found. Using default configuration."
fi

# Activate virtual environment
if [ -d "venv" ]; then
    echo "🐍 Activating Python virtual environment..."
    source venv/bin/activate
else
    echo "❌ Error: Virtual environment not found. Please run setup first."
    exit 1
fi

# Create logs directory
mkdir -p logs

# Function to start an agent server
start_agent() {
    local agent_name=$1
    local port=$2
    local log_file="logs/${agent_name}_a2a.log"
    
    echo "🤖 Starting ${agent_name} A2A server on port ${port}..."
    
    # Start the agent server in the background
    nohup python -m agents.${agent_name} --host localhost --port ${port} > ${log_file} 2>&1 &
    local pid=$!
    
    # Save PID for later cleanup
    echo ${pid} > "logs/${agent_name}_a2a.pid"
    
    echo "   ✅ ${agent_name} started (PID: ${pid}, Log: ${log_file})"
    
    # Give the server a moment to start
    sleep 2
}

# Start all A2A agent servers
echo ""
echo "🎯 Starting A2A Agent Servers..."
echo "================================"

# Start Core Agent (Orchestrator) - Port 10000
start_agent "core_agent" 10000

# Start Context Agent - Port 10001  
start_agent "context_agent" 10001

# Start Domain Real Estate Agent - Port 10002
start_agent "domain_realestate" 10002

echo ""
echo "🎉 All A2A agents started successfully!"
echo ""
echo "📊 Agent Registry:"
echo "  • Core Agent (Orchestrator): http://localhost:10000"
echo "  • Context Agent:              http://localhost:10001" 
echo "  • Domain Real Estate Agent:   http://localhost:10002"
echo ""
echo "🔍 Monitor logs:"
echo "  • tail -f logs/core_agent_a2a.log"
echo "  • tail -f logs/context_agent_a2a.log"
echo "  • tail -f logs/domain_realestate_a2a.log"
echo ""
echo "🛑 To stop all agents: ./local_playground/stop_a2a_agents.sh"
echo ""
echo "✅ A2A Multi-Agent System is ready for testing!"
