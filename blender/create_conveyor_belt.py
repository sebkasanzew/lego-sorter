#!/usr/bin/env python3
"""
Blender script to create a conveyor belt with animated slats.

The conveyor belt is designed to:
- Start INSIDE the bucket so LEGO parts fall onto the slats
- Transport parts along an inclined surface using moving slats
- Slats follow a looping path (top surface -> end -> bottom -> start)

Architecture:
- BEZIER curve path defines the conveyor loop
- Direct keyframe animation for each slat (500 frames per cycle)
- Kinematic rigid bodies for physics interaction with LEGO parts
- Arc-length parameterization ensures uniform slat speed
"""

import bpy
import math
from typing import Optional, Any, Tuple, List, cast
from mathutils import Vector


# ============================================================================
# Configuration Constants
# ============================================================================

# Conveyor geometry (meters)
# Belt starts well inside bucket to catch falling parts
CONVEYOR_START_X = -0.10  # Start inside bucket area (moved from 0.08)
CONVEYOR_START_Z = 0.02  # At internal ramp height
CONVEYOR_END_X = 0.45  # End past bucket wall
CONVEYOR_RISE = 0.12  # Z rise over length (incline)
SLAT_GAP = 0.03  # Gap between top and bottom belt surfaces

# Slat dimensions - sized to overlap each other with no gaps
SLAT_WIDTH = 0.08  # 8cm wide (Y direction) - spans ramp width
SLAT_THICKNESS = 0.10  # 10cm thick (X direction) - overlap ensures no gaps
SLAT_HEIGHT = 0.02  # 2cm tall (Z direction) - catches/pushes bricks

# Animation
SLAT_COUNT = 12  # Number of slats around the loop
ANIMATION_FRAMES = 500  # Frames for one complete loop

# Legacy constants (for compatibility)
CONVEYOR_WIDTH = SLAT_WIDTH
CONVEYOR_LENGTH = CONVEYOR_END_X - CONVEYOR_START_X
CONVEYOR_THICKNESS = SLAT_HEIGHT
CONVEYOR_INCLINE = math.degrees(math.atan2(CONVEYOR_RISE, CONVEYOR_LENGTH))

# Bucket dimensions (must match create_sorting_bucket.py)
BUCKET_BOTTOM_RADIUS = 0.06
BUCKET_WALL_THICKNESS = 0.008
EXIT_Z_OFFSET = 0.02
EXIT_HEIGHT = 0.05


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
        if node_tree is None:
            return mat
        nodes = node_tree.nodes
        nodes.clear()
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        output = nodes.new(type="ShaderNodeOutputMaterial")
        bsdf.location = (-200, 0)
        output.location = (0, 0)
        node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    node_tree = mat.node_tree
    if node_tree is None:
        return mat
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


def ensure_collection(name: str) -> Any:
    """Get or create a collection by name."""
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        scene = bpy.context.scene
        if scene and scene.collection:
            scene.collection.children.link(collection)
    return collection


