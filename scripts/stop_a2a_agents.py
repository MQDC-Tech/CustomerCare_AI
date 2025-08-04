#!/usr/bin/env python3
"""
ADK-native A2A agent stop script.
"""

import os
import signal
import sys
from pathlib import Path


def main():
    """Stop all running A2A agent services."""
    print("🛑 Stopping ADK-native A2A Agent Services")
    print("=" * 50)

    project_root = Path(__file__).parent.parent
    pid_file = project_root / "a2a_pids.txt"

    if not pid_file.exists():
        print("❌ No PID file found. A2A services may not be running.")
        return

    stopped_count = 0

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

    # Clean up PID file
    pid_file.unlink()

    print(f"\n🎯 Stopped {stopped_count} A2A services")
    print("✅ All A2A agent services have been stopped")


if __name__ == "__main__":
    main()
