#!/usr/bin/env python3
"""Visual debugging helpers for LEGO Sorter project.

Provides utilities for adding visual markers, inspecting object state,
and debugging physics simulations in Blender.

Usage:
    # Via MCP
    from utils.blender_mcp_client import BlenderMCPClient
    client = BlenderMCPClient()
    client.execute_code('''
    from utils.blender_debug import add_debug_marker, print_object_state
    add_debug_marker((0, 0, 0), color=(1,0,0,1), name="Origin")
    print_object_state("Conveyor_Belt")
    ''', 'Debug Helpers')

    # Or directly in Blender scripts
    from utils.blender_debug import add_debug_marker
    add_debug_marker(obj.location, color=(0,1,0,1), name=f"Pos_{obj.name}")
"""

try:
    import bpy
    from bpy.types import Material, Mesh, Object as BlenderObject
    from mathutils import Vector
    from typing import Tuple, Optional, Any, cast
except ImportError:
    # Allow importing outside Blender for type checking
    # These type ignores are necessary for the fallback definitions when bpy is not available
    # Type checkers can't understand that these will be replaced at runtime in Blender
    bpy = None  # type: ignore[assignment]
    BlenderObject = None  # type: ignore[assignment,misc]
    Material = None  # type: ignore[assignment,misc]
    Mesh = None  # type: ignore[assignment,misc]
    Vector = None  # type: ignore[assignment,misc]

    def cast(typ, val):  # type: ignore[no-untyped-def]
        """Fallback cast for when typing is not available.

        Type ignore: This is a mock implementation used only when imports fail.
        In normal Blender runtime, typing.cast is used instead.
        """
        return val


def _assign_material_to_mesh_object(obj: Any, mat: Any) -> None:
    """Helper to assign material to mesh object data.

    Note: Blender's object.data is typed as Union[Mesh, Curve, Camera, Light, ...].
    The type stubs cannot express the constraint that when obj.type == 'MESH',
    obj.data is guaranteed to be Mesh. We use type: ignore on materials access
    because runtime validation (obj.type == 'MESH' check) ensures type safety.

    This is a known limitation of fake-bpy-module stubs - see AGENTS.md for context.
    """
    if obj.type == "MESH" and obj.data and hasattr(obj.data, "materials"):
        # Type ignore: obj.type == 'MESH' guarantees obj.data is Mesh at runtime
        # Stubs can't express this constraint, but hasattr provides safety
        obj_materials = obj.data.materials  # type: ignore[union-attr]
        if len(obj_materials) == 0:
            obj_materials.append(mat)
        else:
            obj_materials[0] = mat


def add_debug_marker(
    location: Tuple[float, float, float],
    color: Tuple[float, float, float, float] = (1, 0, 0, 1),
    name: str = "DebugMarker",
    radius: float = 0.05,
) -> Any:
    """Add a small colored sphere at location for visual debugging.

    Args:
        location: (x, y, z) position for marker
        color: (r, g, b, a) color for marker material
        name: Name for the marker object
        radius: Size of marker sphere

    Returns:
        The created marker object

    Example:
        >>> add_debug_marker((0.5, 0, 0.2), color=(0, 1, 0, 1), name="ConveyorStart")
    """
    if bpy is None:
        return None

    # Create sphere
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        location=location,
    )
    marker = bpy.context.active_object
    if marker is None:
        print(f"❌ Failed to create debug marker at {location}")
        return None

    marker.name = name

    # Create or get material
    mat_name = f"DebugMaterial_{name}"
    mat = bpy.data.materials.get(mat_name)

    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        if mat.node_tree is None:
            print(f"❌ Material {mat_name} has no node tree")
            return marker
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        # Emission shader for visibility
        emission = nodes.new(type="ShaderNodeEmission")
        # Blender shader nodes have dynamic socket types not captured in stubs
        color_input = emission.inputs.get("Color")
        strength_input = emission.inputs.get("Strength")
        if color_input and hasattr(color_input, "default_value"):
            # Type ignore: NodeSocketColor has default_value at runtime
            # Base NodeSocket doesn't, but hasattr check ensures safety
            color_input.default_value = color  # type: ignore[union-attr]
        if strength_input and hasattr(strength_input, "default_value"):
            # Type ignore: NodeSocketFloat has default_value at runtime
            strength_input.default_value = 2.0  # type: ignore[union-attr]
        emission.location = (-200, 0)

        output = nodes.new(type="ShaderNodeOutputMaterial")
        output.location = (0, 0)

        emission_output = emission.outputs.get("Emission")
        surface_input = output.inputs.get("Surface")
        if emission_output and surface_input:
            links.new(emission_output, surface_input)

    # Assign material to mesh using helper function
    _assign_material_to_mesh_object(marker, mat)

    print(f"✓ Debug marker '{name}' created at {location}")
    return marker