def clear_conveyor_objects() -> None:
    """Remove ALL existing conveyor-related objects."""
    conveyor_collection = bpy.data.collections.get("conveyor_belt")
    if conveyor_collection:
        for obj in list(conveyor_collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        try:
            scene = bpy.context.scene
            if scene and scene.collection:
                scene.collection.children.unlink(conveyor_collection)
        except Exception:
            pass
        bpy.data.collections.remove(conveyor_collection)

    to_remove = []
    for obj in bpy.data.objects:
        if any(x in obj.name for x in ["Conveyor_", "Slat_", "Belt_"]):
            to_remove.append(obj)
    for obj in to_remove:
        bpy.data.objects.remove(obj, do_unlink=True)

    print(f"✓ Cleared {len(to_remove)} conveyor objects")


def create_conveyor_path() -> Tuple[List[Vector], List[float]]:
    """Calculate control points for the conveyor belt loop.

    The path forms a rectangle with 4 corners:
    - Top surface: slats move from bucket toward end (carrying parts)
    - End: slats transition to bottom (return path)
    - Bottom surface: slats return toward bucket
    - Start: slats transition back to top surface

    Uses arc-length parameterization for uniform slat speed.

    Returns:
        Tuple of (control_points, cumulative_normalized_lengths)
    """
    # Path geometry from configuration
    end_z = CONVEYOR_START_Z + CONVEYOR_RISE

    # 4 corners of the loop (rectangular path)
    p0 = Vector((CONVEYOR_START_X, 0, CONVEYOR_START_Z))  # Top-Start (inside bucket)
    p1 = Vector((CONVEYOR_END_X, 0, end_z))  # Top-End
    p2 = Vector((CONVEYOR_END_X, 0, end_z - SLAT_GAP))  # Bottom-End
    p3 = Vector((CONVEYOR_START_X, 0, CONVEYOR_START_Z - SLAT_GAP))  # Bottom-Start

    control_points = [p0, p1, p2, p3]

    # Calculate segment lengths for arc-length parameterization
    n_pts = len(control_points)
    segment_lengths: List[float] = []
    for i in range(n_pts):
        p_start = control_points[i]
        p_end = control_points[(i + 1) % n_pts]
        segment_lengths.append((p_end - p_start).length)

    total_length = sum(segment_lengths)

    cumulative = [0.0]
    for sl in segment_lengths:
        cumulative.append(cumulative[-1] + sl)
    cumulative_normalized = [c / total_length for c in cumulative]

    print(f"  Path: X from {CONVEYOR_START_X:.2f} to {CONVEYOR_END_X:.2f}")
    print(f"  Path: Z from {CONVEYOR_START_Z:.2f} to {end_z:.2f}")
    print(f"  Path segments: {[f'{sl:.3f}m' for sl in segment_lengths]}")
    print(f"  Total path length: {total_length:.3f}m")

    return control_points, cumulative_normalized


def sample_path_position(
    control_points: List[Vector],
    cumulative_normalized: List[float],
    offset: float,
) -> Vector:
    """Sample position along the path at given offset (0-1).

    Uses arc-length parameterization for uniform speed.

    Args:
        control_points: List of path corner positions
        cumulative_normalized: Normalized cumulative lengths
        offset: Position along path (0=start, 1=full loop)

    Returns:
        World-space position Vector
    """
    offset = offset % 1.0
    n_pts = len(control_points)

    seg_idx = 0
    for i in range(n_pts):
        if offset < cumulative_normalized[i + 1]:
            seg_idx = i
            break
    else:
        seg_idx = n_pts - 1

    seg_start = cumulative_normalized[seg_idx]
    seg_end = cumulative_normalized[seg_idx + 1]
    seg_range = seg_end - seg_start
    seg_t = (offset - seg_start) / seg_range if seg_range > 0 else 0.0

    p0 = control_points[seg_idx]
    p1 = control_points[(seg_idx + 1) % n_pts]

    return p0.lerp(p1, seg_t)


# Conveyor incline angle (calculated from rise/run)
# Negative because slats should tilt opposite to belt direction (perpendicular to surface)
CONVEYOR_INCLINE_RAD = -math.atan2(CONVEYOR_RISE, CONVEYOR_END_X - CONVEYOR_START_X)


def create_side_walls(conveyor_collection: Any) -> List[Any]:
    """Create side walls to prevent LEGO parts from falling off the conveyor.

    Walls start OUTSIDE the bucket (not inside) to avoid interfering with
    guide ramps. Walls extend down to belt level with no gap.

    Returns:
        List of wall objects created
    """
    walls = []
    wall_height = 0.18  # 18cm tall walls - from Z=0 to above top belt surface
    wall_thickness = 0.005  # 5mm thick

    # Walls start OUTSIDE the bucket to not interfere with guide ramps
    # Bucket exit is around X=0.05, so start walls at X=0.069
    wall_start_x = 0.069  # Start outside bucket
    wall_end_x = CONVEYOR_END_X
    wall_length = wall_end_x - wall_start_x
    mid_x = (wall_start_x + wall_end_x) / 2

    # Calculate Z position at the wall midpoint
    # Wall needs to extend from ground level up to contain parts on all slat positions
    # Slats move in a loop, so their Z varies. Wall bottom at Z=0 ensures no gaps.
    # Wall bottom at Z=0, extend up to cover belt height + wall_height
    wall_bottom_z = 0.0
    mid_z = wall_bottom_z + wall_height / 2

    # Y offset: at edge of slats plus half wall thickness
    for side, y_offset in [
        ("Left", SLAT_WIDTH / 2 + wall_thickness / 2),
        ("Right", -SLAT_WIDTH / 2 - wall_thickness / 2),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(mid_x, y_offset, mid_z))
        wall = bpy.context.active_object
        if not wall:
            continue

        wall.name = f"Conveyor_Wall_{side}"
        wall.scale = (wall_length, wall_thickness, wall_height)
        bpy.ops.object.transform_apply(scale=True)

        # Set origin to geometry center to avoid double gizmo display
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")

        # No rotation - walls are vertical containment barriers
        # They don't need to follow conveyor incline

        # Setup rigid body
        set_active(wall)
        wall.select_set(True)
        bpy.ops.rigidbody.object_add(type="PASSIVE")
        rb = wall.rigid_body
        if rb:
            rb.collision_shape = "BOX"
            rb.friction = 0.5
            rb.use_margin = True
            rb.collision_margin = 0.001
        wall.select_set(False)

        # Make wall invisible in render (but visible in viewport for physics)
        wall.hide_render = True
        wall.visible_camera = False
        wall.visible_diffuse = False
        wall.visible_glossy = False
        wall.visible_transmission = False
        wall.visible_volume_scatter = False
        wall.visible_shadow = False

        # Add to conveyor collection
        if conveyor_collection:
            for coll in list(wall.users_collection):
                coll.objects.unlink(wall)
            conveyor_collection.objects.link(wall)

        # Ensure wall is in RigidBodyWorld collection for physics
        rbw_coll = bpy.data.collections.get("RigidBodyWorld")
        if rbw_coll and wall.name not in [o.name for o in rbw_coll.objects]:
            rbw_coll.objects.link(wall)

        walls.append(wall)

    print(
        f"✅ Created {len(walls)} side walls for conveyor (starting outside bucket at X={wall_start_x})"
    )
    return walls


def create_bucket_guide_planes(conveyor_collection: Any) -> List[Any]:
    """Create V-shaped ramp guides inside the bucket to funnel parts onto the belt.

    Uses bmesh to create large wedge-shaped ramps that:
    - Outer edge at bucket TOP radius (Y = ±0.12) to cover full bucket interior
    - Inner edge at belt center (Y = ±0.01) to funnel parts precisely
    - Extends from back of bucket to bucket exit
    - Low friction for parts to slide easily onto slats

    Returns:
        List of guide plane objects created
    """
    import bmesh

    guides = []

    # Bucket dimensions - use TOP radius to cover full bucket interior
    bucket_top_radius = 0.12  # 12cm - covers the full bucket opening

    # Inner edge of ramps - very close to center to funnel all parts onto belt
    # Belt is 8cm wide (±0.04), inner edges at ±0.004 create a 0.8cm landing strip
    inner_edge_y = 0.004

    # Ramp X extent - cover the entire bucket interior
    x_start = -0.10  # Back of bucket area
    x_end = 0.09  # Extend further past bucket exit

    # Heights - extend from bucket top to belt surface
    z_top = 0.15  # At bucket top
    z_bottom = CONVEYOR_START_Z  # At belt surface level

    def create_wedge_ramp(name: str, y_outer: float, y_inner: float) -> Any:
        """Create a thick wedge-shaped ramp using bmesh for solid collision."""
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)

        # Thickness of the ramp (perpendicular to the surface)
        thickness = 0.02  # 2cm thick - solid enough to prevent tunneling

        bm = bmesh.new()
        # Create a solid wedge with 8 vertices (box with angled top)
        # Top surface vertices
        v1 = bm.verts.new((x_start, y_outer, z_top))  # Back, outer, top
        v2 = bm.verts.new((x_start, y_inner, z_bottom))  # Back, inner, bottom
        v3 = bm.verts.new((x_end, y_outer, z_top))  # Front, outer, top
        v4 = bm.verts.new((x_end, y_inner, z_bottom))  # Front, inner, bottom

        # Bottom surface vertices (offset down by thickness)
        # For angled surface, offset perpendicular to surface
        # Approximate by moving in -Z and slightly in Y direction
        y_sign = 1 if y_outer > 0 else -1
        v5 = bm.verts.new(
            (x_start, y_outer - y_sign * thickness * 0.3, z_top - thickness)
        )
        v6 = bm.verts.new(
            (x_start, y_inner - y_sign * thickness * 0.3, z_bottom - thickness)
        )
        v7 = bm.verts.new(
            (x_end, y_outer - y_sign * thickness * 0.3, z_top - thickness)
        )
        v8 = bm.verts.new(
            (x_end, y_inner - y_sign * thickness * 0.3, z_bottom - thickness)
        )

        # Create faces for solid box
        bm.faces.new([v1, v3, v4, v2])  # Top surface
        bm.faces.new([v5, v6, v8, v7])  # Bottom surface
        bm.faces.new([v1, v2, v6, v5])  # Back face
        bm.faces.new([v3, v7, v8, v4])  # Front face
        bm.faces.new([v1, v5, v7, v3])  # Outer edge
        bm.faces.new([v2, v4, v8, v6])  # Inner edge

        bm.to_mesh(mesh)
        bm.free()

        # Link to scene - handle case where context.collection might be None
        scene_coll = bpy.context.scene.collection  # type: ignore[union-attr]
        scene_coll.objects.link(obj)

        # Add to conveyor collection
        if conveyor_collection:
            for coll in list(obj.users_collection):
                coll.objects.unlink(obj)
            conveyor_collection.objects.link(obj)

        # Add rigid body
        set_active(obj)
        obj.select_set(True)
        bpy.ops.rigidbody.object_add(type="PASSIVE")
        rb = obj.rigid_body
        if rb:
            rb.collision_shape = "CONVEX_HULL"  # More robust than MESH
            rb.friction = 0.02  # Very low friction for sliding
            rb.use_margin = True
            rb.collision_margin = 0.005  # Larger margin prevents tunneling
        obj.select_set(False)

        # Add to RigidBodyWorld collection
        rbw_coll = bpy.data.collections.get("RigidBodyWorld")
        if rbw_coll and obj.name not in [o.name for o in rbw_coll.objects]:
            rbw_coll.objects.link(obj)

        # Apply material - darker for contrast
        guide_mat = ensure_material(
            "Guide_Material",
            (0.25, 0.25, 0.28, 1.0),
            roughness=0.6,
            metallic=0.1,
        )
        assign_material(obj, guide_mat)

        return obj

    # Create left ramp: outer at bucket top radius, inner near belt center
    left_ramp = create_wedge_ramp(
        "Bucket_Guide_Ramp_Left", bucket_top_radius, inner_edge_y
    )
    guides.append(left_ramp)

    # Create right ramp: outer at bucket top radius, inner near belt center
    right_ramp = create_wedge_ramp(
        "Bucket_Guide_Ramp_Right", -bucket_top_radius, -inner_edge_y
    )
    guides.append(right_ramp)

    # Note: Bucket_Guide_Back was removed - not needed as parts flow naturally

    print(
        f"✅ Created {len(guides)} bucket guide ramps (full bucket funnel to 2cm landing strip)"
    )
    return guides


