#!/usr/bin/env python3
"""
Blender script to create a sorting bucket with side exit mechanism.

Architecture:
- OPEN-TOP funnel bucket (parts fall in from above)
- Solid bottom with rectangular exit opening on the side
- Sliding gate to control opening size (slides VERTICALLY)
- Inclined internal floor to guide parts toward exit

The bucket is designed to receive LEGO parts from above and release them
one-by-one onto a conveyor belt positioned at the exit opening.

Usage:
- Run this script in Blender to create a bucket object
- The bucket will be added to a 'bucket' collection
- Previous bucket objects will be cleared before creating a new one
"""

import bpy
import bmesh
from typing import Optional, Tuple, Any, cast


# ============================================================================
# Configuration Constants
# ============================================================================

# Bucket dimensions (meters)
BUCKET_TOP_RADIUS = 0.12  # 12cm radius at top (24cm diameter)
BUCKET_BOTTOM_RADIUS = 0.06  # 6cm radius at bottom (12cm diameter)
BUCKET_HEIGHT = 0.18  # 18cm tall
WALL_THICKNESS = 0.008  # 8mm walls

# Exit opening dimensions (LARGE for parts to exit onto conveyor)
EXIT_WIDTH = 0.10  # 10cm wide (fits multiple LEGO bricks)
EXIT_HEIGHT = 0.08  # 8cm tall (large opening for parts to fall through)
EXIT_Z_OFFSET = 0.01  # 1cm above bucket bottom

# Gate/slider dimensions (slides VERTICALLY)
GATE_THICKNESS = 0.005  # 5mm thick gate
GATE_SLIDE_RANGE = 0.06  # Extra height for vertical slide range

# Internal ramp
RAMP_ANGLE = 8  # degrees - guides parts to exit


def ensure_material(
    name: str,
    rgba: Tuple[float, float, float, float],
    roughness: float = 0.5,
    metallic: float = 0.0,
) -> Any:
    """Create or get a simple material."""
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        node_tree = mat.node_tree
        if node_tree:
            nodes = node_tree.nodes
            nodes.clear()
            bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
            output = nodes.new(type="ShaderNodeOutputMaterial")
            bsdf.location = (-200, 0)
            output.location = (0, 0)
            node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    node_tree = mat.node_tree
    if node_tree:
        bsdf = node_tree.nodes.get("Principled BSDF")
        if bsdf:
            base = bsdf.inputs.get("Base Color")
            if base:
                cast(Any, base).default_value = rgba
            rough = bsdf.inputs.get("Roughness")
            if rough:
                cast(Any, rough).default_value = roughness
            met = bsdf.inputs.get("Metallic")
            if met:
                cast(Any, met).default_value = metallic
    return mat


def assign_material(obj: Any, mat: Any) -> None:
    """Assign material to object."""
    if not obj or not hasattr(obj, "data") or obj.data is None:
        return
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def set_active(obj: Any) -> None:
    """Set object as active in view layer."""
    view_layer = bpy.context.view_layer
    if view_layer and hasattr(view_layer, "objects"):
        try:
            view_layer.objects.active = obj
        except Exception:
            pass