def add_debug_arrow(
    start: Tuple[float, float, float],
    direction: Tuple[float, float, float],
    length: float = 1.0,
    color: Tuple[float, float, float, float] = (0, 0, 1, 1),
    name: str = "DebugArrow",
) -> Any:
    """Add a visual arrow to show direction/vector.

    Args:
        start: Starting position (x, y, z)
        direction: Direction vector (will be normalized)
        length: Length of arrow
        color: (r, g, b, a) color
        name: Name for arrow object

    Returns:
        The created arrow object
    """
    if bpy is None or Vector is None:
        return None

    # Create cylinder for shaft
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.02,
        depth=length * 0.8,
        location=start,
    )
    arrow = bpy.context.active_object
    if arrow is None:
        return None

    arrow.name = name

    # Orient arrow in direction
    dir_vec = Vector(direction).normalized()
    # Point cylinder along direction (cylinder default is Z-up)
    arrow.rotation_mode = "QUATERNION"
    arrow.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(dir_vec)

    # Move to midpoint
    arrow.location = Vector(start) + dir_vec * length * 0.4

    # Add cone for arrowhead
    bpy.ops.mesh.primitive_cone_add(
        radius1=0.04,
        radius2=0,
        depth=length * 0.2,
        location=Vector(start) + dir_vec * (length * 0.9),
    )
    cone = bpy.context.active_object
    if cone:
        cone.name = f"{name}_Head"
        cone.rotation_quaternion = arrow.rotation_quaternion
        cone.parent = arrow

    print(f"✓ Debug arrow '{name}' created from {start} dir {direction}")
    return arrow


def print_object_state(obj_name: str) -> None:
    """Print comprehensive state of an object for debugging.

    Args:
        obj_name: Name of object to inspect

    Example:
        >>> print_object_state("Conveyor_Belt")
    """
    if bpy is None:
        return

    obj = bpy.data.objects.get(obj_name)
    if not obj:
        print(f"❌ Object '{obj_name}' not found")
        return

    print(f"\n{'=' * 60}")
    print(f"Object State: {obj_name}")
    print(f"{'=' * 60}")
    print(f"Type: {obj.type}")
    print(
        f"Location: ({obj.location.x:.4f}, {obj.location.y:.4f}, {obj.location.z:.4f})"
    )
    print(
        f"Rotation (Euler): ({obj.rotation_euler.x:.4f}, {obj.rotation_euler.y:.4f}, {obj.rotation_euler.z:.4f})"
    )
    print(f"Scale: ({obj.scale.x:.4f}, {obj.scale.y:.4f}, {obj.scale.z:.4f})")

    # Rigid body info
    if obj.rigid_body:
        rb = obj.rigid_body
        print(f"\nRigid Body:")
        print(f"  Type: {rb.type}")
        print(f"  Mass: {rb.mass:.6f} kg")
        print(f"  Friction: {rb.friction:.3f}")
        print(f"  Restitution: {rb.restitution:.3f}")
        print(f"  Collision Shape: {rb.collision_shape}")
        print(f"  Collision Margin: {rb.collision_margin:.4f}")
        print(f"  Kinematic: {rb.kinematic}")
    else:
        print(f"\nRigid Body: None")

    # Material info
    # Type ignore: obj.type == 'MESH' guarantees obj.data is Mesh with materials
    # Blender stubs use Union for obj.data, can't express this type dependency
    if obj.type == "MESH" and obj.data and hasattr(obj.data, "materials"):
        materials = obj.data.materials  # type: ignore[union-attr]
        if len(materials) > 0:
            print(f"\nMaterials:")
            for i, mat in enumerate(materials):
                if mat:
                    print(f"  [{i}] {mat.name}")

    # Collection membership
    collections = [col.name for col in obj.users_collection]
    print(f"\nCollections: {', '.join(collections) if collections else 'None'}")

    # Parent/children
    if obj.parent:
        print(f"\nParent: {obj.parent.name}")
    if obj.children:
        child_names = [child.name for child in obj.children]
        print(f"Children: {', '.join(child_names)}")

    print(f"{'=' * 60}\n")


