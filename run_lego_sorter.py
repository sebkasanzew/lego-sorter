#!/usr/bin/env python3
"""Main runner script for the LEGO Sorter project.

This script provides a simple interface to run the main functionality
of the LEGO sorter project, including creating buckets and importing
LEGO parts into Blender via the MCP server.

Usage:
    python run_lego_sorter.py
"""

import os
import sys
import time

# Add the utils directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))

from blender_mcp_client import BlenderMCPClient


def run_with_retries(
    client: BlenderMCPClient,
    script: str,
    desc: str,
    attempts: int = 2,
    timeout: int = 300,
) -> bool:
    """Run a Blender script via MCP with limited retries and exponential backoff."""
    for i in range(1, attempts + 1):
        ok = client.execute_script_file(script, desc, timeout=timeout)
        if ok:
            return True
        if i < attempts:
            wait_s = 2**i
            print(f"⏳ Retrying {desc} in {wait_s}s (attempt {i+1}/{attempts})…")
            time.sleep(wait_s)
    return False


def main():
    """Main function to run the LEGO sorter"""
    print("🧱 LEGO Sorter - Blender Simulation")
    print("=" * 40)

    # Debug mode support: shorter timeouts and fewer attempts when BLENDER_MCP_DEBUG=1
    is_debug = os.getenv("BLENDER_MCP_DEBUG", "0") == "1"
    # Accept longer default timeout via env or default to 300s (or 30s in debug)
    default_timeout = int(os.getenv("BLENDER_MCP_TIMEOUT", "30" if is_debug else "300"))
    client = BlenderMCPClient(timeout=default_timeout)

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
    if is_debug:
        print(f"🧪 Debug mode: timeouts set to {default_timeout}s, retries minimized.")

    # Get script paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    blender_dir = os.path.join(script_dir, "blender")

    # 0. Clear the scene first
    print("\n🧹 Clearing Blender scene...")
    clear_script = os.path.join(blender_dir, "clear_scene.py")
    if os.path.exists(clear_script):
        if not run_with_retries(
            client,
            clear_script,
            "Scene Clearing",
            attempts=(1 if is_debug else 2),
            timeout=default_timeout,
        ):
            print("❌ Scene clearing failed after retries")
            return
    else:
        print(f"❌ Clear scene script not found: {clear_script}")
        return

    # 1. Create sorting bucket
    print("\n1️⃣ Creating sorting bucket...")
    bucket_script = os.path.join(blender_dir, "create_sorting_bucket.py")
    if os.path.exists(bucket_script):
        if not run_with_retries(
            client,
            bucket_script,
            "Sorting Bucket",
            attempts=(1 if is_debug else 2),
            timeout=default_timeout,
        ):
            print("❌ Bucket creation failed after retries")
            return
    else:
        print(f"❌ Bucket script not found: {bucket_script}")
        return

    # 2. Create conveyor belt system (optional: set environment SKIP_CONVEYOR=1 to skip)
    skip_conveyor = os.getenv("SKIP_CONVEYOR", "0") == "1"
    if skip_conveyor:
        print("\n2️⃣ Skipping conveyor belt creation (SKIP_CONVEYOR=1)")
    else:
        print("\n2️⃣ Creating conveyor belt system...")
        conveyor_script = os.path.join(blender_dir, "create_conveyor_belt.py")
        if os.path.exists(conveyor_script):
            if not run_with_retries(
                client,
                conveyor_script,
                "Conveyor Belt System",
                attempts=(1 if is_debug else 2),
                timeout=default_timeout,
            ):
                print("❌ Conveyor creation failed after retries")
                return
        else:
            print(f"❌ Conveyor belt script not found: {conveyor_script}")
            return

    # 3. Import LEGO parts
    print("\n3️⃣ Importing LEGO parts...")
    parts_script = os.path.join(blender_dir, "import_lego_parts.py")
    if os.path.exists(parts_script):
        if not run_with_retries(
            client, parts_script, "LEGO Parts", attempts=1, timeout=default_timeout
        ):
            print("⚠️  Skipping LEGO parts due to timeout/error (continuing)")
    else:
        print(f"❌ Parts script not found: {parts_script}")
        return

    # 4. Setup physics animation
    print("\n4️⃣ Setting up physics simulation...")
    physics_script = os.path.join(blender_dir, "animate_lego_physics.py")
    if os.path.exists(physics_script):
        if not run_with_retries(
            client,
            physics_script,
            "Physics Animation",
            attempts=1,
            timeout=default_timeout,
        ):
            print("⚠️  Skipping physics setup due to timeout/error (continuing)")
    else:
        print(f"❌ Physics script not found: {physics_script}")
        return

    # 5. Setup lighting
    print("\n5️⃣ Setting up lighting...")
    lighting_script = os.path.join(blender_dir, "setup_lighting.py")
    if os.path.exists(lighting_script):
        if not run_with_retries(
            client,
            lighting_script,
            "Lighting Setup",
            attempts=1,
            timeout=default_timeout,
        ):
            print("⚠️  Skipping lighting due to timeout/error (continuing)")
    else:
        print(f"❌ Lighting script not found: {lighting_script}")

    # 6. Render a snapshot to add a camera and save PNGs
    print("\n6️⃣ Rendering snapshot (adds camera)...")
    snapshot_script = os.path.join(blender_dir, "render_snapshot.py")
    if os.path.exists(snapshot_script):
        snap_timeout = max(default_timeout, 120 if is_debug else 420)
        if not run_with_retries(
            client, snapshot_script, "Snapshot Render", attempts=1, timeout=snap_timeout
        ):
            print("⚠️  Snapshot rendering failed")
        print(
            "📸 Snapshots saved to renders/snapshot*.png and renders/snapshot_ortho_*.png (camera 'SorterCam' created)"
        )
    else:
        print(f"❌ Snapshot script not found: {snapshot_script}")

    print("\n🎉 LEGO sorter simulation completed!")
    print("Check your Blender scene for the complete sorting system:")
    print("  • Sorting bucket with collection hole")
    print("  • Conveyor belt system with supports")
    print("  • LEGO parts positioned for sorting")
    print(
        "🎬 Physics simulation is now running - parts will flow from bucket to conveyor!"
    )
    print(
        "📷 A camera named 'SorterCam' should be present; latest snapshot at renders/snapshot.png"
    )


if __name__ == "__main__":
    main()