def create_bucket() -> Tuple[Optional[Any], Optional[Any], Optional[Any]]:
    """Create an open-top funnel bucket with side exit for sorting LEGO parts.

    Uses bmesh to reliably remove the top face, creating a true funnel shape.
    Bottom is SOLID (closed mesh) so parts don't fall through.
    Exit is a clean rectangular opening cut from the side.

    Returns:
        Tuple of (bucket, gate, ramp) objects
    """
    # Create outer cone (funnel shape) - with both ends filled initially
    bpy.ops.mesh.primitive_cone_add(
        vertices=32,
        radius1=BUCKET_BOTTOM_RADIUS,
        radius2=BUCKET_TOP_RADIUS,
        depth=BUCKET_HEIGHT,
        end_fill_type="NGON",
        location=(0, 0, BUCKET_HEIGHT / 2),
    )
    bucket = bpy.context.active_object
    if not bucket:
        print("❌ Failed to create bucket")
        return None, None, None

    bucket.name = "Sorting_Bucket"

    # Delete ONLY top face using bmesh - keep bottom CLOSED!
    set_active(bucket)
    bucket.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    mesh_data = bucket.data
    if isinstance(mesh_data, bpy.types.Mesh):
        bm = bmesh.from_edit_mesh(mesh_data)
        bm.faces.ensure_lookup_table()

        if bm.faces:
            # Find top face (highest Z) - only remove this one, keep bottom!
            top_z = max(f.calc_center_median().z for f in bm.faces)

            faces_to_delete = [
                f for f in bm.faces if abs(f.calc_center_median().z - top_z) < 0.001
            ]
            for f in faces_to_delete:
                bm.faces.remove(f)
            bmesh.update_edit_mesh(mesh_data)
            print(f"✅ Removed top face only (open top, CLOSED bottom)")

    bpy.ops.object.mode_set(mode="OBJECT")

    # Add solidify modifier for wall thickness - creates inner walls
    # offset=1.0 means walls grow inward, keeping bottom solid
    solidify = bucket.modifiers.new(name="Solidify", type="SOLIDIFY")
    solidify_any: Any = cast(Any, solidify)
    solidify_any.thickness = WALL_THICKNESS
    solidify_any.offset = 1.0
    solidify_any.use_rim = True  # Close edges where solidify creates gaps
    solidify_any.use_rim_only = False
    bpy.ops.object.modifier_apply(modifier=solidify.name)

    # Create the exit hole cutter - a rectangular box that cuts STRAIGHT through
    # Position it so it creates a clean rectangular opening when viewed from side
    exit_z = EXIT_Z_OFFSET + EXIT_HEIGHT / 2

    # The cutter needs to be long enough to go through the entire bucket wall
    # and positioned at the bucket's edge
    cutter_depth = BUCKET_BOTTOM_RADIUS * 2  # Long enough to cut through

    bpy.ops.mesh.primitive_cube_add(size=1, location=(BUCKET_BOTTOM_RADIUS, 0, exit_z))
    cutter = bpy.context.active_object
    if cutter:
        cutter.name = "Exit_Hole_Cutter"
        # Make cutter deep enough to go through, and sized for rectangle
        cutter.scale = (cutter_depth, EXIT_WIDTH, EXIT_HEIGHT)
        bpy.ops.object.transform_apply(scale=True)

        set_active(bucket)
        bool_mod = bucket.modifiers.new(name="ExitHole", type="BOOLEAN")
        bool_any: Any = cast(Any, bool_mod)
        bool_any.operation = "DIFFERENCE"
        bool_any.object = cutter
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)
        bpy.data.objects.remove(cutter, do_unlink=True)

    # Clean up mesh
    set_active(bucket)
    bucket.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="MEDIAN")

    # Apply material
    bucket_mat = ensure_material(
        "Bucket_Material", (0.7, 0.7, 0.75, 1.0), roughness=0.4, metallic=0.3
    )
    assign_material(bucket, bucket_mat)

    print(
        f"✅ Created bucket with rectangular exit ({EXIT_WIDTH * 100:.0f}x{EXIT_HEIGHT * 100:.0f}cm)"
    )
    print(f"✅ Bucket bottom is CLOSED - no separate floor needed")

    # No separate floor/ramp - bucket mesh bottom handles collision
    return bucket, None, None


def setup_physics(
    obj: Any,
    shape: str = "MESH",
    friction: float = 0.8,
    kinematic: bool = False,
    margin: float = 0.001,
) -> None:
    """Setup rigid body physics for an object."""
    if not obj:
        return
    set_active(obj)
    obj.select_set(True)
    try:
        bpy.ops.rigidbody.object_add(type="PASSIVE")
        rb = obj.rigid_body
        if rb:
            rb.collision_shape = shape
            rb.friction = friction
            rb.use_margin = True
            rb.collision_margin = margin
            rb.kinematic = kinematic
    except Exception:
        pass