def print_collection_state(col_name: str) -> None:
    """Print state of all objects in a collection.

    Args:
        col_name: Name of collection to inspect
    """
    if bpy is None:
        return

    col = bpy.data.collections.get(col_name)
    if not col:
        print(f"❌ Collection '{col_name}' not found")
        return

    print(f"\n{'=' * 60}")
    print(f"Collection: {col_name}")
    print(f"{'=' * 60}")
    print(f"Object count: {len(col.objects)}")
    print(f"\nObjects:")
    for i, obj in enumerate(col.objects, 1):
        print(
            f"  [{i:2d}] {obj.name:30s} at ({obj.location.x:6.3f}, {obj.location.y:6.3f}, {obj.location.z:6.3f})"
        )
    print(f"{'=' * 60}\n")


def print_physics_state(frame: Optional[int] = None) -> None:
    """Print physics simulation state at specified frame.

    Args:
        frame: Frame number to inspect (None = current frame)
    """
    if bpy is None:
        return

    scene = bpy.context.scene
    # Type ignore: bpy.context.scene can be None in stubs but is guaranteed
    # in normal Blender runtime; assertion provides type narrowing
    assert scene is not None, "Scene must exist in Blender context"  # noqa: S101

    if frame is not None:
        scene.frame_set(frame)
        current_frame = frame
    else:
        current_frame = scene.frame_current

    print(f"\n{'=' * 60}")
    print(f"Physics State at Frame {current_frame}")
    print(f"{'=' * 60}")

    # Rigidbody world info
    if scene.rigidbody_world:
        rbw = scene.rigidbody_world
        print(f"Rigidbody World:")
        print(f"  Substeps: {rbw.substeps_per_frame}")
        print(f"  Solver Iterations: {rbw.solver_iterations}")
        print(f"  Time Scale: {rbw.time_scale:.2f}")
    else:
        print(f"Rigidbody World: None")

    # Count rigidbodies by type
    active_count = 0
    passive_count = 0

    for obj in bpy.data.objects:
        if obj.rigid_body:
            if obj.rigid_body.type == "ACTIVE":
                active_count += 1
            elif obj.rigid_body.type == "PASSIVE":
                passive_count += 1

    print(f"\nRigid Bodies:")
    print(f"  Active: {active_count}")
    print(f"  Passive: {passive_count}")
    print(f"  Total: {active_count + passive_count}")

    print(f"{'=' * 60}\n")


