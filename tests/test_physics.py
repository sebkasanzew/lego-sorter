#!/usr/bin/env python3
"""
Test script to verify the LEGO sorter physics animation works correctly.
This script tests individual components of the physics simulation.
"""

import os
import sys

# Add the utils directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

from blender_mcp_client import BlenderMCPClient

def test_physics_script():
    """Test the physics animation script"""
    print("🔬 Testing LEGO Physics Animation Script")
    print("=" * 50)
    
    client = BlenderMCPClient()
    
    # Test connection
    if not client.test_connection():
        print("❌ Blender MCP server is not running")
        return False
    
    # Test basic physics setup code
    physics_test_code = '''
import bpy

# Test if we can create a rigid body world
try:
    if not bpy.context.scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    print("✅ Rigid body world created successfully")
    
    # Test creating a simple physics object
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 2))
    cube = bpy.context.active_object
    if cube:
        cube.name = "Physics_Test_Cube"
        bpy.ops.rigidbody.object_add(type='ACTIVE')
        cube.rigid_body.mass = 1.0
        cube.rigid_body.friction = 0.5
        print("✅ Test cube with physics created successfully")
    
    # Set up basic physics properties
    scene = bpy.context.scene
    scene.gravity = (0, 0, -9.81)
    print("✅ Physics properties configured successfully")
    
    print("🎉 Physics system test completed successfully!")
    
except Exception as e:
    print(f"❌ Physics test failed: {e}")
'''
    
    print("🧪 Running physics system test...")
    client.execute_code(physics_test_code, "Physics System Test")
    
    return True

def test_lego_part_detection():
    """Test if LEGO parts can be detected"""
    print("\n🔍 Testing LEGO parts detection...")
    
    client = BlenderMCPClient()
    
    detection_code = '''
import bpy

# Check for LEGO parts collection
lego_collection = bpy.data.collections.get("lego_parts")
if lego_collection:
    part_count = len([obj for obj in lego_collection.objects if obj.type == 'MESH'])
    print(f"✅ Found {part_count} LEGO parts in collection")
else:
    print("ℹ️  No LEGO parts collection found (this is expected if parts aren't imported yet)")

# Check for sorting bucket
bucket = bpy.data.objects.get("Sorting_Bucket")
if bucket:
    print(f"✅ Found sorting bucket: {bucket.name}")
else:
    print("ℹ️  No sorting bucket found (this is expected if bucket isn't created yet)")
'''
    
    client.execute_code(detection_code, "LEGO Parts Detection Test")

def main():
    """Run all tests"""
    print("🧱 LEGO Sorter Physics Test Suite")
    print("=" * 50)
    
    # Test the physics script
    if test_physics_script():
        # Test LEGO part detection
        test_lego_part_detection()
        print("\n🎉 All tests completed!")
    else:
        print("\n❌ Tests failed - check Blender MCP connection")

if __name__ == "__main__":
    main()
