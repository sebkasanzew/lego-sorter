#!/usr/bin/env python3
"""Tests for Jupyter notebook proof-of-concept.

This test validates that the notebook approach (Option A) works correctly
for controlling Blender via MCP.
"""

import os
import sys
import json

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "utils"))

from utils.blender_mcp_client import BlenderMCPClient


def test_notebook_can_connect_to_mcp():
    """Test that notebook-style code can connect to Blender MCP."""
    client = BlenderMCPClient(timeout=30)
    assert client.test_connection(), "MCP connection failed"


def test_notebook_can_execute_scripts():
    """Test that notebook can execute Blender scripts via MCP."""
    client = BlenderMCPClient(timeout=120)

    # Clear scene first
    success = client.execute_script_file(
        "blender/clear_scene.py", "Clear Scene", timeout=60
    )
    assert success, "Failed to clear scene"

    # Create bucket
    success = client.execute_script_file(
        "blender/create_sorting_bucket.py", "Create Bucket", timeout=120
    )
    assert success, "Failed to create bucket"


def test_notebook_can_execute_custom_code():
    """Test that notebook can execute custom Blender code."""
    client = BlenderMCPClient(timeout=30)

    # Custom code to get scene info
    custom_code = """
import bpy

# Get object count
total_objects = len(bpy.data.objects)
print(f"Total objects: {total_objects}")

# Verify bucket collection exists
bucket_col = bpy.data.collections.get("bucket")
if bucket_col:
    print(f"Bucket collection has {len(bucket_col.objects)} objects")
"""

    success = client.execute_code(custom_code, "Get Scene Info")
    assert success, "Failed to execute custom code"


def test_notebook_error_handling():
    """Test that notebook handles errors gracefully."""
    client = BlenderMCPClient(timeout=30)

    # Intentionally bad code
    bad_code = """
import bpy
# This will fail - accessing non-existent object
obj = bpy.data.objects["NonExistentObject"]
"""

    # Should return False but not crash
    success = client.execute_code(bad_code, "Bad Code Test")
    assert not success, "Bad code should fail"


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
