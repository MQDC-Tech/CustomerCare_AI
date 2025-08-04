#!/usr/bin/env python3
"""
A2A Agent Startup Script
Starts Domain Real Estate Agent and Context Agent as A2A servers using Google's to_a2a() method.
Automatically sets up virtual environment and installs dependencies.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def setup_virtual_environment():
    """Create virtual environment and install dependencies if needed."""
    venv_path = project_root / "venv"

    print("🔧 Setting up virtual environment and dependencies...")

    # Create virtual environment if it doesn't exist
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

    # Determine the python executable in the venv
    if os.name == "nt":  # Windows
        venv_python = venv_path / "Scripts" / "python.exe"
        pip_cmd = venv_path / "Scripts" / "pip.exe"
    else:  # Unix/Linux/macOS
        venv_python = venv_path / "bin" / "python"
        pip_cmd = venv_path / "bin" / "pip"

    # Install/upgrade pip
    print("📦 Upgrading pip...")
    subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], check=True)

    # Install requirements if requirements.txt exists
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        print("📦 Installing requirements from requirements.txt...")
        subprocess.run([str(pip_cmd), "install", "-r", str(requirements_file)], check=True)

    # Install essential ADK and A2A dependencies
    essential_packages = ["google-adk", "a2a", "uvicorn", "fastapi", "pydantic", "httpx", "aiohttp"]

    print("📦 Installing essential packages...")
    for package in essential_packages:
        try:
            subprocess.run([str(pip_cmd), "install", package], check=True, capture_output=True)
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Failed to install {package}: {e}")

    print("✅ Virtual environment setup complete!")
    return str(venv_python)


def start_to_a2a_server(agent_name, expose_script_path, port, venv_python):
    """Start an agent using to_a2a() method with uvicorn."""
    try:
        print(f"🚀 Starting {agent_name} on port {port} using to_a2a() method...")

        # Start the expose_a2a.py script directly using venv python
        cmd = [venv_python, expose_script_path]

        # Create logs directory if it doesn't exist
        logs_dir = project_root / "logs"
        logs_dir.mkdir(exist_ok=True)

        # Set up log files
        log_file = logs_dir / f"{agent_name.lower().replace(' ', '_')}_a2a.log"

        # Start the process in the background with log redirection
        log_handle = open(log_file, "w")
        process = subprocess.Popen(cmd, cwd=project_root, stdout=log_handle, stderr=subprocess.STDOUT, text=True)

        print(f"✅ {agent_name} started with PID {process.pid}")
        print(f"📋 Agent Card: http://localhost:{port}/.well-known/agent.json")

        return process

    except Exception as e:
        print(f"❌ Failed to start {agent_name}: {e}")
        return None


def start_domain_agent():
    """Start Domain Real Estate Agent using proper A2A server"""
    cmd = [sys.executable, "agents/domain_realestate/a2a_server.py"]

    print("🚀 Starting Domain Real Estate Agent on port 8001 using proper A2A server...")
    process = subprocess.Popen(cmd, cwd=project_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Give it a moment to start
    time.sleep(2)

    if process.poll() is None:
        print(f"✅ Domain Real Estate Agent started with PID {process.pid}")
        print("📋 Agent Card: http://localhost:8001/.well-known/agent.json")
        print("🔗 A2A Endpoint: http://localhost:8001/v1/messages:send")
        return ("Domain Real Estate Agent", process, 8001)
    else:
        stdout, stderr = process.communicate()
        print(f"❌ Failed to start Domain Real Estate Agent")
        print(f"Error: {stderr.decode()}")
        return None


def start_context_agent():
    """Start Context Agent using proper A2A server"""
    cmd = [sys.executable, "agents/context_agent/a2a_server.py"]

    print("🚀 Starting Context Agent on port 8002 using proper A2A server...")
    process = subprocess.Popen(cmd, cwd=project_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Give it a moment to start
    time.sleep(2)

    if process.poll() is None:
        print(f"✅ Context Agent started with PID {process.pid}")
        print("📋 Agent Card: http://localhost:8002/.well-known/agent.json")
        print("🔗 A2A Endpoint: http://localhost:8002/v1/messages:send")
        return ("Context Agent", process, 8002)
    else:
        stdout, stderr = process.communicate()
        print(f"❌ Failed to start Context Agent")
        print(f"Error: {stderr.decode()}")
        return None


def main():
    """Start all A2A agent services using official ADK to_a2a() method."""
    print("🌐 Starting A2A Agent Services (Official ADK to_a2a Method)")
    print("=" * 50)

    # Set up virtual environment and install dependencies
    venv_python = setup_virtual_environment()

    agents = [
        ("Domain Real Estate Agent", "agents/domain_realestate/expose_a2a.py", 8001),
        ("Context Agent", "agents/context_agent/expose_a2a.py", 8002),
    ]

    processes = []

    # Start each agent's A2A service
    for agent_name, expose_script, port in agents:
        process = start_to_a2a_server(agent_name, expose_script, port, venv_python)
        if process:
            processes.append((agent_name, process, port))

    if not processes:
        print("❌ No A2A services started successfully")
        sys.exit(1)

    print(f"\n✅ Started {len(processes)} A2A services")
    print("\nAgent endpoints:")
    for agent_name, process, port in processes:
        print(f"  • {agent_name}: http://localhost:{port}")
        print(f"    Agent Card: http://localhost:{port}/.well-known/agent.json")

    # Save PIDs for cleanup
    pid_file = project_root / "a2a_pids.txt"
    with open(pid_file, "w") as f:
        for agent_name, process, port in processes:
            f.write(f"{agent_name}:{process.pid}\n")

    print(f"\n📝 Process IDs saved to: {pid_file}")
    print("\n🛑 To stop all A2A services, run: python scripts/stop_a2a_agents.py")
    print("🧪 To test A2A communication, run: python test_refactored_a2a.py")


if __name__ == "__main__":
    main()
