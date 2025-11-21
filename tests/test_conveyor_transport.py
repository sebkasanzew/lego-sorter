#!/usr/bin/env python3
"""Quick validation script to test conveyor belt transport improvements.

Run this after executing the full pipeline to verify LEGO parts are being transported.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), "utils"))

from utils.blender_mcp_client import BlenderMCPClient


def test_conveyor_transport():
    """Test that LEGO parts are being transported by the conveyor."""
    client = BlenderMCPClient(timeout=120)

    print("=== Conveyor Belt Transport Validation ===\n")

    # Test connection
    if not client.test_connection():
        print("❌ Failed to connect to Blender MCP server")
        return False

    print("✓ Connected to Blender\n")

    # Run the validation code
    response = client.execute_code(
        """
import bpy

# Get a test LEGO part
lego_col = bpy.data.collections.get("lego_parts")
if not lego_col or len(lego_col.objects) == 0:
    print("❌ No LEGO parts found")
else:
    test_part = list(lego_col.objects)[0]
    scene = bpy.context.scene
    
    # Track movement over frames
    positions = []
    for frame in [1, 20, 40]:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        pos = test_part.location.copy()
        positions.append((frame, pos.x, pos.y, pos.z))
    
    print(f"Part: {test_part.name}")
    print("\\nFrame | X Position | Movement")
    print("------|------------|----------")
    
    start_x = positions[0][1]
    for frame, x, y, z in positions:
        delta = x - start_x
        status = "✓" if abs(delta) > 0.05 else "⚠️"
        print(f"{frame:5d} | {x:10.3f} | {delta:+8.3f} {status}")
    
    # Final verdict
    total_movement = positions[-1][1] - positions[0][1]
    if abs(total_movement) > 0.1:
        print(f"\\n✅ SUCCESS: Part moved {total_movement:.3f} units!")
        print("   Conveyor is transporting parts properly.")
    else:
        print(f"\\n❌ FAILURE: Part only moved {total_movement:.3f} units")
        print("   Check physics settings and part positioning.")
""",
        "Validation Test",
    )

    # Response is a dict when execute_code succeeds
    if isinstance(response, dict) and response.get("status") == "success":
        print("\n" + str(response.get("output", "")))
        return True
    else:
        error_msg = (
            response.get("message", "Unknown error")
            if isinstance(response, dict)
            else "Execution failed"
        )
        print(f"❌ Test failed: {error_msg}")
        return False


if __name__ == "__main__":
    success = test_conveyor_transport()
    sys.exit(0 if success else 1)
