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
import bmesh
from typing import Optional, Tuple, Any
from bpy.types import Mesh


def create_bucket() -> Tuple[Optional[Any], Optional[Any]]:
    """Create a hollow bucket with a base for sorting LEGO parts using boolean operations"""
    # Bucket dimensions in meters (24cm x 24cm square)
    bucket_size_top = 0.24  # 24cm square at top
    bucket_size_bottom = 0.06  # 6cm square at bottom (funnel exit)
    bucket_height = 0.20  # Reasonable height
    wall_thickness = 0.01  # 1cm thick walls

    # Create the outer bucket (frustum shape)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.15))
    outer_bucket = bpy.context.active_object
    if outer_bucket:
        outer_bucket.name = "Outer_Bucket_Temp"

    # Enter edit mode and modify to frustum shape
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")

    # Get bmesh representation for precise editing
    mesh_data: Optional[Mesh] = None
    if (
        outer_bucket
        and outer_bucket.data is not None
        and isinstance(outer_bucket.data, Mesh)
    ):
        mesh_data = outer_bucket.data

    if mesh_data is not None:
        bm = bmesh.from_edit_mesh(mesh_data)

        # Select and scale top face (highest Z)
        bpy.ops.mesh.select_all(action="DESELECT")
        for face in bm.faces:
            if all(v.co.z > 0 for v in face.verts):
                face.select = True
        bmesh.update_edit_mesh(mesh_data)
        bpy.ops.transform.resize(value=(bucket_size_top, bucket_size_top, 1))

        # Select and scale bottom face (lowest Z)
        bpy.ops.mesh.select_all(action="DESELECT")
        bm = bmesh.from_edit_mesh(mesh_data)
        for face in bm.faces:
            if all(v.co.z < 0 for v in face.verts):
                face.select = True
        bmesh.update_edit_mesh(mesh_data)
        bpy.ops.transform.resize(value=(bucket_size_bottom, bucket_size_bottom, 1))

        # Scale the whole bucket to proper height
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.transform.resize(value=(1, 1, bucket_height))

    bpy.ops.object.mode_set(mode="OBJECT")

    # Create inner bucket (slightly smaller for hollowing)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.15 + wall_thickness))
    inner_bucket = bpy.context.active_object
    if inner_bucket:
        inner_bucket.name = "Inner_Bucket_Temp"

    # Make inner bucket smaller and shaped
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")

    # Get bmesh for inner bucket
    inner_mesh: Optional[Mesh] = None
    if (
        inner_bucket
        and inner_bucket.data is not None
        and isinstance(inner_bucket.data, Mesh)
    ):
        inner_mesh = inner_bucket.data

    if inner_mesh is not None:
        bm = bmesh.from_edit_mesh(inner_mesh)

        # Select and scale top face
        bpy.ops.mesh.select_all(action="DESELECT")
        for face in bm.faces:
            if all(v.co.z > 0 for v in face.verts):
                face.select = True
        bmesh.update_edit_mesh(inner_mesh)
        bpy.ops.transform.resize(
            value=(
                bucket_size_top - wall_thickness,
                bucket_size_top - wall_thickness,
                1,
            )
        )

        # Select and scale bottom face
        bpy.ops.mesh.select_all(action="DESELECT")
        bm = bmesh.from_edit_mesh(inner_mesh)
        for face in bm.faces:
            if all(v.co.z < 0 for v in face.verts):
                face.select = True
        bmesh.update_edit_mesh(inner_mesh)
        bpy.ops.transform.resize(
            value=(
                bucket_size_bottom - wall_thickness,
                bucket_size_bottom - wall_thickness,
                1,
            )
        )

        # Scale height (slightly shorter than outer)
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.transform.resize(value=(1, 1, bucket_height - wall_thickness))

    bpy.ops.object.mode_set(mode="OBJECT")

    # Use boolean difference to hollow out the bucket
    if outer_bucket and inner_bucket:
        # ensure outer is active
        view_layer = bpy.context.view_layer
        if view_layer is not None and getattr(view_layer, "objects", None) is not None:
            try:
                view_layer.objects.active = outer_bucket
            except Exception:
                pass

        # Add boolean modifier
        try:
            bool_mod = outer_bucket.modifiers.new(name="Boolean", type="BOOLEAN")
            # Use a loosely-typed reference to avoid static attribute errors
            from typing import Any, cast

            bool_mod_any: Any = cast(Any, bool_mod)

            bool_mod_any.operation = "DIFFERENCE"
            bool_mod_any.object = inner_bucket

            # Apply the modifier
            bpy.ops.object.modifier_apply(modifier=bool_mod.name)

            # Remove the inner bucket (no longer needed)
            try:
                bpy.data.objects.remove(inner_bucket)
            except Exception:
                pass

            # Rename to final name (guard in case active object changed)
            try:
                outer_bucket.name = "Sorting_Bucket"
            except Exception:
                pass

            # Apply transforms and ensure normals are correct so collisions align
            try:
                if view_layer and getattr(view_layer, "objects", None) is not None:
                    try:
                        view_layer.objects.active = outer_bucket
                    except Exception:
                        pass
                outer_bucket.select_set(True)
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                # Recalculate normals outside
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.object.mode_set(mode="OBJECT")
                # Set origin to geometry to align pivot/collision
                bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="MEDIAN")
            except Exception:
                pass

            print(
                f"✅ Created hollow bucket with funnel shape using boolean operations"
            )

            # Create an internal collider: a slightly scaled-down duplicate to act as reliable collision geometry
            collider = None
            try:
                if not outer_bucket:
                    raise RuntimeError("No outer bucket to duplicate for collider")
                collider = outer_bucket.copy()
                try:
                    data_obj = outer_bucket.data
                    if data_obj is not None:
                        try:
                            collider.data = data_obj.copy()
                        except Exception:
                            pass
                except Exception:
                    pass
                collider.name = "Sorting_Bucket_Collider"
                # Slightly scale down to ensure it's fully inside the visible bucket
                try:
                    collider.scale = (0.995, 0.995, 0.995)
                except Exception:
                    pass

                # Link collider into the active collection or scene collection
                try:
                    scene = bpy.context.scene
                    try:
                        if scene is not None and scene.collection is not None:
                            scene.collection.objects.link(collider)
                        else:
                            # fallback to context.collection
                            ctx_coll = bpy.context.collection
                            if ctx_coll is not None:
                                ctx_coll.objects.link(collider)
                    except Exception:
                        pass
                except Exception:
                    pass

                # Make collider passive rigid body with mesh collider and zero margin
                # Make collider passive rigid body with mesh collider and zero margin
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
                try:
                    bpy.ops.rigidbody.object_add(type="PASSIVE")
                except Exception:
                    pass
                rb = getattr(collider, "rigid_body", None)
                if rb is None:
                    raise Exception("Rigid body not assigned")

                rb.use_margin = True
                rb.collision_margin = 0.0
                rb.friction = 0.8

            except Exception:
                collider = None

            return outer_bucket, collider
        except Exception:
            # If anything in the boolean step fails, ensure a clean return
            return None, None

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
