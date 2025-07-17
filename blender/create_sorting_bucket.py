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
    outer_bucket.name = "Outer Bucket"

    # Create inner cylinder (to hollow out the bucket)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=6, location=(0, 0, 0))
    inner_bucket = bpy.context.active_object
    inner_bucket.name = "Inner Bucket"

    # Add boolean modifier to outer cylinder
    bool_modifier = outer_bucket.modifiers.new(name="Bucket", type='BOOLEAN')
    bool_modifier.operation = 'DIFFERENCE'
    bool_modifier.object = inner_bucket

    bpy.context.view_layer.objects.active = outer_bucket

    # Apply the boolean modifier, this makes the subtraction permanent
    bpy.ops.object.modifier_apply(modifier=bool_modifier.name)
    
    # Remove the inner cylinder object after applying the modifier
    bpy.data.objects.remove(inner_bucket)

    # Create the base of the bucket
    bpy.ops.mesh.primitive_circle_add(radius=2, enter_editmode=False, align='WORLD', location=(0, 0, -2.5), rotation=(0, 0, 0))
    base = bpy.context.active_object
    base.name = "Bucket Base"
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.fill()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Join the base with the bucket
    bpy.context.view_layer.objects.active = outer_bucket
    base.select_set(True)
    bpy.ops.object.join()
    
    # Return the created bucket
    return outer_bucket

def main():
    """Main function to create the sorting bucket"""
    # Create the bucket
    bucket = create_bucket()
    bucket.name = "Sorting_Bucket"

    # Create a new collection and add the bucket object to it
    bucket_collection = bpy.data.collections.new("bucket")
    bpy.context.collection.children.link(bucket_collection)
    bucket_collection.objects.link(bucket)
    
    print(f"✅ Created sorting bucket: {bucket.name}")

# Always run main when script is executed
main()
