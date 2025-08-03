#!/bin/bash

# A2A Multi-Agent Stop Script
# Stops all A2A agent servers gracefully

set -e

echo "🛑 Stopping ADK-native A2A Multi-Agent System..."

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Function to stop an agent server
stop_agent() {
    local agent_name=$1
    local pid_file="logs/${agent_name}_a2a.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        echo "🤖 Stopping ${agent_name} A2A server (PID: ${pid})..."
        
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            sleep 2
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "   ⚠️  Force killing ${agent_name}..."
                kill -9 "$pid" 2>/dev/null || true
            fi
            
            echo "   ✅ ${agent_name} stopped"
        else
            echo "   ⚠️  ${agent_name} was not running"
        fi
        
        rm -f "$pid_file"
    else
        echo "🤖 ${agent_name}: No PID file found"
    fi
}

# Stop all A2A agent servers
echo ""
echo "🎯 Stopping A2A Agent Servers..."
echo "================================"

# Stop agents in reverse order
stop_agent "domain_realestate"
stop_agent "context_agent" 
stop_agent "core_agent"

# Clean up any remaining processes
echo ""
echo "🧹 Cleaning up any remaining A2A processes..."
pkill -f "python -m agents\." 2>/dev/null || true

echo ""
echo "✅ All A2A agents stopped successfully!"
