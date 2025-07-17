#!/usr/bin/env python3
"""
Blender scene clearing utility script.

This script provides functions to clear the Blender scene, including
removing all objects and cleaning up empty collections.

Usage:
- Run this script in Blender to clear the entire scene
- Use the clear_scene() function to remove all objects and collections
"""

import bpy

def remove_all_objects():
    """Remove all objects from the scene"""
    if bpy.context.object:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        print("✅ Removed all objects from scene")
    else:
        print("ℹ️  No objects to delete in scene")

def clean_empty_collections():
    """Clean up empty collections"""
    removed_count = 0
    for collection in list(bpy.data.collections):
        if not collection.objects:
            bpy.data.collections.remove(collection)
            removed_count += 1
    
    if removed_count > 0:
        print(f"✅ Cleaned up {removed_count} empty collections")
    else:
        print("ℹ️  No empty collections to clean")

def clear_scene():
    """Clear the entire Blender scene"""
    print("🧹 Clearing Blender scene...")
    
    # Remove all objects
    remove_all_objects()
    
    # Clean up empty collections
    clean_empty_collections()
    
    print("✅ Scene cleared successfully")

def main():
    """Main function to clear the scene"""
    clear_scene()

# Always run main when script is executed
main()