def create_slat(
    name: str,
    control_points: List[Vector],
    cumulative_normalized: List[float],
    start_offset: float,
    conveyor_collection: Any,
) -> Optional[Any]:
    """Create a single animated slat that follows the conveyor path.

    Args:
        name: Name for the slat object
        control_points: Path corner positions
        cumulative_normalized: Arc-length parameterization
        start_offset: Initial position on path (0-1)
        conveyor_collection: Collection to add slat to

    Returns:
        The created slat object
    """
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    slat = bpy.context.active_object
    if not slat:
        return None

    slat.name = name
    # Scale to slat dimensions: thickness (X), width (Y), height (Z)
    # primitive_cube size=1 creates 1x1x1 cube, scale directly to desired size
    slat.scale = (SLAT_THICKNESS, SLAT_WIDTH, SLAT_HEIGHT)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Rotate slat to match conveyor incline
    slat.rotation_euler.y = CONVEYOR_INCLINE_RAD

    slat_mat = ensure_material(
        "Slat_Material",
        (0.18, 0.18, 0.20, 1.0),  # Dark gray for contrast
        roughness=0.7,
        metallic=0.0,
    )
    assign_material(slat, slat_mat)

    # Add kinematic rigid body for physics interaction
    set_active(slat)
    slat.select_set(True)
    bpy.ops.rigidbody.object_add(type="PASSIVE")
    rb = slat.rigid_body
    if rb:
        rb.collision_shape = "BOX"
        rb.friction = 3.0  # Very high friction to grip LEGO parts
        rb.restitution = 0.0
        rb.kinematic = True
        rb.use_margin = True
        rb.collision_margin = 0.002
    slat.select_set(False)

    # Direct keyframe animation - keyframe for every frame
    for frame in range(1, ANIMATION_FRAMES + 1):
        frame_offset = (start_offset + (frame - 1) / ANIMATION_FRAMES) % 1.0
        pos = sample_path_position(control_points, cumulative_normalized, frame_offset)
        slat.location = pos
        slat.keyframe_insert(data_path="location", frame=frame)

    # Set LINEAR interpolation for mechanical motion
    if slat.animation_data and slat.animation_data.action:
        action = slat.animation_data.action
        # Blender 5.0 API uses layers/strips/channelbags
        if hasattr(action, "layers"):
            for layer in action.layers:
                for strip in layer.strips:
                    for channelbag in strip.channelbags:  # type: ignore[attr-defined]
                        for fcurve in channelbag.fcurves:
                            for kf in fcurve.keyframe_points:
                                kf.interpolation = "LINEAR"
        # Fallback for older Blender versions
        elif hasattr(action, "fcurves"):
            for fcurve in action.fcurves:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = "LINEAR"

    # Add to collection
    if conveyor_collection:
        for coll in list(slat.users_collection):
            coll.objects.unlink(slat)
        conveyor_collection.objects.link(slat)

    # Ensure slat is in RigidBodyWorld collection for physics
    rbw_coll = bpy.data.collections.get("RigidBodyWorld")
    if rbw_coll and slat.name not in [o.name for o in rbw_coll.objects]:
        rbw_coll.objects.link(slat)

    return slat


