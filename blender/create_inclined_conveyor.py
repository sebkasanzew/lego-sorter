"""
Create gravity-driven inclined conveyor belt.

Instead of friction-based transport with moving slats, uses gravity on an
inclined surface to naturally move parts downward/forward.

Physical principle: Parts slide down incline due to gravity.
No animation required - pure physics simulation.
"""

import bpy
from mathutils import Vector
import math
from typing import Optional, cast, Any


def clear_existing_conveyor() -> None:
    """Remove any existing conveyor belt objects."""
    collections_to_clear = ["conveyor_belt"]

    for col_name in collections_to_clear:
        col = bpy.data.collections.get(col_name)
        if col:
            for obj in list(col.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(col)

    print("✓ Cleared existing conveyor")


def create_inclined_ramp(
    length: float = 1.5,
    width: float = 0.15,
    angle_degrees: float = 20.0,
    start_position: Optional[Vector] = None,
) -> Optional[bpy.types.Object]:
    """
    Create inclined ramp for gravity-driven transport.

    Args:
        length: Ramp length along incline (Blender units)
        width: Ramp width (Blender units)
        angle_degrees: Incline angle from horizontal (degrees)
        start_position: Position of ramp start (top)

    Returns:
        Created ramp object
    """
    if start_position is None:
        start_position = Vector((0.0, 0.0, 0.15))

    # Create mesh
    bpy.ops.mesh.primitive_cube_add()
    ramp = bpy.context.active_object

    if not ramp:
        print("❌ Failed to create ramp object")
        return None

    ramp.name = "Inclined_Conveyor_Ramp"

    # Scale to ramp dimensions
    thickness = 0.005  # Thin ramp
    ramp.scale = (length / 2, width / 2, thickness / 2)
    bpy.ops.object.transform_apply(scale=True)

    # Calculate position and rotation
    angle_rad = math.radians(angle_degrees)

    # Position ramp so top starts at start_position
    # Calculate center position (middle of inclined ramp)
    horizontal_drop = length * math.cos(angle_rad) / 2
    vertical_drop = length * math.sin(angle_rad) / 2

    ramp.location = Vector(
        (
            start_position.x - horizontal_drop,
            start_position.y,
            start_position.z - vertical_drop,
        )
    )

    # Rotate around Y axis (pitch down)
    ramp.rotation_euler = (0, -angle_rad, 0)

    print(f"✓ Created inclined ramp: {angle_degrees}° angle, {length} units long")
    print(
        f"  Top: ({start_position.x:.3f}, {start_position.y:.3f}, {start_position.z:.3f})"
    )

    end_x = start_position.x - length * math.cos(angle_rad)
    end_z = start_position.z - length * math.sin(angle_rad)
    print(f"  Bottom: ({end_x:.3f}, {start_position.y:.3f}, {end_z:.3f})")

    return ramp


def setup_ramp_physics(ramp: bpy.types.Object, friction: float = 0.4) -> None:
    """
    Setup ramp as passive rigid body with controlled friction.

    Lower friction = parts slide faster
    Higher friction = parts slide slower (or not at all if too high)

    Args:
        ramp: Ramp object
        friction: Friction coefficient (0.3-0.5 recommended for sliding)
    """
    scene = bpy.context.scene
    if not scene:
        print("❌ No active scene found")
        return

    # Ensure rigid body world exists
    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()

    # Add to rigid body world collection
    if bpy.context.view_layer:
        bpy.context.view_layer.objects.active = ramp
        bpy.ops.rigidbody.object_add()

    if not ramp.rigid_body:
        print("❌ Failed to add rigid body to ramp")
        return

    # Configure as static passive body
    if ramp.rigid_body:
        ramp.rigid_body.type = "PASSIVE"
        ramp.rigid_body.kinematic = False  # Static, not animated
        ramp.rigid_body.friction = friction
        ramp.rigid_body.collision_margin = 0.001
        ramp.rigid_body.collision_shape = "BOX"

    # Add to rigid body world collection
    rbw = scene.rigidbody_world
    if rbw and rbw.collection:
        if ramp.name not in [obj.name for obj in rbw.collection.objects]:
            rbw.collection.objects.link(ramp)

    print(f"✓ Setup ramp physics: friction={friction}")


def add_side_rails(
    ramp: bpy.types.Object, rail_height: float = 0.02
) -> list[bpy.types.Object]:
    """
    Add side rails to keep parts on ramp.

    Args:
        ramp: Ramp object to add rails to
        rail_height: Height of rails above ramp surface

    Returns:
        List of rail objects
    """
    rails = []
    ramp_length = ramp.dimensions.x
    ramp_width = ramp.dimensions.y

    for side in [-1, 1]:  # Left and right
        bpy.ops.mesh.primitive_cube_add()
        rail = bpy.context.active_object

        if not rail:
            print(f"❌ Failed to create rail for side {side}")
            continue

        rail.name = f"Ramp_Rail_{'Left' if side < 0 else 'Right'}"

        # Scale to thin rail
        rail.scale = (ramp_length / 2, 0.002, rail_height / 2)
        bpy.ops.object.transform_apply(scale=True)

        # Position at ramp edge
        rail.location = ramp.location.copy()
        rail.location.y += side * (ramp_width / 2 + 0.002)
        rail.location.z += rail_height / 2

        # Match ramp rotation
        rail.rotation_euler = ramp.rotation_euler.copy()

        # Setup physics
        if bpy.context.view_layer:
            bpy.context.view_layer.objects.active = rail
            bpy.ops.rigidbody.object_add()

        if rail.rigid_body:
            rail.rigid_body.type = "PASSIVE"
            rail.rigid_body.kinematic = False
            rail.rigid_body.friction = 0.5

        # Add to rigid body world collection
        scene = bpy.context.scene
        if scene:
            rbw = scene.rigidbody_world
            if rbw and rbw.collection:
                if rail.name not in [obj.name for obj in rbw.collection.objects if obj]:
                    rbw.collection.objects.link(rail)

        rails.append(rail)

    print(f"✓ Added side rails (height={rail_height})")
    return rails


def create_collection(ramp: bpy.types.Object, rails: list[bpy.types.Object]) -> None:
    """Organize objects into conveyor_belt collection."""
    scene = bpy.context.scene
    if not scene:
        return

    col = bpy.data.collections.new("conveyor_belt")
    scene.collection.children.link(col)

    for obj in [ramp] + rails:
        # Unlink from scene collection if present
        for scene_col in obj.users_collection:
            scene_col.objects.unlink(obj)
        # Link to conveyor collection
        col.objects.link(obj)

    print("✓ Created conveyor_belt collection")


def add_material(ramp: bpy.types.Object, rails: list[bpy.types.Object]) -> None:
    """Add visual material to ramp and rails."""
    # Ramp material (blue-gray)
    mat_ramp = bpy.data.materials.new(name="Ramp_Material")
    mat_ramp.use_nodes = True

    if mat_ramp.node_tree:
        nodes = mat_ramp.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            # Cast inputs to Any to avoid linter errors with default_value
            inputs = cast(Any, bsdf.inputs)
            inputs["Base Color"].default_value = (0.3, 0.4, 0.6, 1.0)
            inputs["Metallic"].default_value = 0.2
            inputs["Roughness"].default_value = 0.6

    if hasattr(ramp.data, "materials"):
        # Cast data to Mesh to avoid linter errors
        mesh_data = cast(bpy.types.Mesh, ramp.data)
        mesh_data.materials.append(mat_ramp)

    # Rail material (dark gray)
    mat_rail = bpy.data.materials.new(name="Rail_Material")
    mat_rail.use_nodes = True

    if mat_rail.node_tree:
        nodes = mat_rail.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            inputs = cast(Any, bsdf.inputs)
            inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1.0)
            inputs["Metallic"].default_value = 0.8
            inputs["Roughness"].default_value = 0.3

    for rail in rails:
        if hasattr(rail.data, "materials"):
            mesh_data = cast(bpy.types.Mesh, rail.data)
            mesh_data.materials.append(mat_rail)

    print("✓ Added materials")


def main() -> None:
    """Main entry point for creating inclined gravity conveyor."""
    print("\n🏗️ Creating gravity-driven inclined conveyor...\n")

    clear_existing_conveyor()

    # Create inclined ramp
    # 20° angle: steep enough to slide, gentle enough to control
    ramp = create_inclined_ramp(
        length=1.5,
        width=0.15,
        angle_degrees=20.0,
        start_position=Vector((0.0, 0.0, 0.15)),
    )

    if not ramp:
        print("❌ Failed to create ramp")
        return

    # Setup physics with moderate friction for controlled sliding
    setup_ramp_physics(ramp, friction=0.4)

    # Add side rails to keep parts on track
    rails = add_side_rails(ramp, rail_height=0.02)

    # Organize and style
    create_collection(ramp, rails)
    add_material(ramp, rails)

    print("\n✅ Gravity-driven inclined conveyor created!")
    print("📋 Physics principle: Parts slide down due to gravity")
    print("   No animation needed - pure physics simulation")
    print("   Adjust friction (0.3-0.5) to control slide speed")
    print("\n▶️ Place parts at top of ramp and run simulation")


main()
