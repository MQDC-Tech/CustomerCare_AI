#!/usr/bin/env python3
"""
ADK-native A2A agent stop script.
"""

import os
import signal
import subprocess
import sys
from pathlib import Path


def kill_processes_on_port(port):
    """Kill all processes using the specified port."""
    try:
        # Find processes using the port
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    pid = int(pid.strip())
                    os.kill(pid, signal.SIGTERM)
                    print(f"✅ Killed process {pid} on port {port}")
                except (ValueError, ProcessLookupError, PermissionError) as e:
                    print(f"⚠️  Could not kill process {pid}: {e}")
        else:
            print(f"ℹ️  No processes found on port {port}")
    except FileNotFoundError:
        print("⚠️  lsof command not found, trying alternative method")
        # Alternative method using netstat and kill
        try:
            result = subprocess.run(
                ["netstat", "-tulpn", "|", "grep", f":{port}"],
                shell=True,
                capture_output=True,
                text=True
            )
            print(f"ℹ️  Port {port} status: {result.stdout}")
        except Exception as e:
            print(f"⚠️  Could not check port {port}: {e}")


def main():
    """Stop all running multi-agent system services."""
    print("🛑 Stopping Complete Multi-Agent System")
    print("=" * 50)

    # Kill processes on specific ports
    print("\n🔍 Checking and stopping processes on agent ports...")
    kill_processes_on_port(8001)  # Core Agent (A2A)
    kill_processes_on_port(8002)  # Context Agent (A2A)
    kill_processes_on_port(8080)  # Domain Agent (ADK Web)
    
    # Also try to kill any uvicorn processes (A2A services)
    print("\n🔍 Stopping uvicorn A2A processes...")
    try:
        result = subprocess.run(
            ["pkill", "-f", "uvicorn.*expose_a2a"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Stopped uvicorn A2A processes")
        else:
            print("ℹ️  No uvicorn A2A processes found")
    except Exception as e:
        print(f"⚠️  Could not stop uvicorn processes: {e}")
    
    # Kill any ADK web processes
    print("\n🔍 Stopping ADK web processes...")
    try:
        result = subprocess.run(
            ["pkill", "-f", "google.adk.cli.*web"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Stopped ADK web processes")
        else:
            print("ℹ️  No ADK web processes found")
    except Exception as e:
        print(f"⚠️  Could not stop ADK web processes: {e}")

    project_root = Path(__file__).parent.parent
    pid_file = project_root / "a2a_pids.txt"
    stopped_count = 0

    if pid_file.exists():
        print("\n🔍 Stopping processes from PID file...")
        
        # Read and stop each process
        with open(pid_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    agent_name, pid_str = line.split(":")
                    pid = int(pid_str)

                    # Try to terminate the process
                    try:
                        os.kill(pid, signal.SIGTERM)
                        print(f"✅ Stopped {agent_name} (PID: {pid})")
                        stopped_count += 1
                    except ProcessLookupError:
                        print(f"⚠️  {agent_name} (PID: {pid}) was not running")
                    except PermissionError:
                        print(f"❌ Permission denied stopping {agent_name} (PID: {pid})")

                except ValueError:
                    print(f"⚠️  Invalid PID file entry: {line}")
    else:
        print("ℹ️  No PID file found")

    # Clean up PID file if it exists
    if pid_file.exists():
        pid_file.unlink()

    print(f"\n🎯 Stopped {stopped_count} services from PID file")
    print("✅ All multi-agent system services have been stopped")
    print("\n🌐 System Status:")
    print("   • Core Agent (A2A :8001): 🛑 Stopped")
    print("   • Context Agent (A2A :8002): 🛑 Stopped")
    print("   • Domain Agent (Web :8080): 🛑 Stopped")


if __name__ == "__main__":
    main()
