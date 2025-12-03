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


def create_bucket() -> Tuple[Optional[Any], Optional[Any]]:
    """Create an open-bottom funnel bucket for sorting LEGO parts.

    The bucket has a wide top opening, narrows to a funnel, and has an
    open bottom hole where parts can fall through onto the conveyor belt.
    """
    # Bucket dimensions in meters
    bucket_size_top = 0.24  # 24cm square at top
    bucket_size_bottom = 0.08  # 8cm square at bottom (exit hole size)
    bucket_height = 0.18  # Height of bucket
    wall_thickness = 0.01  # 1cm thick walls

    # Create the outer bucket shell (frustum/funnel shape)
    bpy.ops.mesh.primitive_cone_add(
        vertices=32,
        radius1=bucket_size_bottom / 2,  # Bottom radius (smaller)
        radius2=bucket_size_top / 2,  # Top radius (larger)
        depth=bucket_height,
        end_fill_type="NOTHING",  # Open top and bottom!
        location=(0, 0, 0.15),
    )
    outer_bucket = bpy.context.active_object
    if outer_bucket:
        outer_bucket.name = "Sorting_Bucket_Temp"

    # Add solidify modifier to give walls thickness
    if outer_bucket:
        solidify_mod = outer_bucket.modifiers.new(name="Solidify", type="SOLIDIFY")
        from typing import Any, cast

        solidify_any: Any = cast(Any, solidify_mod)
        solidify_any.thickness = wall_thickness
        solidify_any.offset = 1.0  # Offset outward

        # Apply the solidify modifier
        bpy.ops.object.modifier_apply(modifier=solidify_mod.name)

        # Rename to final name
        outer_bucket.name = "Sorting_Bucket"

        # Apply transforms and fix normals
        view_layer = bpy.context.view_layer
        if view_layer and getattr(view_layer, "objects", None) is not None:
            try:
                view_layer.objects.active = outer_bucket
            except Exception:
                pass
        outer_bucket.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Recalculate normals
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")

        # Set origin to geometry
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="MEDIAN")

        print(
            f"✅ Created open-bottom funnel bucket (exit hole: {bucket_size_bottom * 100:.0f}cm)"
        )

        # Create an internal collider for physics
        collider = None
        try:
            collider = outer_bucket.copy()
            if outer_bucket.data is not None:
                try:
                    collider.data = outer_bucket.data.copy()
                except Exception:
                    pass
            collider.name = "Sorting_Bucket_Collider"
            collider.scale = (0.995, 0.995, 0.995)

            # Link collider into scene
            scene = bpy.context.scene
            if scene is not None and scene.collection is not None:
                scene.collection.objects.link(collider)

            # Make collider passive rigid body
            view_layer = bpy.context.view_layer
            if (
                view_layer is not None
                and getattr(view_layer, "objects", None) is not None
            ):
                try:
                    view_layer.objects.active = collider
                except Exception:
                    pass
            collider.select_set(True)
            bpy.ops.rigidbody.object_add(type="PASSIVE")
            rb = getattr(collider, "rigid_body", None)
            if rb:
                rb.collision_shape = "MESH"
                rb.use_margin = True
                rb.collision_margin = 0.0
                rb.friction = 0.8

        except Exception as e:
            print(f"⚠️ Failed to create collider: {e}")
            collider = None

        return outer_bucket, collider

    return None, None


def main() -> None:
    """Main function to create the sorting bucket"""
    # Remove existing bucket objects and collections
    bucket_collection = bpy.data.collections.get("bucket")
    if bucket_collection is not None:
        # Remove all objects in the bucket collection
        for obj in list(bucket_collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        # Unlink and remove the collection itself
        scene = bpy.context.scene
        if scene and getattr(scene, "collection", None) is not None:
            try:
                if bucket_collection.name in scene.collection.children:
                    scene.collection.children.unlink(bucket_collection)
            except Exception:
                pass
        bpy.data.collections.remove(bucket_collection)

    # Create the bucket
    bucket, base = create_bucket()
    # Create a new collection and add the bucket to it
    bucket_collection = None
    try:
        bucket_collection = bpy.data.collections.new("bucket")
        # Link the new collection to the scene if not already linked
        scene = bpy.context.scene
        if scene is not None:
            try:
                scene.collection.children.link(bucket_collection)
            except Exception:
                pass
    except Exception:
        bucket_collection = None
    # Move the bucket to the bucket collection
    if bucket is not None and bucket_collection is not None:
        for coll in list(bucket.users_collection):
            coll.objects.unlink(bucket)
        bucket_collection.objects.link(bucket)

    if bucket is not None:
        print(f"✅ Created sorting bucket: {bucket.name}")
        # Ensure bucket has correct collision properties when script runs standalone
        view_layer = bpy.context.view_layer
        if view_layer is not None and getattr(view_layer, "objects", None) is not None:
            try:
                view_layer.objects.active = bucket
            except Exception:
                pass
        try:
            bucket.select_set(True)
        except Exception:
            pass
        # Add passive rigid body if not present to help animate_lego_physics attach correct settings
        try:
            if not getattr(bucket, "rigid_body", None):
                try:
                    bpy.ops.rigidbody.object_add(type="PASSIVE")
                except Exception:
                    pass
        except Exception:
            pass
        try:
            rb = getattr(bucket, "rigid_body", None)
            if rb is not None:
                try:
                    rb.collision_shape = "MESH"
                except Exception:
                    pass
                try:
                    rb.use_margin = True
                except Exception:
                    pass
                try:
                    rb.collision_margin = 0.001  # 1mm margin
                except Exception:
                    pass
        except Exception:
            pass


# Always run main when script is executed
main()
