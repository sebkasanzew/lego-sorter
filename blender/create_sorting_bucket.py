#!/usr/bin/env python3
"""
Blender script to create a sorting bucket for LEGO parts.

This script creates a hollow bucket with a base that can be used
to sort LEGO parts in the Blender scene.

Usage:
- Run this script in Blender to create a bucket object
- The bucket will be added to a 'bucket' collection
- Previous bucket objects will be cleared before creating a new one
"""

import bpy
from typing import Optional, Tuple, Any

def create_bucket() -> Tuple[Optional[Any], None]:
    """Create a hollow bucket with a base for sorting LEGO parts using boolean operations"""
    # Bucket dimensions in meters (24cm x 24cm square)
    bucket_size_top = 0.24  # 24cm square at top
    bucket_size_bottom = 0.06  # 6cm square at bottom (funnel exit)
    bucket_height = 0.20  # Reasonable height
    wall_thickness = 0.01  # 1cm thick walls

    # Create the outer bucket (frustum shape)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.0))  # type: ignore
    outer_bucket = bpy.context.active_object
    if outer_bucket:
        outer_bucket.name = "Outer_Bucket_Temp"
    
    # Enter edit mode and modify to frustum shape
    bpy.ops.object.mode_set(mode='EDIT')  # type: ignore
    bpy.ops.mesh.select_all(action='SELECT')  # type: ignore
    
    # Get bmesh representation for precise editing
    import bmesh
    if outer_bucket and hasattr(outer_bucket, 'data') and outer_bucket.data:  # type: ignore
        bm = bmesh.from_edit_mesh(outer_bucket.data)  # type: ignore
        
        # Select and scale top face (highest Z)
        bpy.ops.mesh.select_all(action='DESELECT')  # type: ignore
        for face in bm.faces:
            if all(v.co.z > 0 for v in face.verts):
                face.select = True
        
        bmesh.update_edit_mesh(outer_bucket.data)  # type: ignore
        bpy.ops.transform.resize(value=(bucket_size_top, bucket_size_top, 1))  # type: ignore
        
        # Select and scale bottom face (lowest Z)
        bpy.ops.mesh.select_all(action='DESELECT')  # type: ignore
        bm = bmesh.from_edit_mesh(outer_bucket.data)  # type: ignore
        for face in bm.faces:
            if all(v.co.z < 0 for v in face.verts):
                face.select = True
        
        bmesh.update_edit_mesh(outer_bucket.data)  # type: ignore
        bpy.ops.transform.resize(value=(bucket_size_bottom, bucket_size_bottom, 1))  # type: ignore
        
        # Scale the whole bucket to proper height
        bpy.ops.mesh.select_all(action='SELECT')  # type: ignore
        bpy.ops.transform.resize(value=(1, 1, bucket_height))  # type: ignore
    
    bpy.ops.object.mode_set(mode='OBJECT')  # type: ignore
    
    # Create inner bucket (slightly smaller for hollowing)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.0 + wall_thickness))  # type: ignore
    inner_bucket = bpy.context.active_object
    if inner_bucket:
        inner_bucket.name = "Inner_Bucket_Temp"
    
    # Make inner bucket smaller and shaped
    bpy.ops.object.mode_set(mode='EDIT')  # type: ignore
    bpy.ops.mesh.select_all(action='SELECT')  # type: ignore
    
    # Get bmesh for inner bucket
    if inner_bucket and hasattr(inner_bucket, 'data') and inner_bucket.data:  # type: ignore
        bm = bmesh.from_edit_mesh(inner_bucket.data)  # type: ignore
        
        # Select and scale top face
        bpy.ops.mesh.select_all(action='DESELECT')  # type: ignore
        for face in bm.faces:
            if all(v.co.z > 0 for v in face.verts):
                face.select = True
        
        bmesh.update_edit_mesh(inner_bucket.data)  # type: ignore
        bpy.ops.transform.resize(value=(bucket_size_top - wall_thickness, bucket_size_top - wall_thickness, 1))  # type: ignore
        
        # Select and scale bottom face
        bpy.ops.mesh.select_all(action='DESELECT')  # type: ignore
        bm = bmesh.from_edit_mesh(inner_bucket.data)  # type: ignore
        for face in bm.faces:
            if all(v.co.z < 0 for v in face.verts):
                face.select = True
        
        bmesh.update_edit_mesh(inner_bucket.data)  # type: ignore
        bpy.ops.transform.resize(value=(bucket_size_bottom - wall_thickness, bucket_size_bottom - wall_thickness, 1))  # type: ignore
        
        # Scale height (slightly shorter than outer)
        bpy.ops.mesh.select_all(action='SELECT')  # type: ignore
        bpy.ops.transform.resize(value=(1, 1, bucket_height - wall_thickness))  # type: ignore
    
    bpy.ops.object.mode_set(mode='OBJECT')  # type: ignore
    
    # Use boolean difference to hollow out the bucket
    if outer_bucket and inner_bucket:
        outer_bucket.select_set(True)
        bpy.context.view_layer.objects.active = outer_bucket
        
        # Add boolean modifier
        bool_mod = outer_bucket.modifiers.new(name="Boolean", type='BOOLEAN')  # type: ignore
        bool_mod.operation = 'DIFFERENCE'  # type: ignore
        bool_mod.object = inner_bucket  # type: ignore
        
        # Apply the modifier
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)  # type: ignore
        
        # Remove the inner bucket (no longer needed)
        bpy.data.objects.remove(inner_bucket)  # type: ignore
        
        # Rename to final name
        outer_bucket.name = "Sorting_Bucket"
        
        print(f"✅ Created hollow bucket with funnel shape using boolean operations")
        
        # Return the bucket object (no separate base needed)
        return outer_bucket, None
    
    return None, None

def main() -> None:
    """Main function to create the sorting bucket"""
    # Remove existing bucket objects and collections
    bucket_collection = bpy.data.collections.get("bucket")  # type: ignore
    if bucket_collection is not None:
        # Remove all objects in the bucket collection
        for obj in list(bucket_collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)  # type: ignore
        # Unlink and remove the collection itself
        if bucket_collection.name in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.unlink(bucket_collection)
        bpy.data.collections.remove(bucket_collection)

    # Create the bucket
    bucket, base = create_bucket()
    # Create a new collection and add the bucket to it
    bucket_collection = None
    if hasattr(bpy.data, "collections") and hasattr(bpy.data.collections, "new"):
        bucket_collection = bpy.data.collections.new("bucket")  # type: ignore
        # Link the new collection to the scene if not already linked
        if hasattr(bpy.context.scene, "collection") and hasattr(bpy.context.scene.collection, "children"):
            bpy.context.scene.collection.children.link(bucket_collection)
    # Move the bucket to the bucket collection
    if bucket is not None and bucket_collection is not None:
        for coll in list(bucket.users_collection):  # type: ignore
            coll.objects.unlink(bucket)
        bucket_collection.objects.link(bucket)
    
    if bucket is not None:
        print(f"✅ Created sorting bucket: {bucket.name}")

# Always run main when script is executed
main()
