#!/usr/bin/env python3
"""Blender MCP (Model Context Protocol) utility script.

This script provides utilities to connect to and execute scripts in Blender
via the MCP server. It includes functions to test connectivity and execute
Python scripts within Blender remotely.

Requirements:
- Blender MCP server running (typically on localhost:9876)
- BlenderMCP addon enabled in Blender

Usage:
- Run this script to execute other Blender scripts via MCP
- Modify the main() function to run different scripts
"""

import json
import socket
import os
import time
from typing import Optional


class BlenderMCPClient:
    """Client for communicating with Blender via MCP server."""

    def __init__(
        self, host: str = "localhost", port: int = 9876, timeout: Optional[int] = None
    ):
        """Initialize the client with host, port and optional timeout."""
        self.host = host
        self.port = port
        # Allow override via constructor or env var, default to 180s for heavy Blender ops
        env_timeout = os.getenv("BLENDER_MCP_TIMEOUT")
        self.timeout = int(
            timeout if timeout is not None else (env_timeout if env_timeout else 180)
        )

    def _effective_timeout(self, timeout: Optional[int]) -> int:
        """Return the timeout to use (param > env > default)."""
        if timeout is not None:
            return int(timeout)
        return int(self.timeout)

    def test_connection(self):
        """Test if we can connect to the Blender MCP server"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self._effective_timeout(None))
            result = sock.connect_ex((self.host, self.port))
            sock.close()

            if result == 0:
                print(f"✅ Blender MCP server is running on {self.host}:{self.port}")
                return True
            else:
                print(
                    f"❌ Cannot connect to Blender MCP server on {self.host}:{self.port}"
                )
                return False
        except Exception as e:
            print(f"❌ Error testing connection: {e}")
            return False

    def execute_code(
        self, code: str, description: str = "code", timeout: Optional[int] = None
    ) -> bool:
        """Execute Python code in Blender via MCP"""
        try:
            # Connect to Blender MCP server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Enable TCP keepalive to survive long renders
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            except Exception:
                pass
            sock.settimeout(self._effective_timeout(timeout))
            sock.connect((self.host, self.port))

            # Command to execute the code
            command = {"type": "execute_code", "params": {"code": code}}

            # Send command
            message = json.dumps(command, ensure_ascii=False) + "\n"
            sock.sendall(message.encode("utf-8", errors="replace"))

            # Receive response using a non-blocking loop with heartbeat
            total_timeout = self._effective_timeout(timeout)
            is_debug = os.getenv("BLENDER_MCP_DEBUG", "0") == "1"
            deadline = time.time() + total_timeout
            buffer = bytearray()
            last_notice = time.time()
            response_text: Optional[str] = None
            while True:
                now = time.time()
                if now >= deadline:
                    raise socket.timeout()
                # Small per-iteration timeout
                sock.settimeout(max(0.5, min(2.0, deadline - now)))
                try:
                    chunk = sock.recv(8192)
                except socket.timeout:
                    # Heartbeat every ~2s in debug, ~5s otherwise
                    interval = 2.0 if is_debug else 5.0
                    if time.time() - last_notice > interval:
                        print("… waiting for Blender to finish (MCP)")
                        last_notice = time.time()
                    continue
                if not chunk:
                    # Socket closed by server; try to parse what we have
                    try:
                        response_text = buffer.decode("utf-8", errors="replace").strip()
                        # Best-effort: break and parse below
                        break
                    except Exception:
                        break
                buffer.extend(chunk)
                # Prefer newline-terminated JSON; otherwise, attempt parse of full buffer
                if b"\n" in buffer:
                    line, _rest = buffer.split(b"\n", 1)
                    response_text = line.decode("utf-8", errors="replace").strip()
                    break
                else:
                    # Try to parse full buffer as JSON if it looks complete
                    try:
                        tentative = buffer.decode("utf-8", errors="replace").strip()
                        # Quick sanity: must start with { and end with }
                        if tentative.startswith("{") and tentative.endswith("}"):
                            # Try a non-throwing check
                            json.loads(tentative)
                            response_text = tentative
                            break
                    except Exception:
                        pass

            sock.close()

            if not response_text:
                raise TimeoutError("No response received from Blender MCP (empty).")

            response = response_text

            result = json.loads(response)
            if result.get("status") == "success":
                print(f"✅ Successfully executed {description}!")
                result_data = result.get("result", "No result message")
                if result_data:
                    # Handle nested result structure from Blender MCP
                    if isinstance(result_data, dict) and "result" in result_data:
                        # Extract the actual result string
                        actual_result = result_data["result"]
                        if isinstance(actual_result, str):
                            formatted_result = actual_result.replace("\\n", "\n")
                            print(f"Result:\n{formatted_result}")
                        else:
                            print(f"Result: {actual_result}")
                    elif isinstance(result_data, str):
                        formatted_result = result_data.replace("\\n", "\n")
                        print(f"Result:\n{formatted_result}")
                    else:
                        print(f"Result: {result_data}")
                return True
            else:
                print(f"❌ Failed to execute {description}")
                error_message = result.get("message", "Unknown error")
                if isinstance(error_message, str):
                    formatted_error = error_message.replace("\\n", "\n")
                    print(f"Error: {formatted_error}")
                else:
                    print(f"Error: {error_message}")
                return False
        except socket.timeout:
            # Guidance for users when long operations exceed timeout
            print(
                f"❌ Error executing {description}: timed out after {self._effective_timeout(timeout)}s"
            )
            print(
                "💡 Tip: Increase timeout via BLENDER_MCP_TIMEOUT env var or BlenderMCPClient(timeout=...)."
            )
            return False
        except Exception as e:
            print(f"❌ Error executing {description}: {e}")
            return False

    def execute_script_file(
        self,
        script_path: str,
        description: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> bool:
        """Execute a Python script file in Blender via MCP"""
        if not os.path.exists(script_path):
            print(f"❌ Script file not found: {script_path}")
            return False

        if description is None:
            description = os.path.basename(script_path)

        try:
            # Read the script content
            with open(script_path, "r") as f:
                script_content = f.read()

            print(f"📝 Executing script: {script_path}")
            return self.execute_code(script_content, description, timeout=timeout)

        except Exception as e:
            print(f"❌ Error reading script {script_path}: {e}")
            return False


def main():
    """Main function to demonstrate MCP usage"""
    print("🔗 Blender MCP Client")
    print("=" * 50)

    client = BlenderMCPClient()

    # Test connection
    print("🔍 Testing Blender MCP connection...")
    if not client.test_connection():
        print("\n📋 To set up Blender MCP:")
        print("1. Open Blender")
        print("2. Go to 3D View sidebar (press N)")
        print("3. Find 'BlenderMCP' tab")
        print("4. Click 'Connect to Claude'")
        print("5. Run this script again")
        return

    # Execute Blender scripts
    print(f"\n🎯 Executing Blender scripts...")

    # Get the blender directory path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    blender_dir = os.path.join(script_dir, "..", "blender")

    # Execute bucket creation script
    bucket_script = os.path.join(blender_dir, "create_sorting_bucket.py")
    if os.path.exists(bucket_script):
        client.execute_script_file(bucket_script, "Sorting Bucket Creation")
    else:
        print(f"⚠️  Bucket script not found: {bucket_script}")

    # Execute LEGO parts import script
    parts_script = os.path.join(blender_dir, "import_lego_parts.py")
    if os.path.exists(parts_script):
        client.execute_script_file(parts_script, "LEGO Parts Import")
    else:
        print(f"⚠️  Parts import script not found: {parts_script}")

    print("\n✅ All scripts executed successfully!")


if __name__ == "__main__":
    main()
