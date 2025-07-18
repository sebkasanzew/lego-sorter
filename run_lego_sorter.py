#!/usr/bin/env python3
"""
Main runner script for the LEGO Sorter project.

This script provides a simple interface to run the main functionality
of the LEGO sorter project, including creating buckets and importing
LEGO parts into Blender via the MCP server.

Usage:
    python run_lego_sorter.py
"""

import os
import sys

# Add the utils directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from blender_mcp_client import BlenderMCPClient

def main():
    """Main function to run the LEGO sorter"""
    print("🧱 LEGO Sorter - Blender Simulation")
    print("=" * 40)
    
    client = BlenderMCPClient()
    
    # Test connection
    print("🔍 Testing Blender MCP connection...")
    if not client.test_connection():
        print("\n📋 Setup Instructions:")
        print("1. Open Blender")
        print("2. Go to 3D View sidebar (press N)")
        print("3. Find 'BlenderMCP' tab")
        print("4. Click 'Connect to Claude'")
        print("5. Run this script again")
        return
    
    # Execute the main scripts
    print(f"\n🎯 Running LEGO sorter simulation...")
    
    # Get script paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    blender_dir = os.path.join(script_dir, "blender")
    
    # 0. Clear the scene first
    print("\n🧹 Clearing Blender scene...")
    clear_script = os.path.join(blender_dir, "clear_scene.py")
    if os.path.exists(clear_script):
        client.execute_script_file(clear_script, "Scene Clearing")
    else:
        print(f"❌ Clear scene script not found: {clear_script}")
        return
    
    # 1. Create sorting bucket
    print("\n1️⃣ Creating sorting bucket...")
    bucket_script = os.path.join(blender_dir, "create_sorting_bucket.py")
    if os.path.exists(bucket_script):
        client.execute_script_file(bucket_script, "Sorting Bucket")
    else:
        print(f"❌ Bucket script not found: {bucket_script}")
        return
    
    # 2. Import LEGO parts
    print("\n2️⃣ Importing LEGO parts...")
    parts_script = os.path.join(blender_dir, "import_lego_parts.py")
    if os.path.exists(parts_script):
        client.execute_script_file(parts_script, "LEGO Parts")
    else:
        print(f"❌ Parts script not found: {parts_script}")
        return
    
    # 3. Setup physics animation
    print("\n3️⃣ Setting up physics simulation...")
    physics_script = os.path.join(blender_dir, "animate_lego_physics.py")
    if os.path.exists(physics_script):
        client.execute_script_file(physics_script, "Physics Animation")
    else:
        print(f"❌ Physics script not found: {physics_script}")
        return
    
    print("\n🎉 LEGO sorter simulation completed!")
    print("Check your Blender scene for the imported parts and sorting bucket.")
    print("🎬 Physics simulation is now running - parts will fall under gravity!")

if __name__ == "__main__":
    main()
