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

def create_bucket():
    """Create a hollow bucket with a base for sorting LEGO parts"""
    # Create outer cylinder
    bpy.ops.mesh.primitive_cylinder_add(radius=2, depth=5, location=(0, 0, 0))
    outer_bucket = bpy.context.active_object
    if outer_bucket is not None:
        outer_bucket.name = "Outer Bucket"

    # Create inner cylinder (to hollow out the bucket)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=6, location=(0, 0, 0))
    inner_bucket = bpy.context.active_object
    if inner_bucket is not None:
        inner_bucket.name = "Inner Bucket"

    # Add boolean modifier to outer cylinder
    if outer_bucket is not None and inner_bucket is not None:
        bool_modifier = outer_bucket.modifiers.new(name="Bucket", type='BOOLEAN')  # type: ignore
        bool_modifier.operation = 'DIFFERENCE'
        bool_modifier.object = inner_bucket

    if outer_bucket is not None:
        bpy.context.view_layer.objects.active = outer_bucket

    # Apply the boolean modifier, this makes the subtraction permanent
    if outer_bucket is not None:
        bpy.ops.object.modifier_apply(modifier="Bucket")
    
    # Remove the inner cylinder object after applying the modifier
    if inner_bucket is not None:
        bpy.data.objects.remove(inner_bucket)

    # Create the base of the bucket
    bpy.ops.mesh.primitive_circle_add(radius=2, enter_editmode=False, align='WORLD', location=(0, 0, -2.5), rotation=(0, 0, 0))
    base = bpy.context.active_object
    if base is not None:
        base.name = "Bucket Base"
        bpy.context.view_layer.objects.active = base
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.fill()
        bpy.ops.object.mode_set(mode='OBJECT')
    # Return both objects so they can be added to the collection before joining
    return outer_bucket, base

def main():
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
    outer_bucket, base = create_bucket()
    # Create a new collection and add both objects to it
    bucket_collection = None
    if hasattr(bpy.data, "collections") and hasattr(bpy.data.collections, "new"):
        bucket_collection = bpy.data.collections.new("bucket")  # type: ignore
        # Link the new collection to the scene if not already linked
        if hasattr(bpy.context.scene, "collection") and hasattr(bpy.context.scene.collection, "children"):
            bpy.context.scene.collection.children.link(bucket_collection)
    # Move both objects to the bucket collection
    for obj in [outer_bucket, base]:
        if obj is not None and bucket_collection is not None:
            for coll in list(obj.users_collection):  # type: ignore
                coll.objects.unlink(obj)
            bucket_collection.objects.link(obj)
    # Now join the base with the bucket
    joined_bucket = outer_bucket
    if outer_bucket is not None and base is not None:
        bpy.context.view_layer.objects.active = outer_bucket
        base.select_set(True)
        bpy.ops.object.join()
        joined_bucket = bpy.context.active_object
    if joined_bucket is not None:
        joined_bucket.name = "Sorting_Bucket"
    if joined_bucket is not None:
        print(f"✅ Created sorting bucket: {joined_bucket.name}")

# Always run main when script is executed
main()