def visualize_bounding_boxes(collection_name: Optional[str] = None) -> None:
    """Add wireframe cubes showing bounding boxes of objects.

    Args:
        collection_name: If specified, only visualize objects in this collection
    """
    if bpy is None:
        return

    if collection_name:
        col = bpy.data.collections.get(collection_name)
        if not col:
            print(f"❌ Collection '{collection_name}' not found")
            return
        objects = col.objects
    else:
        objects = bpy.data.objects

    for obj in objects:
        if obj.type != "MESH":
            continue

        if Vector is None:
            print(f"❌ mathutils.Vector not available")
            return

        # Get bounding box
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

        # Calculate bbox center and dimensions
        # Type ignore: Vector constructor accepts tuple, but stubs expect Sequence[float]
        # This is safe - tuple is a sequence, just more specific
        min_corner = Vector(  # type: ignore[arg-type]
            (
                min(c.x for c in bbox_corners),
                min(c.y for c in bbox_corners),
                min(c.z for c in bbox_corners),
            )
        )
        max_corner = Vector(  # type: ignore[arg-type]
            (
                max(c.x for c in bbox_corners),
                max(c.y for c in bbox_corners),
                max(c.z for c in bbox_corners),
            )
        )

        center = (min_corner + max_corner) / 2
        dimensions = max_corner - min_corner

        # Create wireframe cube
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=center,
        )
        bbox_obj = bpy.context.active_object
        if bbox_obj:
            bbox_obj.name = f"BBox_{obj.name}"
            bbox_obj.scale = dimensions / 2
            bbox_obj.display_type = "WIRE"

    print(f"✓ Bounding boxes visualized for {len(objects)} objects")


def measure_distance(obj1_name: str, obj2_name: str) -> Optional[float]:
    """Measure distance between two objects.

    Args:
        obj1_name: Name of first object
        obj2_name: Name of second object

    Returns:
        Distance in Blender units, or None if objects not found
    """
    if bpy is None or Vector is None:
        return None

    obj1 = bpy.data.objects.get(obj1_name)
    obj2 = bpy.data.objects.get(obj2_name)

    if not obj1:
        print(f"❌ Object '{obj1_name}' not found")
        return None
    if not obj2:
        print(f"❌ Object '{obj2_name}' not found")
        return None

    # Type ignore: Vector constructor accepts tuple but stubs expect Sequence[float]
    # Tuple is a valid sequence type, this is overly strict typing in stubs
    loc1 = obj1.location
    loc2 = obj2.location
    dist = (Vector((loc1.x, loc1.y, loc1.z)) - Vector((loc2.x, loc2.y, loc2.z))).length  # type: ignore[arg-type]
    print(f"Distance between '{obj1_name}' and '{obj2_name}': {dist:.4f} units")
    return dist


def clear_debug_markers() -> None:
    """Remove all debug markers from the scene."""
    if bpy is None:
        return

    removed = 0
    for obj in list(bpy.data.objects):
        if obj.name.startswith("DebugMarker") or obj.name.startswith("DebugArrow"):
            bpy.data.objects.remove(obj, do_unlink=True)
            removed += 1

    print(f"✓ Removed {removed} debug markers")


# Main function for testing
def main():
    """Test debug utilities."""
    if bpy is None:
        print("⚠️  Must run in Blender context")
        return

    print("\n🔍 Testing Debug Utilities\n")

    # Add some markers
    add_debug_marker((0, 0, 0), color=(1, 0, 0, 1), name="Origin")
    add_debug_marker((1, 0, 0), color=(0, 1, 0, 1), name="X_Axis")
    add_debug_marker((0, 1, 0), color=(0, 0, 1, 1), name="Y_Axis")
    add_debug_marker((0, 0, 1), color=(1, 1, 0, 1), name="Z_Axis")

    # Add arrow
    add_debug_arrow((0, 0, 0), (1, 1, 1), length=0.5, name="DiagonalDir")

    # Print state of some objects if they exist
    for obj_name in ["Conveyor_Belt", "Sorting_Bucket_Base", "SorterCam"]:
        if bpy.data.objects.get(obj_name):
            print_object_state(obj_name)

    # Print collection states
    for col_name in ["bucket", "conveyor_belt", "lego_parts"]:
        if bpy.data.collections.get(col_name):
            print_collection_state(col_name)

    # Print physics state
    print_physics_state()

    print("\n✅ Debug utilities test complete\n")


if __name__ == "__main__":
    if bpy is not None:
        main()
