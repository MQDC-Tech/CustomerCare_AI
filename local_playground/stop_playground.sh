#!/bin/bash
echo "🛑 Stopping ADK Playground..."

# Check if PID file exists and kill the specific process
if [ -f "logs/playground/adk_server.pid" ]; then
    PID=$(cat logs/playground/adk_server.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "Stopping ADK server (PID: $PID)..."
        kill $PID
        sleep 2
        # Force kill if still running
        if kill -0 $PID 2>/dev/null; then
            kill -9 $PID
        fi
    fi
    rm -f logs/playground/adk_server.pid
fi

# Kill any remaining ADK web processes
pkill -f "adk web" 2>/dev/null || true

# Kill processes on playground port as backup
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

echo "✅ ADK Playground stopped."