def main() -> None:
    """Main function to create the conveyor belt system."""
    print("=" * 60)
    print("🏗️  Creating Conveyor Belt with Path-Driven Slats")
    print("=" * 60)

    scene = bpy.context.scene
    if scene:
        scene.frame_set(1)

    # Clear existing conveyor objects
    clear_conveyor_objects()

    # Create collection
    conveyor_collection = ensure_collection("conveyor_belt")

    # Calculate path control points (no visible curve object)
    control_points, cumulative_normalized = create_conveyor_path()

    # Calculate total path length
    total_length = sum(
        (control_points[(i + 1) % len(control_points)] - control_points[i]).length
        for i in range(len(control_points))
    )

    print(f"\n  Creating {SLAT_COUNT} slats...")

    # Create slats evenly distributed around the path
    slats = []
    for i in range(SLAT_COUNT):
        offset = i / SLAT_COUNT
        slat = create_slat(
            f"Slat_{i:02d}",
            control_points,
            cumulative_normalized,
            offset,
            conveyor_collection,
        )
        if slat:
            slats.append(slat)

    # Create side walls to prevent parts from falling off
    walls = create_side_walls(conveyor_collection)

    # Create guide planes inside bucket to funnel parts onto belt
    guides = create_bucket_guide_planes(conveyor_collection)

    # Reset to frame 1
    if scene:
        scene.frame_set(1)

    print("\n" + "=" * 60)
    print("✅ Conveyor belt created successfully!")
    print(f"   Path length: {total_length:.2f}m")
    print(f"   {len(slats)} animated slats (looping)")
    print(f"   {len(walls)} side walls (at slat level)")
    print(f"   {len(guides)} bucket guide planes (funneling)")
    print(f"   Animation: {ANIMATION_FRAMES} frames per cycle")
    print(f"   Belt starts INSIDE bucket for parts to fall onto slats")
    print("=" * 60)


# Execute
main()
