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


def get_venv_python():
    venv_path = project_root / "venv"
    if os.name == "nt":  # Windows
        return str(venv_path / "Scripts" / "python.exe")
    else:  # Unix/Linux/macOS
        return str(venv_path / "bin" / "python")


def start_domain_agent_web(venv_python):
    """Start Domain Agent via ADK web interface."""
    try:
        print("\n🏠 Starting Domain Agent (ADK Web Interface on port 8080)...")
        
        # Change to project root and start ADK web
        cmd = [
            venv_python, "-m", "google.adk.cli", 
            "web", "agents/domain_realestate",
            "--port", "8080"
        ]
        
        # Start ADK web in background
        process = subprocess.Popen(
            cmd,
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it time to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Domain Agent (ADK Web) started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Failed to start Domain Agent: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting Domain Agent: {e}")
        return None


def main():
    """Start complete multi-agent system: A2A services + Domain Agent web interface."""
    print("🚀 Starting Complete Multi-Agent System...")
    print("=" * 50)
    
    # Setup virtual environment and dependencies
    venv_python = setup_virtual_environment()
    
    processes = []
    
    # Start Core Agent (A2A service)
    print("\n📋 Starting Core Agent (A2A service on port 8001)...")
    core_process = start_to_a2a_server("core_agent", "agents/core_agent/expose_a2a.py", 8001, venv_python)
    if core_process:
        processes.append(("core_agent", core_process, 8001))
        time.sleep(2)  # Allow time for startup
    
    # Start Context Agent (A2A service)
    print("\n👤 Starting Context Agent (A2A service on port 8002)...")
    context_process = start_to_a2a_server("context_agent", "agents/context_agent/expose_a2a.py", 8002, venv_python)
    if context_process:
        processes.append(("context_agent", context_process, 8002))
        time.sleep(2)  # Allow time for startup
    
    # Start Domain Agent (ADK Web Interface)
    domain_process = start_domain_agent_web(venv_python)
    if domain_process:
        processes.append(("domain_agent_web", domain_process, 8080))
        time.sleep(2)  # Allow time for startup
    
    if not processes:
        print("❌ Failed to start any services")
        return
    
    print(f"\n✅ Started {len(processes)} services")
    print("\n🌐 System Endpoints:")
    for agent_name, process, port in processes:
        if agent_name == "domain_agent_web":
            print(f"  🏠 Domain Agent (Web UI): http://localhost:{port}")
        else:
            print(f"  🤖 {agent_name}: http://localhost:{port}")
            print(f"      Agent Card: http://localhost:{port}/.well-known/agent.json")

    # Save PIDs for cleanup
    pid_file = project_root / "a2a_pids.txt"
    with open(pid_file, "w") as f:
        for agent_name, process, port in processes:
            f.write(f"{agent_name}:{process.pid}\n")
    
    print("\n" + "=" * 60)
    print("🎯 MULTI-AGENT SYSTEM READY")
    print("=" * 60)
    print("✅ All services started successfully!")
    print("\n🌐 Access the system:")
    print("   👉 Open browser: http://localhost:8080")
    print("\n🏗️ Architecture:")
    print("   User → Domain Agent (Web :8080) → A2A Services")
    print("   • Core Agent (A2A): http://localhost:8001")
    print("   • Context Agent (A2A): http://localhost:8002")
    print("\n🧪 Test these scenarios:")
    print('   • "Remember that I prefer 3-bedroom houses"')
    print('   • "Find me 3-bedroom houses under $500k"')
    print('   • "What\'s the weather today?"')
    print('   • "What are my saved preferences?"')

    print(f"\n📝 Process IDs saved to: {pid_file}")
    print("\n🛑 To stop all services, run: python3 scripts/stop_a2a_agents.py")
    print("\n⚠️  Keep this terminal open - services are running in background")


if __name__ == "__main__":
    main()
