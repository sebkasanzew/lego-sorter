#!/usr/bin/env python3
"""
Blender MCP (Model Context Protocol) utility script.

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
import sys
import os

class BlenderMCPClient:
    """Client for communicating with Blender via MCP server"""
    
    def __init__(self, host='localhost', port=9876):
        self.host = host
        self.port = port
        self.timeout = 5
    
    def test_connection(self):
        """Test if we can connect to the Blender MCP server"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            
            if result == 0:
                print(f"✅ Blender MCP server is running on {self.host}:{self.port}")
                return True
            else:
                print(f"❌ Cannot connect to Blender MCP server on {self.host}:{self.port}")
                return False
        except Exception as e:
            print(f"❌ Error testing connection: {e}")
            return False
    
    def execute_code(self, code, description="code"):
        """Execute Python code in Blender via MCP"""
        try:
            # Connect to Blender MCP server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            
            # Command to execute the code
            command = {
                "type": "execute_code",
                "params": {
                    "code": code
                }
            }
            
            # Send command
            message = json.dumps(command) + '\n'
            sock.send(message.encode())
            
            # Receive response
            response = sock.recv(8192).decode()  # Increased buffer size
            sock.close()
            
            result = json.loads(response)
            if result.get('status') == 'success':
                print(f"✅ Successfully executed {description}!")
                result_data = result.get('result', 'No result message')
                if result_data:
                    print(f"Result: {result_data}")
            else:
                print(f"❌ Failed to execute {description}")
                print(f"Error: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error executing {description}: {e}")
    
    def execute_script_file(self, script_path, description=None):
        """Execute a Python script file in Blender via MCP"""
        if not os.path.exists(script_path):
            print(f"❌ Script file not found: {script_path}")
            return
        
        if description is None:
            description = os.path.basename(script_path)
        
        try:
            # Read the script content
            with open(script_path, 'r') as f:
                script_content = f.read()
            
            print(f"📝 Executing script: {script_path}")
            self.execute_code(script_content, description)
            
        except Exception as e:
            print(f"❌ Error reading script {script_path}: {e}")

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
