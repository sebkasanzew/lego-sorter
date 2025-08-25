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
from typing import Optional, Tuple, Any, cast

def create_bucket() -> Tuple[Optional[Any], Optional[Any]]:
    """Create a hollow bucket with a base for sorting LEGO parts using boolean operations"""
    # Bucket dimensions in meters (24cm x 24cm square)
    bucket_size_top = 0.24  # 24cm square at top
    bucket_size_bottom = 0.06  # 6cm square at bottom (funnel exit)
    bucket_height = 0.20  # Reasonable height
    wall_thickness = 0.01  # 1cm thick walls

    # Create the outer bucket (frustum shape)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.15))  # type: ignore
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
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.15 + wall_thickness))  # type: ignore
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
        # ensure outer is active
        try:
            view_layer = bpy.context.view_layer
            if view_layer and getattr(view_layer, 'objects', None) is not None:
                try:
                    view_layer.objects.active = outer_bucket
                except Exception:
                    pass
        except Exception:
            pass

        # Add boolean modifier
        try:
            bool_mod = outer_bucket.modifiers.new(name="Boolean", type='BOOLEAN')  # type: ignore
            bool_mod.operation = 'DIFFERENCE'  # type: ignore
            bool_mod.object = inner_bucket  # type: ignore

            # Apply the modifier
            bpy.ops.object.modifier_apply(modifier=bool_mod.name)  # type: ignore

            # Remove the inner bucket (no longer needed)
            try:
                bpy.data.objects.remove(inner_bucket)  # type: ignore
            except Exception:
                pass

            # Rename to final name (guard in case active object changed)
            try:
                outer_bucket.name = "Sorting_Bucket"
            except Exception:
                pass

            # Apply transforms and ensure normals are correct so collisions align
            try:
                if view_layer and getattr(view_layer, 'objects', None) is not None:
                    try:
                        view_layer.objects.active = outer_bucket
                    except Exception:
                        pass
                outer_bucket.select_set(True)
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                # Recalculate normals outside
                bpy.ops.object.mode_set(mode='EDIT')  # type: ignore
                bpy.ops.mesh.normals_make_consistent(inside=False)  # type: ignore
                bpy.ops.object.mode_set(mode='OBJECT')  # type: ignore
                # Set origin to geometry to align pivot/collision
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')  # type: ignore
            except Exception:
                pass

            print(f"✅ Created hollow bucket with funnel shape using boolean operations")

            # Create an internal collider: a slightly scaled-down duplicate to act as reliable collision geometry
            collider = None
            try:
                if not outer_bucket:
                    raise RuntimeError("No outer bucket to duplicate for collider")
                collider = outer_bucket.copy()
                try:
                    collider.data = outer_bucket.data.copy()  # type: ignore[attr-defined]
                except Exception:
                    pass
                collider.name = 'Sorting_Bucket_Collider'
                # Slightly scale down to ensure it's fully inside the visible bucket
                try:
                    collider.scale = (0.995, 0.995, 0.995)
                except Exception:
                    pass

                # Link collider into the active collection or scene collection
                try:
                    scene = bpy.context.scene
                    if scene is not None and getattr(scene, 'collection', None) is not None:
                        scene.collection.objects.link(collider)
                    else:
                        # fallback to context.collection
                        ctx_coll = getattr(bpy.context, 'collection', None)
                        if ctx_coll is not None:
                            ctx_coll.objects.link(collider)
                except Exception:
                    pass

                # Make collider passive rigid body with mesh collider and zero margin
                try:
                    view_layer = bpy.context.view_layer
                    if view_layer and getattr(view_layer, 'objects', None) is not None:
                        try:
                            view_layer.objects.active = collider
                        except Exception:
                            pass
                    collider.select_set(True)
                    bpy.ops.rigidbody.object_add(type='PASSIVE')  # type: ignore
                    collider.rigid_body.collision_shape = 'MESH'  # type: ignore
                    try:
                        collider.rigid_body.use_margin = True  # type: ignore
                        collider.rigid_body.collision_margin = 0.0  # type: ignore
                    except Exception:
                        pass
                    try:
                        collider.rigid_body.friction = 0.8  # type: ignore
                    except Exception:
                        pass
                except Exception:
                    pass
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
    bucket_collection = bpy.data.collections.get("bucket")  # type: ignore
    if bucket_collection is not None:
        # Remove all objects in the bucket collection
        for obj in list(bucket_collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)  # type: ignore
        # Unlink and remove the collection itself
        scene = getattr(bpy.context, 'scene', None)
        if scene and getattr(scene, 'collection', None) is not None:
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
    if hasattr(bpy.data, "collections") and hasattr(bpy.data.collections, "new"):
        bucket_collection = bpy.data.collections.new("bucket")  # type: ignore
        # Link the new collection to the scene if not already linked
        scene = getattr(bpy.context, 'scene', None)
        if scene and hasattr(scene, "collection") and hasattr(scene.collection, "children"):
            try:
                scene.collection.children.link(bucket_collection)
            except Exception:
                pass
    # Move the bucket to the bucket collection
    if bucket is not None and bucket_collection is not None:
        for coll in list(bucket.users_collection):  # type: ignore
            coll.objects.unlink(bucket)
        bucket_collection.objects.link(bucket)
    
    if bucket is not None:
        print(f"✅ Created sorting bucket: {bucket.name}")
        # Ensure bucket has correct collision properties when script runs standalone
        try:
            view_layer = getattr(bpy.context, 'view_layer', None)
            if view_layer and getattr(view_layer, 'objects', None) is not None:
                try:
                    view_layer.objects.active = bucket
                except Exception:
                    pass
            bucket.select_set(True)
            # Add passive rigid body if not present to help animate_lego_physics attach correct settings
            if not getattr(bucket, 'rigid_body', None):
                bpy.ops.rigidbody.object_add(type='PASSIVE')  # type: ignore
                bucket.rigid_body.collision_shape = 'MESH'  # type: ignore
                # small margin helps prevent floating due to solver tolerances
                try:
                    bucket.rigid_body.use_margin = True  # type: ignore
                    bucket.rigid_body.collision_margin = 0.001  # 1mm margin
                except Exception:
                    pass
        except Exception:
            pass

# Always run main when script is executed
main()