def animate_gate(gate: Any, open_amount: float = 1.0) -> None:
    """Create keyframe animation for gate sliding open (vertically UP)."""
    if not gate:
        return

    # Gate slides UP to open (on Z-axis)
    slide_distance = EXIT_HEIGHT * open_amount
    scene = bpy.context.scene
    if not scene:
        return

    scene.frame_set(1)
    gate.location.z = EXIT_Z_OFFSET + EXIT_HEIGHT / 2  # Closed position
    gate.keyframe_insert(data_path="location", index=2)  # Z-axis

    scene.frame_set(50)
    gate.location.z = EXIT_Z_OFFSET + EXIT_HEIGHT / 2 + slide_distance  # Open position
    gate.keyframe_insert(data_path="location", index=2)

    scene.frame_set(100)
    gate.location.z = EXIT_Z_OFFSET + EXIT_HEIGHT / 2 + slide_distance  # Stay open
    gate.keyframe_insert(data_path="location", index=2)

    scene.frame_set(1)
    print(f"✅ Animated gate (slides UP {slide_distance * 100:.1f}cm over 50 frames)")


def main() -> None:
    """Main function to create the sorting bucket with side exit."""
    print("=" * 60)
    print("🏗️  Creating Sorting Bucket (Side Exit Design)")
    print("=" * 60)

    # Remove existing bucket objects and collections
    bucket_collection = bpy.data.collections.get("bucket")
    if bucket_collection is not None:
        for obj in list(bucket_collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        scene = bpy.context.scene
        if scene and getattr(scene, "collection", None) is not None:
            try:
                if bucket_collection.name in scene.collection.children:
                    scene.collection.children.unlink(bucket_collection)
            except Exception:
                pass
        bpy.data.collections.remove(bucket_collection)

    # Create the bucket components
    bucket, gate, ramp = create_bucket()

    # Create collection
    bucket_collection = bpy.data.collections.new("bucket")
    scene = bpy.context.scene
    if scene:
        scene.collection.children.link(bucket_collection)

    # Collect all bucket objects (including rails)
    objects_to_add = [bucket, gate, ramp]
    rail_left = bpy.data.objects.get("Gate_Rail_Left")
    rail_right = bpy.data.objects.get("Gate_Rail_Right")
    if rail_left:
        objects_to_add.append(rail_left)
    if rail_right:
        objects_to_add.append(rail_right)

    # Move objects to bucket collection
    for obj in objects_to_add:
        if obj:
            for coll in list(obj.users_collection):
                coll.objects.unlink(obj)
            bucket_collection.objects.link(obj)

    # Setup physics - bucket needs MESH collision with higher margin for thin shells
    setup_physics(
        bucket, "MESH", friction=0.8, margin=0.01
    )  # 1cm margin for reliability
    # Gate not used currently
    if gate:
        setup_physics(gate, "BOX", friction=0.5, kinematic=True)

    # Bucket bottom collision was removed - bucket floor is already solid

    # Animate gate (if exists)
    animate_gate(gate, open_amount=1.0)

    print("=" * 60)
    print("✅ Sorting Bucket created successfully!")
    print("=" * 60)
    print(f"   Exit opening: {EXIT_WIDTH * 100:.0f}cm × {EXIT_HEIGHT * 100:.0f}cm")
    print(f"   Exit height:  {EXIT_Z_OFFSET * 100:.0f}cm from bottom")
    print(f"   Gate slides VERTICALLY (up/down) to control opening")
    print(f"   Bucket is OPEN at top for loading parts")
    print("=" * 60)


# Always run main when script is executed
main()
